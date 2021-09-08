import logging
import re

import praw

import config
from bot_controller import BotController
from database import DatabaseController

subreddit = config.read_config('Reddit Config', 'subreddit')
minimum_price = int(config.read_config('Reddit Config', 'minimum_price'))

_logger = logging.getLogger(__name__)


# TODO: type hints everywhere
class RedditController:
    def __init__(self):

        self.databaseController = DatabaseController()
        self.botController = BotController()
        self.reddit = praw.Reddit(
            client_id=config.read_config('Reddit Config', 'client_id'),
            client_secret=config.read_config('Reddit Config', 'client_secret'),
            user_agent=config.read_config('Reddit Config', 'user_agent')
        )

    def evaluatePosts(self):
        post_count = int(config.read_config('Reddit Config', 'post_count'))
        if not post_count:
            post_count = 10

        new_submissions = self.reddit.subreddit(subreddit).new(limit=post_count)
        list_submissions = list(new_submissions)
        _logger.info("Found %s new submissions.", len(list_submissions))

        count = 0

        # iterate over new submissions from oldest to newest
        for submission in reversed(list_submissions):

            # if the submission is Active and we haven't already considered it, then do something
            if submission.link_flair_text == 'Active' or not self.databaseController.does_submission_exists(
                    submission.id):

                numbers = re.findall(r'\d+', submission.title)
                if numbers:
                    # use list comprehension to easily get biggest number
                    biggest_number = max([int(num) for num in numbers])
                else:
                    _logger.warning("(%s) - Couldn't find price in title '%s'!", submission.id, submission.title)
                    continue

                if biggest_number >= minimum_price:
                    # try adding to database
                    if self.databaseController.add_submission(submission):
                        _logger.info("(%s) - Submission added, sending message", submission.id)
                        self.botController.sendText(submission.title, biggest_number, submission.created_utc,
                                                    submission.shortlink)
                        count += 1
                    else:
                        _logger.error("(%s) - Error while adding submission to database", submission.id)
                else:
                    _logger.info("(%s) - Price '%d' is lower than minimum price %d.", submission.id, biggest_number,
                                 minimum_price)
            else:
                # else ignore submission
                pass

        _logger.info("Found %d submissions matching filter.", count)

import logging
import re

import praw

import config
from bot_controller import BotController
from database import DatabaseController

subreddit = config.read_config('Reddit Config', 'subreddit')
minimum_price = config.read_config('Reddit Config', 'minimum_price')


class RedditController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.databaseController = DatabaseController()
        self.botController = BotController()
        self.reddit = praw.Reddit(
            client_id=config.read_config('Reddit Config', 'client_id'),
            client_secret=config.read_config('Reddit Config', 'client_secret'),
            user_agent=config.read_config('Reddit Config', 'user_agent')
        )

    def evaluatePosts(self):
        postcount = int(config.read_config('Reddit Config', 'post_count'))
        if not postcount:
            postcount = 10

        new_submissions = self.reddit.subreddit(subreddit).new(limit=postcount)
        list_submissions = list(new_submissions)
        # self.logger.debug("Found %s new submissions.", len(list_submissions))

        count = 0

        # iterate over new submissions from oldest to newest
        for submission in reversed(list_submissions):

            # if the submission is Active and we haven't already considered it, then do something
            if submission.link_flair_text == 'Active' and not self.databaseController.does_submission_exists(
                    submission.id):

                numbers = re.findall(r'\d+', submission.title)
                if numbers:
                    # use list comprehension to easily get biggest number
                    biggest_number = max([int(num) for num in numbers])
                else:
                    self.logger.info("({id}) - Couldn't find price in title '{title}'!".format(id=submission.id,
                                                                                               title=submission.title))
                    continue

                if biggest_number > int(minimum_price):
                    # try adding to database
                    if self.databaseController.add_submission(submission):
                        self.logger.info("({id}) - Submission added, sending message".format(id=submission.id))
                        self.botController.sendText(submission.title, biggest_number, submission.created_utc,
                                                    submission.shortlink)
                        count += 1
                    else:
                        self.logger.info("({id}) - Error while adding submission to database".format(id=submission.id))
                else:
                    self.logger.info("({id}) - Price '{price}' is lower than minimum value".format(price=biggest_number,
                                                                                                   id=submission.id))
            else:
                # else ignore submission
                pass

        self.logger.info("Found %d submissions matching filter.", count)

import logging
import re

import praw

import config
import telegram_bot
from database import DatabaseController

subreddit = config.read_config('Reddit Config', 'subreddit')
minimum_price = int(config.read_config('Reddit Config', 'minimum_price'))

_logger = logging.getLogger(__name__)


class RedditController:
    def __init__(self):
        self.databaseController = DatabaseController()
        self.reddit = praw.Reddit(
            client_id=config.read_config('Reddit Config', 'client_id'),
            client_secret=config.read_config('Reddit Config', 'client_secret'),
            user_agent=config.read_config('Reddit Config', 'user_agent')
        )
        self.post_limit = int(config.read_config('Reddit Config', 'post_limit'))
        if self.post_limit < 1:
            raise Exception(f"Post count ({self.post_limit}) must be >= 1.")

    def evaluatePosts(self) -> None:
        new_submissions = self.reddit.subreddit(subreddit).new(limit=self.post_limit)
        list_submissions = list(new_submissions)
        _logger.info("Found %d submissions.", len(list_submissions))

        # iterate over new submissions from oldest to newest
        num_submissions_matching_filter = 0
        submission: praw.reddit.models.Submission
        for submission in reversed(list_submissions):
            if submission.link_flair_text != 'Active':
                _logger.debug("(%s) - Submission not Active. Skipping...", submission.id)
                continue
            if self.databaseController.does_submission_exists(submission.id):
                _logger.debug("(%s) - Submission already considered. Skipping...", submission.id)
                continue

            numbers = re.findall(r'\d+', submission.title)
            if numbers:
                # use list comprehension to easily get biggest number
                biggest_number = max([int(num) for num in numbers])
            else:
                _logger.warning("(%s) - Failed to find price in title: %s", submission.id, submission.title)
                continue

            if biggest_number >= minimum_price:
                # try adding to database
                if self.databaseController.add_submission(submission):
                    _logger.info("(%s) - Submission added, sending message...", submission.id)
                    telegram_bot.sendText(submission.id, submission.title, biggest_number, submission.created_utc,
                                          submission.shortlink)
                    num_submissions_matching_filter += 1
                else:
                    _logger.error("(%s) - Failed to add submission to database.", submission.id)
            else:
                _logger.info("(%s) - Price (%d) is lower than minimum price (%d)..", submission.id, biggest_number,
                             minimum_price)

        _logger.info("Found %d/%d submissions matching filter.", num_submissions_matching_filter, len(list_submissions))

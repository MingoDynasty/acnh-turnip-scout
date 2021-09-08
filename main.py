import logging.config
import os
import schedule
import sys
import time

import yaml

import config
from database import DatabaseController
from reddit_controller import RedditController

if __name__ == '__main__':
    logConfFile = os.path.join(os.path.dirname(__file__), 'logging.yaml')
    if not os.path.isfile(logConfFile):
        print(logConfFile + " not found.")
        sys.exit()

    # create a directory for log files to go into
    if not os.path.isdir("logs"):
        os.makedirs("logs")

    with open(logConfFile, 'r') as fh:
        logging_config = yaml.safe_load(fh.read())
        logging.config.dictConfig(logging_config)

    logger = logging.getLogger(__name__)

    databaseController = DatabaseController()
    databaseController.move_db()
    databaseController.setup_db()

    redditController = RedditController()

    str_poll_interval = config.read_config('Application Config', 'poll_interval')
    try:
        poll_interval = int(str_poll_interval)
    except ValueError:
        logger.error("poll_interval (%s) must be a number.", str_poll_interval)
        sys.exit(1)
    logger.info("Using poll interval (seconds): %d", poll_interval)

    def main_loop():
        logger.info("Polling Reddit...")
        redditController.evaluatePosts()
        logger.info("Poll finished.")

    try:
        schedule.every(poll_interval).seconds.do(main_loop)
        main_loop()
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping the bot...")

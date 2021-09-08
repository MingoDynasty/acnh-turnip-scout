import logging.config
import os
import sched
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

    LOG_FORMAT = "%(asctime)-15s - %(levelname)s - %(message)s"
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=LOG_FORMAT)

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
    logger.info("Using poll interval: %d", poll_interval)

    logger.info("---- Polling Reddit ----")
    redditController.evaluatePosts()
    logger.info("---- Poll finished ----")

    # main loop
    scheduler = sched.scheduler(time.time, time.sleep)


    def main_loop(sc):
        logger.info("---- Polling Reddit ----")
        redditController.evaluatePosts()
        logger.info("---- Poll finished ----")
        scheduler.enter(poll_interval, 1, main_loop, (sc,))


    try:
        scheduler.enter(poll_interval, 1, main_loop, (scheduler,))
        scheduler.run()
    except KeyboardInterrupt:
        logger.info("---- Stopping the bot ----")

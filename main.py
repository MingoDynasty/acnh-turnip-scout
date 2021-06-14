import logging.config
import os
import sched
import sys
import config
import time

from database import DatabaseController
from reddit_controller import RedditController

if __name__ == '__main__':
    logConfFile = os.path.join(os.path.dirname(__file__), 'logging.conf')
    if not os.path.isfile(logConfFile):
        print(logConfFile + " not found.")
        exit()

    log_format = "%(asctime)-15s - %(levelname)s - %(message)s"
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=log_format)
    logging.config.fileConfig(logConfFile)
    logger = logging.getLogger(__name__)

    databaseController = DatabaseController()
    databaseController.setup_db()

    redditController = RedditController()

    str_poll_interval = config.read_config('Application Config', 'poll_interval')
    try:
        poll_interval = int(str_poll_interval)
    except ValueError as e:
        logger.error("poll_interval (%s) must be a number.", str_poll_interval)
        exit(1)
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

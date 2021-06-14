import logging.config
import os
import sched
import sys
import time

from database import DatabaseController
from reddit_controller import RedditController

ping_interval = 180  # TODO: move to config file; rename to poll

if __name__ == '__main__':
    logConfFile = os.path.join(os.path.dirname(__file__), 'logging.conf')
    if not os.path.isfile(logConfFile):
        print(logConfFile + " not found.")
        exit()

    log_format = "%(asctime)-15s - %(levelname)s - %(message)s"
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=log_format)
    logging.config.fileConfig(logConfFile)
    logger = logging.getLogger(__name__)

    logger.info("mingtest start")

    # telegram.setup()

    databaseController = DatabaseController()
    databaseController.setup_db()

    redditController = RedditController()

    logger.info("---- Polling Reddit ----")
    redditController.evaluatePosts()
    logger.info("---- Poll finished ----")

    # main loop
    scheduler = sched.scheduler(time.time, time.sleep)


    def main_loop(sc):
        logger.info("---- Polling Reddit ----")
        redditController.evaluatePosts()
        logger.info("---- Poll finished ----")
        scheduler.enter(ping_interval, 1, main_loop, (sc,))


    try:
        scheduler.enter(ping_interval, 1, main_loop, (scheduler,))
        scheduler.run()
    except KeyboardInterrupt:
        logger.info("---- Stopping the bot ----")

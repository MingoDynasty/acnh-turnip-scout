import sched
import time

import database as db
import redditconfig as reddit

ping_interval = 180

if __name__ == '__main__':
    # telegram.setup()
    db.setup_db()

    print("---- Polling Reddit ----")
    reddit.evaluatePosts()

    # main loop
    scheduler = sched.scheduler(time.time, time.sleep)


    def main_loop(sc):
        print("\n---- Polling Reddit ----")
        reddit.evaluatePosts()
        scheduler.enter(ping_interval, 1, main_loop, (sc,))


    try:
        scheduler.enter(ping_interval, 1, main_loop, (scheduler,))
        scheduler.run()
    except KeyboardInterrupt:
        print("---- Stopping the bot ----")

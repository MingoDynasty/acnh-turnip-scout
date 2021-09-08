import datetime
import logging
import os
import sqlite3

import config
from praw import models

_logger = logging.getLogger(__name__)

DB_PATH = config.read_config('Application Config', 'db_path')


# TODO: simply reuse connection, also so it's not possible to move the database file during script execution
class DatabaseController:

    # TODO: for debugging only. Remove later.
    def move_db(self):
        _logger.info('Moving database...')
        if not os.path.exists(DB_PATH):
            _logger.info("DB (%s) does not exist. Nothing to move.", DB_PATH)
            return
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%I%M%S")
        os.rename(DB_PATH, f"{DB_PATH}.{timestamp}")

    def setup_db(self) -> None:
        _logger.info('Setting up database...')
        db = sqlite3.connect(DB_PATH)
        # Get a cursor object
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE if not exists submissions(id TEXT PRIMARY KEY, title TEXT, created TEXT, shortlink TEXT)
        ''')
        db.commit()

    def get_submissions(self) -> list:
        _logger.info('Fetching all submissions...')
        db = sqlite3.connect(DB_PATH)
        cursor = db.cursor()
        cursor.execute('''SELECT * FROM submissions''')
        return cursor.fetchall()

    def does_submission_exists(self, _id: int) -> bool:
        db = sqlite3.connect(DB_PATH)
        cursor = db.cursor()
        cursor.execute('''SELECT * FROM submissions WHERE id = ?''', (_id,))
        all_rows = cursor.fetchall()
        return len(all_rows) > 0

    def add_submission(self, sub: models.Submission) -> bool:
        if not self.does_submission_exists(sub.id):
            _logger.info("(%s) - Adding submission to database...", sub.id)
            db = sqlite3.connect(DB_PATH)
            cursor = db.cursor()
            cursor.execute('''INSERT INTO submissions(id,title,created,shortlink) VALUES(?,?,?,?)''',
                           (sub.id, sub.title, sub.created_utc, sub.shortlink))
            db.commit()
            return True
        _logger.info("(%s) - Submission already exists in database.", sub.id)
        return False

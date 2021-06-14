import logging
import sqlite3

DB_PATH = 'data/turnip_submissions.db'


class DatabaseController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def setup_db(self):
        self.logger.info('[DB] Setting up database')
        db = sqlite3.connect(DB_PATH)
        # Get a cursor object
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE if not exists submissions(id TEXT PRIMARY KEY, title TEXT, created TEXT, shortlink TEXT)
        ''')
        db.commit()

    def get_submissions(self):
        self.logger.info('[DB] Fetching all submissions')
        db = sqlite3.connect(DB_PATH)
        cursor = db.cursor()
        cursor.execute('''SELECT * FROM submissions''')
        return cursor.fetchall()

    def does_submission_exists(self, id):
        db = sqlite3.connect(DB_PATH)
        cursor = db.cursor()
        cursor.execute('''SELECT * FROM submissions WHERE id = ?''', (id,))
        all_rows = cursor.fetchall()
        return True if len(all_rows) > 0 else False

    def add_submission(self, sub):
        if not self.does_submission_exists(sub.id):
            self.logger.info("[DB]({id}) - Adding to db".format(id=sub.id))
            db = sqlite3.connect(DB_PATH)
            cursor = db.cursor()
            cursor.execute('''INSERT INTO submissions(id,title,created,shortlink) VALUES(?,?,?,?)''',
                           (sub.id, sub.title, sub.created_utc, sub.shortlink))
            db.commit()
            return True
        else:
            self.logger.info("[DB]({id}) - Submission already exists in db".format(id=sub.id))
            return False

import base64
import re

import praw

import config
import logging

from bot_controller import BotController
from database import DatabaseController


reddit = praw.Reddit(
    client_id=config.read_config('REDDITCONFIG', 'client_id'),
    client_secret=config.read_config('REDDITCONFIG', 'client_secret'),
    user_agent=config.read_config('REDDITCONFIG', 'user_agent')
)
encodingType = 'utf-8'
subreddit = config.read_config('REDDITCONFIG', 'subreddit')
minimum_price = config.read_config('REDDITCONFIG', 'minimum_price')
savedPosts = []


def base64String(value, shouldDecode):
    if shouldDecode == 'true':
        return value.decode(encodingType)
    else:
        message_bytes = value.encode(encodingType)
        return base64.b64encode(message_bytes)


def encodeString(str):
    message_bytes = str.encode(encodingType)
    base64_bytes = base64.b64encode(message_bytes)
    return base64_bytes


def decodeString(base64EncryptedString):
    base64_message = base64EncryptedString.decode(encodingType)
    decoded_string = base64.b64decode(base64_message)
    return decoded_string


# Used as a last resort to find the price from the image if it cannot be found in the submission title
# temporarily disabled
# def extract_text(url):
#    # Uses tesseract from following lib. Needs to be installed locally -> https://github.com/UB-Mannheim/tesseract/wiki
#    path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
#    image_path = url
#    img_data = requests.get(url).content
#    filename = url.split('/')[-1]
#    if filename:
#        with open(filename, 'wb') as handler:
#            handler.write(img_data)
#
#        img = Image.open(filename)
#        pytesseract.tesseract_cmd = path_to_tesseract
#
#        text = pytesseract.image_to_string(img)
#        return text[:-1]


class RedditController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.databaseController = DatabaseController()
        self.botController = BotController()

    def evaluatePosts(self):
        postcount = int(config.read_config('REDDITCONFIG', 'post_count'))
        if not postcount:
            postcount = 10

        new_submissions = reddit.subreddit(subreddit).new(limit=postcount)
        list_submissions = list(new_submissions)
        # self.logger.debug("Found %s new submissions.", len(list_submissions))

        count = 0

        # iterate over new submissions from oldest to newest
        for submission in reversed(list_submissions):

            # if the submission is Active and we haven't already considered it, then do something
            if submission.link_flair_text != 'Active' and not self.databaseController.does_submission_exists(submission.id):

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
                        self.botController.sendText(submission.title, biggest_number, submission.created_utc, submission.shortlink)
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

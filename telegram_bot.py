import logging
from datetime import datetime

from requests import get

import config

_logger = logging.getLogger(__name__)


# TODO: use Telegram Python library instead
def sendText(submission_id: int, title, price, created, shortlink) -> bool:
    # Globally store values from config instead of adding per request
    token = config.read_config('Telegram Config', 'token')
    chatID = config.read_config('Telegram Config', 'chatID')

    created = datetime.fromtimestamp(created).astimezone().replace(microsecond=0).strftime(
        "%Y-%m-%d %I:%M:%S %p %Z")
    multi_line_msg = """I found a nice offer! I think the price is {price}.
Posted on: {created}
Here's the link if you want to check it out: {shortlink}""".format(price=price, created=created,
                                                                   shortlink=shortlink)

    # urlencode msg for safety
    send_text = 'https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chatID + '&parse_mode=Markdown&text=' + multi_line_msg

    response = get(send_text)

    if response.status_code == 200:
        _logger.info("(%s) - Successfully sent message.", submission_id)
        return True
    _logger.error("(%s) - Failed to send message.", submission_id)
    return False

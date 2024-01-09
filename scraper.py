import logging
import logging.config
import os

from dotenv import load_dotenv
from pydantic import AnyHttpUrl
from pythonjsonlogger import jsonlogger

from handlers.monday import MondayHandler
from handlers.moodle import MoodleHandler


def get_config():
    load_dotenv()
    return os.environ


def get_logger() -> logging.Logger:
    _logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(json_indent=4)
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    _logger.setLevel(logging.INFO)
    return _logger


if __name__ == "__main__":
    config = get_config()
    username = config["MOODLE_USERNAME"]
    password = config["MOODLE_PASSWORD"]
    base_url = config["MOODLE_BASEURL"]
    monday_token = config["MONDAY_API_KEY"]
    board_id = config["MONDAY_BOARD_ID"]
    logger = get_logger()

    monday = MondayHandler(token=monday_token, logger=logger)
    boards = monday.get_boards()
    items = boards.fetch_items_by_board_id(board_id)

    mh = MoodleHandler(
        username=username,
        password=password,
        baseurl=AnyHttpUrl(base_url, scheme="https"),
        logger=logger,
    )

    assigns = mh.get_assigns()

    for assign in assigns:
        item_id = monday.add_item(
            board_id=board_id,
            item=assign,
            moodle=mh,
        )

        logger.info(
            msg="fetched assign",
            extra={
                "title": assign.title,
                "description": assign.description,
                "dates": {
                    "start": assign.dates.start,
                    "due": assign.dates.due,
                },
                "url": assign.url,
                "attachments": {attachment.name: attachment.url for attachment in assign.attachments},
            },
        )

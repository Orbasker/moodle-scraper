import logging
import logging.config
import os

from dotenv import load_dotenv
from pydantic.v1 import AnyHttpUrl
from pythonjsonlogger import jsonlogger

from handlers.monday import MondayBoardHandler
from handlers.moodle import MoodleHandler
from models.column_names import ColumnNames, Dates


def get_config() -> dict:
    load_dotenv()
    return os.environ.copy()


def get_column_names(conf: dict) -> ColumnNames:
    return ColumnNames(
        description=conf["MONDAY_COLUMN_NAME_DESCRIPTION"],
        dates=Dates(
            start=conf["MONDAY_COLUMN_NAME_START_DATE"],
            due=conf["MONDAY_COLUMN_NAME_DUE_DATE"],
        ),
        url=conf["MONDAY_COLUMN_NAME_URL"],
        attachments=conf["MONDAY_COLUMN_NAME_ATTACHMENTS"],
        course_name=conf["MONDAY_COLUMN_NAME_COURSE_NAME"],
    )


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

    mbh = MondayBoardHandler(
        token=monday_token,
        logger=logger,
        board_id=int(board_id),
    )

    items = mbh.fetch_items()

    mh = MoodleHandler(
        username=username,
        password=password,
        baseurl=AnyHttpUrl(base_url, scheme="https"),
        logger=logger,
    )

    assigns = mh.get_assigns()

    for assign in assigns:
        item_id = mbh.add_item(
            assign=assign,
            column_names=get_column_names(conf=config),
            # group_id="new_group29179"
        )

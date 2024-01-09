import os

from monday import MondayClient
from logging import Logger
from handlers.moodle import MoodleHandler


class MondayBoardHandler:
    def __init__(self, token: str, board_id: int, logger: Logger):
        self.client = MondayClient(token)
        self.board_id = board_id
        self.logger = logger
        self.items = {}

    def fetch_items(self, check_cache: bool = True) -> dict:
        if check_cache and self.items:
            return self.items
        self.items = self.client.boards.fetch_items_by_board_id(self.board_id)
        return self.items

    def add_item(self, board_id: int, item, moodle: MoodleHandler):
        item_name = item.title
        given_date = item.dates.start.strftime("%Y-%m-%d")
        due_date = item.dates.due.strftime("%Y-%m-%d")
        column_values = {
            "text": item.description,
            "date20": {"date": due_date},
            "date": {"date": given_date},
            "link": {"text": item.title, "url": item.url},
        }
        item_id = self.client.items.create_item(
            board_id=board_id, group_id="topics", item_name=item_name, column_values=column_values
        )
        item_id = item_id.get("data")["create_item"]["id"]
        self.logger.info(msg="Added item", extra={"item_id": item_id, "item": item})
        result = ""
        if len(item.attachments) <= 0:
            result = "No attachments"
            self.logger.info(msg="No attachments")
        else:
            for attachment in item.attachments:
                response = moodle.session.get(attachment.url)
                if response.status_code == 200:
                    filename = attachment.name
                    with open(filename, "wb") as f:
                        f.write(response.content)
                    result = self.client.items.add_file_to_column(item_id=item_id, column_id="files3", file=filename)
                    if result.get("data") is not None:
                        self.logger.info(msg="Added file", extra={"item_id": item_id, "file": filename})
                    else:
                        self.logger.error(msg="Error while adding file", extra={"item_id": item_id, "file": filename})
                    os.remove(filename)
                else:
                    result = "Error while downloading file"
                    self.logger.error(msg="Error while downloading file", extra={"status_code": response.status_code})
        return {"item_id": item_id, "res": result}

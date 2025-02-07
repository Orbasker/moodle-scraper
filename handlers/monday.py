import json
import os
from logging import Logger

from monday import MondayClient

from models.assign import Assign, Attachment
from models.column_names import ColumnNames


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

    def _add_attachments(self, item_id: str, attachments: list[Attachment]):
        for attachment in attachments:
            with open(attachment.name, "wb") as f:
                f.write(attachment.data)
            self.client.items.add_file_to_column(
                item_id=item_id,
                column_id="files3",
                file=attachment.name,
            )
            os.remove(attachment.name)

    def _should_add_item(self, assign: Assign, column_names: ColumnNames) -> bool:
        for board in self.items["data"]["boards"]:
            for group in board['items_page']['items']:
                for item in group["column_values"]:
                    if item["id"] == column_names.url:
                        url_column = json.loads(item["value"])
                        if url_column["text"] == assign.title:
                            self.logger.info("item already exists in board", extra={"title": assign.title})
                            return False

        self.logger.info("item does not exist in board", extra={"title": assign.title})
        return True

    def add_item(
        self,
        assign: Assign,
        column_names: ColumnNames,
        group_id: str = "topics",
    ):
        if not self._should_add_item(
            assign=assign,
            column_names=column_names,
        ):
            return

        column_values = {
            column_names.description: assign.description,
            column_names.dates.start: {
                "date": assign.dates.start.strftime("%Y-%m-%d"),
            },
            column_names.dates.due: {
                "date": assign.dates.due.strftime("%Y-%m-%d"),
            },
            column_names.url: {"text": assign.title, "url": assign.url},
            column_names.course_name: assign.course_name,
        }

        item = self.client.items.create_item(
            board_id=self.board_id,
            group_id=group_id,
            item_name=assign.title,
            create_labels_if_missing=True,
            column_values=column_values,
        )

        item_id = item["data"]["create_item"]["id"]

        self._add_attachments(
            item_id,
            assign.attachments,
        )

        return item_id

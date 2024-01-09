from monday import MondayClient
import requests
import os
from handlers.moodle import MoodleHandler
class MondayHandler:
    def __init__(self, token):
        self.client = MondayClient(token)

    def get_boards(self):
        return self.client.boards

    def get_board(self, board_id):
        return self.client.boards.get_board(board_id)

    def add_item(self, board_id, item,moodle: MoodleHandler):
        item_name = item.title
        given_date = item.dates.start.strftime("%Y-%m-%d")
        due_date = item.dates.due.strftime("%Y-%m-%d")
        column_values = {
            "text": item.description,
            "date20": {"date": due_date},
            "date": {"date": given_date},
            "link": {"text": item.title,
                     "url": item.url},
        }
        item_id = self.client.items.create_item(board_id=board_id, group_id="topics", item_name=item_name,
                                             column_values=column_values)
        item_id = item_id.get('data')['create_item']['id']
        if len(item.attachments):
            response = moodle.session.get(item.attachments[0].url)
            if response.status_code == 200:
                filename = item.attachments[0].name
                with open(filename, 'wb') as f:
                    f.write(response.content)
                result = self.client.items.add_file_to_column(item_id=item_id, column_id="files3", file=filename)
                os.remove(filename)
            else:
                result = "Error while downloading file"
        else:
            result = "No attachments"
        return {"item_id": item_id, "res": result}
from logging import Logger
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pydantic import AnyHttpUrl

from models.assign import Assign, Attachment
from parsers.assign import AssignParser


class MoodleHandler:
    session = None

    def _login(self):
        self.session = requests.Session()
        login_url = urljoin(self.baseurl, "login/index.php")
        login_data = {"username": self.username, "password": self.password}
        self.session.post(login_url, data=login_data)

    def __init__(
        self,
        username: str,
        password: str,
        baseurl: AnyHttpUrl,
        logger: Logger,
    ):
        self.username = username
        self.password = password
        self.baseurl = baseurl
        self.logger = logger
        self._login()

    def _fetch_page(self, url: AnyHttpUrl) -> BeautifulSoup:
        response = self.session.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def _get_calendar_page(self) -> BeautifulSoup:
        return self._fetch_page(urljoin(self.baseurl, "calendar/view.php"))

    def _get_assign_page(self, assign_page_url: AnyHttpUrl) -> BeautifulSoup:
        return self._fetch_page(assign_page_url)

    def _get_attachments(self, assign_page: BeautifulSoup) -> list[Attachment]:
        attachments = []
        if attachments_section := assign_page.find(
            name="div",
            class_="fileuploadsubmission",
        ):
            for attachment in attachments_section.find_all("a", {"target": "_blank"}):
                url = attachment["href"]
                attachments.append(
                    Attachment(
                        url=url,
                        name=attachment.text.strip(),
                        data=self.session.get(url).content,
                    )
                )

        return attachments

    def get_assigns(self) -> list[Assign]:
        calendar_page = self._get_calendar_page()
        calendar_events = calendar_page.find_all("div", class_="event")
        for event_div in calendar_events:
            assign_elem = event_div.find("div", class_="card-footer").find("a")
            assign_url = assign_elem["href"]
            assign_page = self._get_assign_page(assign_url)
            attachments = self._get_attachments(assign_page)
            yield AssignParser.parse(
                page=assign_page,
                attachments=attachments,
                url=assign_url,
            )


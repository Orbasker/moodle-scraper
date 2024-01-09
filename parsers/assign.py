import dateparser
from bs4 import BeautifulSoup
from pydantic import AnyHttpUrl, HttpUrl

from models.assign import Assign, Attachment, Dates


class AssignParser:
    @classmethod
    def parse(cls, page: BeautifulSoup, url: AnyHttpUrl) -> Assign:
        return Assign(
            title=cls._get_name(page),
            description=cls._get_description(page),
            attachments=cls._get_attachments(page),
            dates=cls._get_dates(page),
            url=url,
        )

    @classmethod
    def _get_name(cls, page: BeautifulSoup) -> str:
        return page.find("h1", class_="h2").text.strip()

    @classmethod
    def _get_description(cls, page: BeautifulSoup) -> str:
        if description_raw := page.find("div", class_="activity-description"):
            return description_raw.text.strip()

    @classmethod
    def _get_dates(cls, page: BeautifulSoup) -> Dates:
        dates_elem = page.find("div", class_="activity-dates")

        dates = []
        for date_elem in dates_elem.find("div", class_="description-inner").find_all("div"):
            date_elem.find("strong").decompose()
            date_str = date_elem.text.strip()
            dates.append(dateparser.parse(date_str) if date_str else None)

        return Dates(*dates)

    @classmethod
    def _get_attachments(cls, page: BeautifulSoup) -> list[HttpUrl]:
        attachments = []
        if attachments_section := page.find(
            name="div",
            class_="fileuploadsubmission",
        ):
            attachments.extend(
                Attachment(
                    url=attachment["href"],
                    name=attachment.text.strip(),
                )
                for attachment in attachments_section.find_all("a", {"target": "_blank"})
            )
        return attachments

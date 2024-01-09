import dateparser
from bs4 import BeautifulSoup
from pydantic.v1 import AnyHttpUrl

from models.assign import Assign, Attachment, Dates


class AssignParser:
    @classmethod
    def parse(
        cls,
        page: BeautifulSoup,
        attachments: list[Attachment],
        url: AnyHttpUrl,
    ) -> Assign:
        return Assign(
            title=cls._get_name(page),
            description=cls._get_description(page),
            attachments=attachments,
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

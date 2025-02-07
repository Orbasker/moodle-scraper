from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import HttpUrl


@dataclass
class Dates:
    start: datetime
    due: datetime


@dataclass
class Attachment:
    name: str
    url: HttpUrl
    data: bytes


@dataclass
class Assign:
    title: str
    description: str
    dates: Dates
    url: HttpUrl
    attachments: Optional[list[Attachment]]
    course_name: str

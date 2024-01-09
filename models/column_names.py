from dataclasses import dataclass
@dataclass
class Dates:
    start: str
    due: str
@dataclass
class ColumnNames:
    description: str
    dates: Dates
    url: str
    attachments: str

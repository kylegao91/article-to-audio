import dataclasses
from dataclasses import dataclass
from typing import List, Union


@dataclass
class Article:
    source_name: str
    source_id: str
    source_rank: int
    title: Union[str, None]
    url: str

    text_list: Union[List[str], None] = None
    content: Union[str, None] = None
    summary: Union[str, None] = None

    def asdict(self):
        return dataclasses.asdict(self)

    @staticmethod
    def fromdict(obj):
        return Article(**obj)
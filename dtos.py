from enum import Enum
import dataclasses
from dataclasses import dataclass
from typing import List, Union
import logging


class Gender(Enum):
    MALE = 0
    FEMALE = 1


@dataclass
class Article:
    source_id: str
    source_rank: int
    title: Union[str, None]
    url: str

    text_list: Union[List[str], None] = None
    content: Union[str, None] = None
    summary: Union[str, None] = None

    def asdict(self):
        return dataclasses.asdict(self)


@dataclass
class Script:
    host_name: str
    host_gender: Gender
    text: str
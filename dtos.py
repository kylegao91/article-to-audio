import dataclasses
from dataclasses import dataclass
from typing import List, Union
import logging


@dataclass
class Article:
    source_id: str
    source_rank: int
    title: Union[str, None]
    url: str

    text_list: Union[List[str], None] = None
    content: Union[str, None] = None
    summary: Union[str, None] = None

    def should_skip(self):
        if self.url is None:
            logging.info("Story has no URL, skipping: %s", self.source_id)
            return True
        if self.url.startswith("https://www.github.com") or self.url.startswith(
            "https://github.com"
        ):
            logging.info("Github story, skipping: %s", self.url)
            return True
        return False

    def asdict(self):
        return dataclasses.asdict(self)
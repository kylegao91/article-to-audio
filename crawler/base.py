from typing import List

from dtos import Article


class BaseCrawler:
    def get_article_list(self, max_num_articles: int) -> List[Article]:
        raise NotImplementedError()

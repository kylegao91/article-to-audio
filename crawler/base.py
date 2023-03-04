import logging
from typing import List

from dtos import Article


class BaseCrawler:
    def __init__(self, parser):
        self.parser = parser

    def get_articles(self, max_num_articles: int) -> List[Article]:
        article_list = []
        for article in self.get_article_list(max_num_articles):
            try:
                self.parse_article(article)
            except:
                logging.warning("Failed to parse article: %s", article.url)
                continue
            article_list.append(article)
            if len(article_list) >= max_num_articles:
                break
        return article_list

    def get_article_list(self, max_num_articles: int) -> List[Article]:
        raise NotImplementedError()

    def parse_article(self, article: Article) -> Article:
        article.text_list = self.parser.get_url_content(article.url)
        return article

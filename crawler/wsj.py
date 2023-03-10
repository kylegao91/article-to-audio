import logging
from typing import List

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from crawler.base import BaseCrawler

from dtos import Article

WSJ_SOURCE = "Wall Street Journal"
WSJ_URL = "https://www.wsj.com/"


def get_page(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        content = page.content()
        # Test the background page as you would any other page.
        browser.close()
    return content


class WSJCrawler(BaseCrawler):
    def get_article_list(self, max_num_stories: int) -> List[Article]:
        html = get_page(WSJ_URL)

        soup = BeautifulSoup(html, "html.parser")

        top_articles = soup.find(id="top-news").find_all("article")
        for count, article in enumerate(top_articles):
            title_tag = article.find(["h3", "h4"])
            if title_tag is None:
                logging.warning("Skipping article with no title")
                continue
            title = title_tag.text
            url = title_tag.find("a").get("href")

            if self._should_skip(title, url):
                continue

            article = Article(
                source_name=WSJ_SOURCE,
                source_id=self._get_id(count),
                source_rank=count,
                title=title,
                url=url,
            )
            yield article

    def _get_id(self, count):
        return f"wsj-{count}"

    def _should_skip(self, title, url):
        if "livecoverage" in url:
            logging.info("Skipping live coverage article: %s", title)
            return True

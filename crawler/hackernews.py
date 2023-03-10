import logging
import requests
from typing import List

from dtos import Article
from crawler.base import BaseCrawler

HN_SOURCE = "Hackernews"
HN_TOPSTORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"


class HackerNewsCrawler(BaseCrawler):
    def get_article_list(self, max_num_stories: int) -> List[Article]:
        """Get the top stories from Hacker News."""
        logging.info("Getting top stories from Hacker News")
        top_story_ids = requests.get(HN_TOPSTORIES_URL).json()

        for count, story_id in enumerate(top_story_ids):
            story = requests.get(HN_ITEM_URL.format(story_id)).json()
            if self._should_skip(story):
                continue
            article = Article(
                source_name=HN_SOURCE,
                source_id=story_id,
                source_rank=count,
                title=story["title"],
                url=story.get("url", None),
            )
            yield article

    def _should_skip(self, story):
        if "url" not in story or story["url"] is None:
            logging.info("Story has no URL, skipping: %s", story["id"])
            return True
        url = story["url"]
        if url.startswith("https://www.github.com") or url.startswith(
            "https://github.com"
        ):
            logging.info("Github story, skipping: %s", url)
            return True
        return False

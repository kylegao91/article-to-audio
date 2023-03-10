from typing import List

from dtos import Article
from crawler.base import BaseCrawler


SAMPLE_STORIES = [
    {
        "id": "1",
        "title": "Amazon Pausing Construction of Washington, D.C.-Area Second Headquarters",
        "url": "https://www.wsj.com/articles/amazon-pausing-construction-of-washington-d-c-area-second-headquarters-b62ef6df",
    },
    {
        "id": "2",
        "title": "New York Pushes London Aside in Battle of Financial Centers",
        "url": "https://www.wsj.com/articles/chip-designer-arm-intends-to-list-in-new-york-12210e53",
    },
    {
        "id": "3",
        "title": "U.S. Prepares New Rules on Investment in China",
        "url": "https://www.wsj.com/articles/u-s-prepares-new-rules-on-investment-in-technology-abroad-a451e035",
    },
    {
        "id": "4",
        "title": "Wagner Chief Says Eastern Ukraine’s Bakhmut Is Effectively Surrounded",
        "url": "https://www.wsj.com/articles/wagner-chief-says-eastern-ukraines-bakhmut-is-effectively-surrounded-c7af41d6",
    },
    {
        "id": "5",
        "title": "The Tax Play That Saves Some Couples Big Bucks",
        "url": "https://www.wsj.com/articles/married-filing-separately-vs-jointly-taxes-f9f45ad2",
    },
]


class SampleCrawler(BaseCrawler):

    def get_article_list(self, max_num_stories: int) -> List[Article]:
        """Get sample articles."""

        article_list = []
        for count, story in enumerate(SAMPLE_STORIES):
            article = Article(
                source_name="Wall street journal",
                source_id=story["id"],
                source_rank=count,
                title=story["title"],
                url=story.get("url", None),
            )
            article_list.append(article)
            if len(article_list) >= max_num_stories:
                break
        return article_list

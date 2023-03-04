import datetime
import json
import logging

import pytz
from composer import Composer
from crawler import HackerNewsCrawler
from crawler.sample import SampleCrawler
from summary import OpenAISummarizer
from webparser import ChromeExtensionBypassPaywallParser, SimpleParser

logging.basicConfig(
    level=logging.DEBUG, format="%(name)s - %(levelname)s - %(message)s"
)

TIMEZONE = "America/New_York"

MAX_NUM_STORIES = 10
MAX_NUM_SUMMARIES = 5


if __name__ == "__main__":
    summarizer = OpenAISummarizer()
    parser = SimpleParser()
    crawler = HackerNewsCrawler(parser)
    # parser = ChromeExtensionBypassPaywallParser()
    # crawler = SampleCrawler(parser)

    article_list = crawler.get_articles(MAX_NUM_STORIES)

    summed_article_list = []
    try:
        for article in article_list:
            summary = summarizer.summarize(article.text_list)
            if not summary:
                logging.warning(
                    "Failed to generate summary for story: %s", article.source_id
                )
                continue
            article.summary = summary
            summed_article_list.append(article)

            if len(summed_article_list) >= MAX_NUM_SUMMARIES:
                break
    finally:
        with open("stories.json", "w") as f:
            f.write(json.dumps([a.asdict() for a in summed_article_list]))

    composer = Composer(
        "hackernews",
        datetime.datetime.now(tz=pytz.timezone(TIMEZONE)),
    )
    composer.compose(
        summed_article_list,
        output_file="output.wav",
    )

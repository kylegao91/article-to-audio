import os
import datetime
import json
import pickle
import logging

import pytz
from composer import Composer
from crawler import HackerNewsCrawler
from crawler.sample import SampleCrawler
from crawler.wsj import WSJCrawler
from dtos import Article
from podcast.castos import CastosPodcast
from summary import OpenAISummarizer
from webparser import ChromeExtensionBypassPaywallParser, SimpleParser

logging.basicConfig(
    level=logging.DEBUG, format="%(name)s - %(levelname)s - %(message)s"
)

TIMEZONE = "America/New_York"

SKIP_PUBLISH = os.getenv("SKIP_PUBLISH", "False").lower() == "true"
LOAD_FROM_STORY_DUMP = os.getenv("LOAD_FROM_STORY_DUMP", "False").lower() == "true"
LOAD_FROM_CONVO_DUMP = os.getenv("LOAD_FROM_CONVO_DUMP", "False").lower() == "true"

MAX_NUM_STORIES = 10
MAX_NUM_SUMMARIES = 10


if __name__ == "__main__":
    source_name = "Wall Street Journal"
    summarizer = OpenAISummarizer()
    # parser = SimpleParser()
    parser = ChromeExtensionBypassPaywallParser()
    # crawler = HackerNewsCrawler(parser)
    podcast_host = CastosPodcast()
    # crawler = SampleCrawler(parser)
    crawler = WSJCrawler(parser)

    if LOAD_FROM_STORY_DUMP:
        with open("stories.json", "r") as f:
            summed_article_list = [Article(**a) for a in json.loads(f.read())]
    else:
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

    if LOAD_FROM_CONVO_DUMP:
        with open("scripts.json", "rb") as f:
            podcast_scripts = pickle.load(f)
    else:
        podcast_scripts = summarizer.generate_conversation(
            [a.summary for a in summed_article_list]
        )
        with open("scripts.json", "wb") as f:
            pickle.dump(podcast_scripts, f)

    date = datetime.datetime.now(tz=pytz.timezone(TIMEZONE))
    audio_path = "output.mp3"
    note_path = "notes.txt"
    composer = Composer(source_name, date)
    # composer.compose(summed_article_list, output_file=audio_path, note_file=note_path)
    composer.compose_conversation(
        podcast_scripts, output_file=audio_path, note_file=note_path
    )

    # if not SKIP_PUBLISH:
    #     podcast_host.create_episode(
    #         52699,
    #         date.strftime("%A, %B %d"),
    #         note_path,
    #         audio_path,
    #     )

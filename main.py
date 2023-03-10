import os
import datetime
import json
import logging

import click
import pytz
from composer import Composer
from crawler import HackerNewsCrawler
from dtos import Article
from podcast.castos import CastosPodcast
from summary import OpenAISummarizer
from webparser import ChromeExtensionBypassPaywallParser, SimpleParser

logging.basicConfig(
    level=logging.DEBUG, format="%(name)s - %(levelname)s - %(message)s"
)

TIMEZONE = "America/New_York"

SKIP_PUBLISH = os.getenv("SKIP_PUBLISH", "False").lower() == "true"

MAX_NUM_STORIES = 10
MAX_NUM_SUMMARIES = 10


@click.group()
def cli():
    pass


@cli.command()
@click.option("--max-stories", default=MAX_NUM_STORIES)
@click.option("--output", default="stories.json")
def crawl(max_stories, output):
    parser = ChromeExtensionBypassPaywallParser()
    crawler = HackerNewsCrawler(parser)
    article_list = crawler.get_articles(max_stories)
    with open(output, "w") as f:
        f.write(json.dumps([a.asdict() for a in article_list]))


@cli.command()
@click.option("--max-summaries", default=MAX_NUM_SUMMARIES)
@click.option("--input", default="stories.json")
@click.option("--output", default="stories_with_summary.json")
def summary(max_summaries, input, output):
    with open(input, "r") as f:
        article_list = [Article.fromdict(a) for a in json.loads(f.read())]

    summarizer = OpenAISummarizer()
    summarized_article_list = []
    for article in article_list:
        summary = summarizer.summarize(article.text_list)
        if not summary:
            logging.warning(
                "Failed to generate summary for story: %s", article.source_id
            )
            continue
        article.summary = summary
        summarized_article_list.append(article)

        if len(summarized_article_list) >= max_summaries:
            break

    with open(output, "w") as f:
        f.write(json.dumps([a.asdict() for a in summarized_article_list]))


@cli.command()
@click.argument("feedname")
@click.option("--input", default="stories_with_summary.json")
@click.option("--data-dir", default="data")
@click.option("--audio-output", default="output.mp3")
@click.option("--note-output", default="output.txt")
def compose(feedname, input, data_dir, audio_output, note_output):
    with open(input, "r") as f:
        article_list = [Article.fromdict(a) for a in json.loads(f.read())]

    date = datetime.datetime.now(tz=pytz.timezone(TIMEZONE))
    composer = Composer(feedname, date, data_dir)
    composer.compose(article_list, output_file=audio_output, note_file=note_output)


@cli.command()
@click.argument("podcast-id")
@click.argument("audio-path")
@click.argument("note_path")
def publish(podcast_id, audio_path, note_path):
    podcast_host = CastosPodcast()

    date = datetime.datetime.now(tz=pytz.timezone(TIMEZONE))
    title = date.strftime("%A, %B %d")

    podcast_host.create_episode(
        podcast_id,
        title,
        note_path,
        audio_path,
    )

if __name__ == '__main__':
    cli()
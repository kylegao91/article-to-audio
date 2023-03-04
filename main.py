import datetime
import json
import os
from typing import List
import logging

import pytz
import openai
from transformers import GPT2TokenizerFast
from composer import Composer
from crawler import HackerNewsCrawler
from crawler.sample import SampleCrawler
from webparser import ChromeExtensionBypassPaywallParser, SimpleParser

logging.basicConfig(
    level=logging.DEBUG, format="%(name)s - %(levelname)s - %(message)s"
)

TIMEZONE = "America/New_York"

OPENAI_MOCK = os.getenv("OPENAI_MOCK", "False").lower() == "true"
OPENAI_ORG_ID = os.environ.get("OPENAI_ORG_ID")
OPENAI_API_TOKEN = os.environ.get("OPENAI_API_TOKEN")
OPENAI_MAX_TOKEN = 4096
OPENAI_MAX_RESPONSE_TOKEN = 256

MAX_NUM_STORIES = 10
MAX_NUM_SUMMARIES = 5


class Summarizer:
    def __init__(self, tokenizer, max_length):
        self.tokenizer = tokenizer
        self.max_length = max_length

    def break_down_text(self, text) -> List[str]:
        text_len = self.tokenizer(text, return_length=True).length[0]
        if text_len > self.max_length:
            # TODO: This is a naive way of breaking down text. Improve it.
            separator = ". "
            splits = text.split(". ")
            if len(splits) == 1:
                splits = text.split(" ")
                separator = " "
            mid = len(splits) // 2
            first = separator.join(splits[:mid])
            second = separator.join(splits[mid:])
            return self.break_down_text(first) + self.break_down_text(second)
        else:
            return [text]

    def get_chunks(self, text_list) -> List[str]:
        # first, break up the text into chunks that are less than the max length
        breakdown_chunk_list = []
        for text in text_list:
            breakdown_chunk_list += self.break_down_text(text)

        # second, merge chunks that are less than the max length
        merged_chunk_list = []
        chunk = ""
        current_length = 0
        for text in breakdown_chunk_list:
            text_len = self.tokenizer(text, return_length=True).length[0]

            if current_length + text_len > self.max_length:
                merged_chunk_list.append(chunk)
                chunk = ""
                current_length = 0
            chunk += " " + text
            current_length += text_len
        if chunk:
            merged_chunk_list.append(chunk)

        return merged_chunk_list

    def summarize(self, text_list: List[str]) -> str:
        """Summarize a list of text, recursively to bypass GPT's token limit."""
        logging.info("Summarizing text")

        chunk_list = self.get_chunks(text_list)
        summary_list = [openai_summarize_text(chunk) for chunk in chunk_list]

        if len(summary_list) == 1:
            return summary_list[0]
        else:
            return self.summarize(summary_list)


def openai_authenticate():
    """Authenticate with OpenAI."""
    logging.info("Authenticating with OpenAI")
    openai.api_key = OPENAI_API_TOKEN
    openai.organization = OPENAI_ORG_ID


def openai_summarize_text(text):
    """Summarize text using OpenAI."""
    logging.info("Summarizing text with OpenAI")
    if OPENAI_MOCK:
        return "This is a mock summary."

    prompt = [
        {
            "role": "system",
            "content": "You are a helpful assitant that summarize longer text into podcast ready scripts.",
        },
        {
            "role": "user",
            "content": f"Summarize this:\n{text}",
        },
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt,
        max_tokens=256,
    )
    return response.choices[0].message["content"]


if __name__ == "__main__":
    openai_authenticate()
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    summarizer = Summarizer(tokenizer, OPENAI_MAX_TOKEN - OPENAI_MAX_RESPONSE_TOKEN)

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
    composer.compose(summed_article_list, "output.wav")

import datetime
import json
import os
from typing import List
import requests
import logging

import pytz
import openai
from readabilipy import simple_json_from_html_string
from transformers import GPT2TokenizerFast
from composer import Composer

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")

TIMEZONE = "America/New_York"

OPENAI_ORG_ID = os.environ.get("OPENAI_ORG_ID")
OPENAI_API_TOKEN = os.environ.get("OPENAI_API_TOKEN")
OPENAI_MAX_TOKEN = 2048
OPENAI_MAX_RESPONSE_TOKEN = 256

HN_TOPSTORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

TOP_N = 3


class Summarizer:
    def __init__(self, tokenizer, max_length):
        self.tokenizer = tokenizer
        self.max_length = max_length

    def get_chunks(self, text_list) -> List[str]:
        chunk_list = []

        chunk = ""
        current_length = 0
        for text in text_list:
            text_len = self.tokenizer(text, return_length=True).length[0]
            if current_length + text_len > self.max_length:
                chunk_list.append(chunk)
                chunk = ""
                current_length = 0
            chunk += " " + text
            current_length += text_len
        if chunk:
            chunk_list.append(chunk)

        return chunk_list

    def summarize(self, text_list: List[str]) -> str:
        """Summarize a list of text, recursively to bypass GPT's token limit."""
        logging.info("Summarizing text")

        chunk_list = self.get_chunks(text_list)
        summary_list = [openai_summarize_text(chunk) for chunk in chunk_list]

        if len(summary_list) == 1:
            return summary_list[0]
        else:
            return self.summarize(summary_list)


def get_url_content(url) -> List[str]:
    """Get the content of a URL, return as a list of strings."""
    logging.info("Getting content from URL: %s", url)
    req = requests.get(url)
    article = simple_json_from_html_string(req.text, use_readability=True)
    text_list = [t["text"] for t in article["plain_text"]]
    return text_list


def get_hackernews_top_stories():
    """Get the top stories from Hacker News."""
    logging.info("Getting top stories from Hacker News")
    top_stories = requests.get(HN_TOPSTORIES_URL).json()
    return top_stories


def get_hackernews_item(item_id):
    """Get a single item from Hacker News."""
    logging.info("Getting item from Hacker News: %s", item_id)
    item = requests.get(HN_ITEM_URL.format(item_id)).json()
    return item


def openai_authenticate():
    """Authenticate with OpenAI."""
    logging.info("Authenticating with OpenAI")
    openai.api_key = OPENAI_API_TOKEN
    openai.organization = OPENAI_ORG_ID


def openai_summarize_text(text):
    """Summarize text using OpenAI."""
    logging.info("Summarizing text with OpenAI")
    prompt = f"Summarize this, ignore html:\n{text}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        top_p=1,
        max_tokens=256,
    )
    return response["choices"][0]["text"]


def skip_story(story):
    if story["url"].startswith("https://www.github.com") or story["url"].startswith(
        "https://github.com"
    ):
        logging.info("Github story, skipping: %s", story["url"])
        return True
    return False


if __name__ == "__main__":
    openai_authenticate()
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    summarizer = Summarizer(tokenizer, OPENAI_MAX_TOKEN - OPENAI_MAX_RESPONSE_TOKEN)

    top_story_ids = get_hackernews_top_stories()

    story_list = []
    for count, story_id in enumerate(top_story_ids):
        story = get_hackernews_item(story_id)
        if skip_story(story):
            continue

        text_list = get_url_content(story["url"])
        story["summary"] = summarizer.summarize(text_list)
        if not story["summary"]:
            logging.warning("Failed to generate summary for story: %s", story["url"])
        # story["summary"] = "This is a summary of the story."
        story_list.append(story)

        count += 1
        if count >= TOP_N:
            break

    included_stories = [s for s in story_list if "summary" in s]

    with open("stories.json", "w") as f:
        f.write(json.dumps(included_stories))

    composer = Composer(
        "hackernews",
        datetime.datetime.now(tz=pytz.timezone(TIMEZONE)),
    )
    composer.compose(included_stories, "output.wav")

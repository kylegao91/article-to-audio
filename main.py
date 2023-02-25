import os
import json
import requests
import logging

import openai
from readabilipy import simple_json_from_html_string

from text_to_speech import TextToSpeech

AWS_PROFILE = os.environ.get("AWS_PROFILE", "default")

OPENAI_ORG_ID  = "org-ESQ6hYtJpMURFdC5NwuRm0ho"
OPENAI_API_TOKEN = os.environ.get("OPENAI_API_TOKEN")

HN_TOPSTORIES_URL = 'https://hacker-news.firebaseio.com/v0/topstories.json'
HN_ITEM_URL = 'https://hacker-news.firebaseio.com/v0/item/{}.json'

TOP_N = 1

def get_url_content(url):
    """Get the content of a URL."""
    req = requests.get(url)
    article = simple_json_from_html_string(req.text, use_readability=True)
    return article["plain_content"]

def get_hackernews_top_stories():
    """Get the top stories from Hacker News."""
    top_stories = requests.get(HN_TOPSTORIES_URL).json()
    return top_stories

def get_hackernews_item(item_id):
    """Get a single item from Hacker News."""
    item = requests.get(HN_ITEM_URL.format(item_id)).json()
    return item

def openai_authenticate():
    """Authenticate with OpenAI."""
    openai.api_key = OPENAI_API_TOKEN
    openai.organization = OPENAI_ORG_ID

def openai_summarize_text(text):
    """Summarize text using OpenAI."""
    prompt = f"Summarize this, ignore html:\n{text}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        top_p=1,
        max_tokens=256,
    )
    return response["choices"][0]["text"]

if __name__ == "__main__":
  openai_authenticate()
  text_to_speech_client = TextToSpeech(AWS_PROFILE)

  top_stories = get_hackernews_top_stories()
  for story_id in top_stories[:TOP_N]:
    story = get_hackernews_item(story_id)
    content = get_url_content(story["url"])
    story["summary"]= openai_summarize_text(content)
    print(json.dumps(story))
    text_to_speech_client.convert(story["summary"])
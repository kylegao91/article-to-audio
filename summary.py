import logging
import os
from typing import List

import openai
from transformers import GPT2TokenizerFast

from dtos import Gender, Script


OPENAI_MOCK = os.getenv("OPENAI_MOCK", "False").lower() == "true"
OPENAI_ORG_ID = os.environ.get("OPENAI_ORG_ID")
OPENAI_API_TOKEN = os.environ.get("OPENAI_API_TOKEN")
OPENAI_MAX_TOKEN = 4096
OPENAI_MAX_RESPONSE_TOKEN = 256


def openai_authenticate():
    """Authenticate with OpenAI."""
    logging.info("Authenticating with OpenAI")
    openai.api_key = OPENAI_API_TOKEN
    openai.organization = OPENAI_ORG_ID


def openai_summarize_text(
    text,
    prompt="Summarize this",
    max_tokens=OPENAI_MAX_RESPONSE_TOKEN,
):
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
            "content": f"{prompt}:\n{text}",
        },
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt,
        max_tokens=max_tokens,
    )
    return response.choices[0].message["content"]


class OpenAISummarizer:
    def __init__(
        self,
        tokenizer=GPT2TokenizerFast.from_pretrained("gpt2"),
        max_length=OPENAI_MAX_TOKEN - OPENAI_MAX_RESPONSE_TOKEN,
    ):
        self.tokenizer = tokenizer
        self.max_length = max_length
        openai_authenticate()

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

    def generate_conversation(self, topic_list: List[str]) -> List[Script]:
        """Given a list of topics, generate a conversation that discusses them."""

        # assumes each topic is ~256 tokens
        CHUNK_SIZE = 2
        PROMPT_PREFIX = (
            "Generate a podcast script between John and Carol, two podcast hosts, on today's headline stories below.  "
            "Have at least two exchanges for each topic.  "
        )
        FIRST_PROMPT_SUFFIX = (
            "There are more topics to cover later, so don't close the conversation."
        )
        MID_PROMPT_SUFFIX = "They have covered a few other stories already today.  There are more topics to cover later, so don't close the conversation."
        LAST_PROMPT_SUFFIX = "They have covered a few other stories already today.  Close the conversation at the end by saying goodbye to the audiences.."

        num_chunks = len(topic_list) // CHUNK_SIZE
        if len(topic_list) % CHUNK_SIZE != 0:
            num_chunks += 1

        script_list = []
        for chunk_idx in range(num_chunks):
            topics = topic_list[chunk_idx * CHUNK_SIZE : (chunk_idx + 1) * CHUNK_SIZE]
            if not topics:
                continue
            text = ""
            for topic_idx, topic in enumerate(topics):
                text += f"Story {chunk_idx * CHUNK_SIZE + topic_idx + 1}: \n{topic}\n\n"

            if chunk_idx == 0:
                prompt = PROMPT_PREFIX + FIRST_PROMPT_SUFFIX
            elif chunk_idx == num_chunks - 1:
                prompt = PROMPT_PREFIX + LAST_PROMPT_SUFFIX
            else:
                prompt = PROMPT_PREFIX + MID_PROMPT_SUFFIX

            prompt_length = self.tokenizer(prompt, return_length=True).length[0]
            text_length = self.tokenizer(text, return_length=True).length[0]
            max_tokens = OPENAI_MAX_TOKEN - prompt_length - text_length - 100
            generated = openai_summarize_text(
                text, prompt=prompt, max_tokens=max_tokens
            )
            script_list += generated.split("\n\n")

        parsed_script_list = []
        for script in script_list:
            fields = script.split(": ")
            if len(fields) != 2:
                logging.error("Invalid script: %s", script)
                continue
            host, text = fields
            if host == "John":
                gender = Gender.MALE
            elif host == "Carol":
                gender = Gender.FEMALE
            else:
                raise ValueError(f"Unknown host {host}")
            parsed_script_list.append(Script(host, gender, text))
        return parsed_script_list

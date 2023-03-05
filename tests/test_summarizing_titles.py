from utils.preprocessing import sample
from summary import (
    openai_summarize_text,
    openai_authenticate,
    OPENAI_MOCK,
)
import os
import openai

real_test = os.getenv("GIVE_A_CENT", 0)

import pytest


def testing_title_combined() -> None:
    """
     GIVE_A_CENT=1 pytest tests/test_summarizing_titles.py -s
    """
    raw_text = "data/news_10.txt"
    sampled_text = sample(raw_text)
    if real_test:
        openai.organization = os.getenv("OPENAI_ORG_ID", None)
        openai.api_key = os.getenv("OPENAI_API_TOKEN", None)
    else:
        OPENAI_MOCK = True
    response = openai_summarize_text(
        sampled_text,
        "below are 10 stories, make a eye catching title from any of the story that you feel best to attract reader's attention",
        OPENAI_MOCK=not real_test,
    )
    assert response is not None
    print(response)

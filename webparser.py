import logging
from typing import List
import requests

from playwright.sync_api import sync_playwright
from readabilipy import simple_json_from_html_string


class BaseParser:
    def get_url_content(self, url) -> List[str]:
        """Get the content of a URL, return as a list of strings."""
        raise NotImplementedError()


class SimpleParser(BaseParser):
    def get_url_content(self, url) -> List[str]:
        """Get the content of a URL, return as a list of strings."""
        logging.info("Getting content from URL: %s", url)
        req = requests.get(url)
        article = simple_json_from_html_string(req.text, use_readability=True)
        text_list = [t["text"] for t in article["plain_text"]]
        return text_list


class ChromeExtensionBypassPaywallParser(BaseParser):
    def __init__(self, extention_path: str = "./extentions"):
        self.extention_path = extention_path
        self.user_data_dir = "/tmp/test-user-data-dir"

    def get_url_content(self, url) -> List[str]:
        """Get the content of a URL, return as a list of strings."""
        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                self.user_data_dir,
                headless=False,
                args=[
                    f"--disable-extensions-except={self.extention_path}",
                    f"--load-extension={self.extention_path}",
                ],
            )

            page = context.new_page()
            page.goto(url)
            readable = simple_json_from_html_string(
                page.content(), use_readability=True
            )
            text_list = [t["text"] for t in readable["plain_text"]]

            # Test the background page as you would any other page.
            context.close()
        return text_list

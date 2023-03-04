import os
import requests

from requests_toolbelt.multipart.encoder import MultipartEncoder

CASTOS_BASE_URL = "https://app.castos.com/api/v2"
CASTOS_API_TOKEN = os.environ.get("CASTOS_API_TOKEN")


class CastosPodcast:
    def __init__(self):
        pass

    def get_episode(self, podcast_id, episode_id):
        req = requests.get(
            f"{CASTOS_BASE_URL}/podcasts/{podcast_id}/episodes/{episode_id}",
            params={"token": CASTOS_API_TOKEN},
        )
        return req.json()

    def create_episode(self, podcast_id, title, show_note_path, file_path):
        show_note = open(show_note_path).read()
        payload = MultipartEncoder(
            fields={
                "post_title": title,
                "post_content": show_note,
                "episode_file": (file_path, open(file_path, "rb"), "audio/mpeg"),
            }
        )
        req = requests.post(
            f"{CASTOS_BASE_URL}/podcasts/{podcast_id}/episodes/",
            params={"token": CASTOS_API_TOKEN},
            data=payload,
            headers={"Content-Type": payload.content_type},
        )
        req.raise_for_status()

    def update_episode(self, podcast_id, episode_id, title, show_note):
        payload = MultipartEncoder(
            fields={
                "post_title": title,
                "post_content": show_note,
            }
        )
        req = requests.post(
            f"{CASTOS_BASE_URL}/podcasts/{podcast_id}/episodes/{episode_id}",
            params={"token": CASTOS_API_TOKEN},
            data=payload,
            headers={"Content-Type": payload.content_type},
        )
        req.raise_for_status()

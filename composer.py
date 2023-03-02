import os
from datetime import datetime
from typing import List

from pydub import AudioSegment
from dtos import Article

from text_to_speech import TextToSpeech


class Composer:
    def __init__(self, feed_name: str, date_created: datetime):
        self.feed_name = feed_name
        self.date_created = date_created
        self.tts = TextToSpeech()

        self._data_dir = os.path.join(
            os.path.dirname(__file__),
            "data",
            self.feed_name,
        )
        self._date_data_dir = os.path.join(
            os.path.dirname(__file__),
            "data",
            self.feed_name,
            self.date_created.strftime("%Y-%m-%d"),
        )
        if not os.path.exists(self._date_data_dir):
            os.makedirs(self._date_data_dir)

    def compose(self, article_list: List[Article], output_file: str):
        full_audio = AudioSegment.empty()

        open_path = os.path.join(self._date_data_dir, "open.wav")
        self.tts.convert(f"Welcome to {self.feed_name} daily!", open_path)
        full_audio += AudioSegment.from_wav(open_path)

        date_plug_path = os.path.join(self._date_data_dir, f"date_plug.wav")
        self.tts.convert(
            f"Today is {self.date_created.strftime('%A, %B %d')}",
            date_plug_path,
        )
        full_audio += AudioSegment.from_wav(date_plug_path)

        summary_prompt_path = os.path.join(self._date_data_dir, "summary_prompt.wav")
        self.tts.convert("This is a summary of the story.", summary_prompt_path)
        summary_prompt = AudioSegment.from_wav(summary_prompt_path)

        for idx, story in enumerate(article_list):
            filler_path = os.path.join(self._data_dir, f"filler_{idx + 1}.wav")
            filler = self._get_filler(idx, len(article_list))
            self.tts.convert(filler, filler_path)
            full_audio += AudioSegment.from_wav(filler_path)

            title_path = os.path.join(
                self._date_data_dir, f"{story.source_id }_title.wav"
            )
            self.tts.convert(story.title, title_path)
            full_audio += AudioSegment.from_wav(title_path)

            full_audio += summary_prompt

            audio_path = os.path.join(self._date_data_dir, f"{story.source_id}.wav")
            self.tts.convert(story.summary, audio_path)
            full_audio += AudioSegment.from_wav(audio_path)

        close_path = os.path.join(self._date_data_dir, "close.wav")
        self.tts.convert(
            "That's it for today's update. Thank you for listening!", close_path
        )
        full_audio += AudioSegment.from_wav(close_path)

        full_audio.export(output_file, format="wav")

    def _get_filler(self, idx: int, num_stories: int) -> str:
        if idx <= 3:
            filler = f"Story number {idx + 1}."
        elif idx == num_stories - 1:
            filler = "Last story of the day."
        else:
            filler = "Next story."
        return filler

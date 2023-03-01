import os
from datetime import datetime

from pydub import AudioSegment

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

    def compose(self, story_list, output_file):
        full_audio = AudioSegment.empty()

        full_audio += AudioSegment.from_wav(os.path.join(self._data_dir, "open.wav"))

        date_plug_path = os.path.join(self._date_data_dir, f"date_plug.wav")
        self.tts.convert(
            f"Today is {self.date_created.strftime('%A, %B %d')}",
            date_plug_path,
        )
        full_audio += AudioSegment.from_wav(date_plug_path)

        for count, story in enumerate(story_list):
            if count == len(story_list) - 1:
                filler_path = os.path.join(self._data_dir, "filler_last.wav")
            else:
                filler_path = os.path.join(self._data_dir, f"filler_{count + 1}.wav")
            full_audio += AudioSegment.from_wav(filler_path)

            title_path = os.path.join(self._date_data_dir, f"{story['id']}_title.wav")
            self.tts.convert(story["title"], title_path)
            full_audio += AudioSegment.from_wav(title_path)

            audio_path = os.path.join(self._date_data_dir, f"{story['id']}.wav")
            self.tts.convert(story["summary"], audio_path)
            full_audio += AudioSegment.from_wav(audio_path)

        full_audio += AudioSegment.from_wav(os.path.join(self._data_dir, "close.wav"))

        full_audio.export(output_file, format="wav")

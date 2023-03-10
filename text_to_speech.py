import os
import sys
import azure.cognitiveservices.speech as speechsdk


class TextToSpeech:
    def __init__(self):
        # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
        self.speech_config = speechsdk.SpeechConfig(
            subscription=os.environ.get("AZURE_KEY"),
            region=os.environ.get("AZURE_REGION"),
        )

        # The language of the voice that speaks.
        self.speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

    def convert(self, text: str, output_file: str):
        ssml = """
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis"
            xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">
            <voice name="en-US-JennyNeural">
                <prosody rate="+30%">
                    {text}
                </prosody>
            </voice>
        </speak>
        """.format(
            text=text
        )

        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config, audio_config=audio_config
        )
        speech_synthesis_result = speech_synthesizer.speak_ssml(ssml)

        if (
            speech_synthesis_result.reason
            == speechsdk.ResultReason.SynthesizingAudioCompleted
        ):
            print("Speech synthesized for text [{}]".format(text))
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print(
                        "Error details: {}".format(cancellation_details.error_details)
                    )
                    print("Did you set the speech resource key and region values?")


if __name__ == "__main__":
    client = TextToSpeech()

    text = sys.argv[1]
    output_path = sys.argv[2]

    client.convert(text, output_path)

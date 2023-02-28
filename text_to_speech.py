"""Getting Started Example for Python 2.7+/3.3+"""
import logging
from contextlib import closing

from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError


class TextToSpeech(object):

  def __init__(self, profile="default"):
    # Create a client using the credentials and region defined in the [adminuser]
    # section of the AWS credentials file (~/.aws/credentials).
    session = Session(profile_name=profile)
    self.polly = session.client("polly")

  def convert(self, text, output):
    logging.info("Converting text to speech")
    try:
        # Request speech synthesis
        response = self.polly.synthesize_speech(Text=text, OutputFormat="mp3", VoiceId="Joanna")
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        return False

    # Access the audio stream from the response
    if "AudioStream" in response:
        # Note: Closing the stream is important because the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
        with closing(response["AudioStream"]) as stream:
          print("Writing speech to file: " + output)
          try:
              # Open a file for writing the output as a binary stream
              with open(output, "wb") as file:
                file.write(stream.read())
          except IOError as error:
              # Could not write to file, exit gracefully
              print(error)
              return False

    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        return False

    return True
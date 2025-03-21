# Import necessary libraries
from transformers import pipeline
import requests
import logging
from youtube_transcript_api import YouTubeTranscriptApi
from readProperties import PropertiesReader
from DB import Database
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import AuthorizedSession
from flask import session


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CaptionDerivationAudio:
    def __init__(self):
        self.properties = PropertiesReader("config.properties")
        self.db = Database()

    def __str__(self):
        return f"{CaptionDerivationAudio.__name__}"
    
    def get_audio_id(self, audio_path):
        audio_id = audio_path.split("=")[-1]
        if audio_id is None:
            audio_id = audio_path.split("/")[-1]

        return audio_id
    
    def get_captions(self, audio_path, source="all"):
        '''
            Get captions from the audio.
        ''' 
        logging.info(f"Getting captions from {audio_path} using {source}")
        
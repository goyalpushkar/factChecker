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
from Authorization import Authorization


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CaptionDerivationVideo:
    def __init__(self):
        self.properties = PropertiesReader()
        self.db = Database()
        self.authorization = Authorization()

    def __str__(self):
        return f"{CaptionDerivationVideo.__name__}"
    
    def get_video_id(self, video_path):
        video_id = video_path.split("=")[-1]
        if video_id is None:
            video_id = video_path.split("/")[-1]

        return video_id
    
    def get_captions_nlp(self, video_path):
        '''
            Get captions from the video using the Hugging Face pipeline.
        '''
        try:
            nlp = pipeline("video-to-text", device=0)
            captions = nlp(video_path)
            return captions
        except Exception as e:
            logging.error(f"Error getting captions: {e}")
            return None
    
    def get_captions_thirdparty(self, video_path):
        '''
            Get captions from the video using third party app
            https://github.com/jdepoix/youtube-transcript-api?utm_source=chatgpt.com

            Pass in the video ID, NOT the video URL. For a video with the URL https://www.youtube.com/watch?v=12345 the ID is 12345.
        '''
        try:
            video_id = self.get_video_id(video_path)
            
            ytt_api = YouTubeTranscriptApi()
            captions = ytt_api.fetch(video_id)
            return captions.to_raw_data()   # return the value in dictionary format
        except Exception as e:
            logging.error(f"Error getting captions: {e}")
            return None
        
    def get_captions_google(self, video_path, language_code="en"):
        '''
            Get captions from the video using Google API and OAuth 2.0
            https://developers.google.com/youtube/v3/docs/captions/list
            https://developers.google.com/youtube/v3/docs/captions/download
            https://developers.google.com/youtube/v3/guides/implementation/captions?utm_source=chatgpt.com
        '''
        try:
            video_id = self.get_video_id(video_path)
            credentials = self.authorization.get_session_credentials()
            if not credentials:
                return "No credentials found"

            authed_session = self.authorization.get_authorized_session(credentials)

            # 1. Get the list of available caption tracks
            list_url = f"https://www.googleapis.com/youtube/v3/captions?part=snippet&videoId={video_id}"
            response = authed_session.get(list_url)
            response.raise_for_status()
            data = response.json()

            caption_tracks = data.get("items", [])
            if not caption_tracks:
                logging.info(f"get_captions_google: No captions found for video: {video_id}")
                return "No captions found"

            # 2. Find the caption track for the desired language (or default to the first one)
            target_track_id = None
            for track in caption_tracks:
                if track["snippet"]["language"] == language_code:
                    target_track_id = track["id"]
                    break
            if not target_track_id:
                logging.warning(f"No captions found for language code '{language_code}'. Using the first available track.")
                target_track_id = caption_tracks[0]["id"]

            # 3. Download the caption data
            download_url = f"https://www.googleapis.com/youtube/v3/captions/{target_track_id}?tfmt=srt"
            response = authed_session.get(download_url)
            response.raise_for_status()

            # 4. Return the caption text
            caption_text = response.text
            logging.info(f"get_captions_google: Captions {caption_text} found for video: {video_id}")
            return caption_text

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                logging.error(f"Error getting captions: {e}. Check if the video is private or if the API key has the correct permissions.")
                return "Video is private or API key has no permissions"
            elif e.response.status_code == 404:
                logging.error(f"Error getting captions: {e}. No captions found for the video.")
                return "No captions found"
            else:
                logging.error(f"Error getting captions: {e}")
                return "Error getting captions"
        except requests.RequestException as e:
            logging.error(f"Error getting captions: {e}")
            return "Error getting captions"
        except Exception as e:
            logging.error(f"Error getting captions: {e}")
            return "Error getting captions"
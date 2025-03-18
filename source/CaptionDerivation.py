# Import necessary libraries
from transformers import pipeline
import requests
import logging
from youtube_transcript_api import YouTubeTranscriptApi
from readProperties import PropertiesReader

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CaptionDerivation:
    def __init__(self):
        self.properties = PropertiesReader("config.properties")

    def __str__(self):
        return f"{CaptionDerivation.__name__}"
    
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
            video_id = video_path.split("=")[-1]
            ytt_api = YouTubeTranscriptApi()
            captions = ytt_api.fetch(video_id)
            return captions.to_raw_data()   # return the value in dictionary format
        except Exception as e:
            logging.error(f"Error getting captions: {e}")
            return None
    
    def get_captions_google(self, video_path):
        '''
            Get captions from the video using Google API
            https://developers.google.com/youtube/v3/docs/captions/download?utm_source=chatgpt.com
            https://developers.google.com/youtube/v3/guides/implementation/captions?utm_source=chatgpt.com
        '''
        try:
            video_id = video_path.split("=")[-1]
            google_api_key = self.properties.get_property("api", "google_api_key")
            api_url = f"https://www.googleapis.com/youtube/v3/captions?part=snippet&videoId={video_id}&key={google_api_key}"    # Replace with your own API key
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()      
            captions = data.get("items", [])
            return captions
        except requests.RequestException as e:
            logging.error(f"Error getting captions: {e}")
            return None
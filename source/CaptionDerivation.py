# Import necessary libraries
from transformers import pipeline
import requests
import logging
from youtube_transcript_api import YouTubeTranscriptApi
from readProperties import PropertiesReader
from CaptionDerivationVideo import CaptionDerivationVideo
from CaptionDerivationAudio import CaptionDerivationAudio
from DB import Database

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CaptionDerivation:
    def __init__(self):
        self.properties = PropertiesReader("config.properties")
        self.db = Database()
        self.videoCaptions = CaptionDerivationVideo()
        self.audioCaptions = CaptionDerivationAudio()

    def __str__(self):
        return f"{CaptionDerivation.__name__}"
    
    def get_captions(self, video_path, source="all"):
        '''
            Get captions from the video.
        '''
        logging.info(f"Getting captions from {video_path} using {source}")

        video_id = self.videoCaptions.get_video_id(video_path)

        cached_result = self.db.get_captions_cached_result(video_id)
        if cached_result:
            return cached_result

        nlp_captions = None
        tp_captions = None
        google_captions = None

        if source == "nlp":
            nlp_captions = self.videoCaptions.get_captions_nlp(video_path)
            if nlp_captions:
                self.db.insert_captions_cache(video_id, nlp_captions)
        elif source == "thirdparty":
            tp_captions = self.videoCaptions.get_captions_thirdparty(video_path)
            final_tp_captions = ""
            for data in tp_captions:
                final_tp_captions += data.get("text", "")
                final_tp_captions += " "
            tp_captions = final_tp_captions
            
            if tp_captions:
                self.db.insert_captions_cache(video_id, tp_captions)
        elif source == "google":
            google_captions = self.videoCaptions.get_captions_google(video_path)

            if google_captions:
                self.db.insert_captions_cache(video_id, google_captions)
        else:
            nlp_captions = self.videoCaptions.get_captions_nlp(video_path)
            tp_captions = self.videoCaptions.get_captions_thirdparty(video_path)
            google_captions = self.videoCaptions.get_captions_google(video_path)
            
            # tp_captions = [{'text': 'this is ritesh srinivasana and welcome', 'start': 0.179, 'duration': 4.681}, 
            #                {'text': "to my channel in this video let's look", 'start': 2.22, 'duration': 5.76}]
            final_tp_captions = ""
            for data in tp_captions:
                final_tp_captions += data.get("text", "")
                final_tp_captions += " "
            tp_captions = final_tp_captions

            # logging.info(f"Captions: {nlp_captions}, {tp_captions}, {google_captions}")
            captions = nlp_captions if nlp_captions else "" \
            + tp_captions if tp_captions else "" \
            + google_captions if google_captions else ""

            # logging.info(f"Captions: {captions}")
            if captions & captions != "":
                self.db.insert_captions_cache(video_id, captions)
        
        return {"nlp": nlp_captions, \
                "thirdparty": tp_captions, \
                "google": google_captions
                }
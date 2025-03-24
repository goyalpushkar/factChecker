# Import necessary libraries
import logging
from readProperties import PropertiesReader
from CaptionDerivationVideo import CaptionDerivationVideo
from CaptionDerivationAudio import CaptionDerivationAudio
from DB import Database

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CaptionDerivation:
    """
    A class to derive captions from a given video.
    """
    def __init__(self, kwargs=None):
        if 'properties' in kwargs:
            self.properties = kwargs['properties']
        else:
            self.properties = PropertiesReader()
        self.db = Database()
        self.video_captions = CaptionDerivationVideo(kwargs={"properties":self.properties})
        self.audio_captions = CaptionDerivationAudio(kwargs={"properties":self.properties})

    def __str__(self):
        return f"{CaptionDerivation.__name__}"
    
    def get_captions(self, video_path, source="all"):
        '''
            Get captions from the video.
        '''
        logging.info(f"get_captions: Getting captions from {video_path} using {source}")

        video_id = self.video_captions.get_video_id(video_path)

        # Temporarily disable cache
        # cached_result = self.db.get_captions_cached_result(video_id)
        # if cached_result:
        #     return cached_result

        nlp_captions = None
        tp_captions = None
        google_captions = None
        final_caption = ""

        if source == "nlp":
            nlp_captions = self.video_captions.get_captions_nlp(video_path)
            if nlp_captions:
                self.db.insert_captions_cache(video_id, nlp_captions)

            return nlp_captions
        elif source == "thirdparty":
            tp_captions = self.video_captions.get_captions_thirdparty(video_path)
            final_tp_captions = ""
            for data in tp_captions:
                final_tp_captions += data.get("text", "")
                final_tp_captions += " "
            tp_captions = final_tp_captions
            
            if tp_captions:
                self.db.insert_captions_cache(video_id, tp_captions)
            
            return tp_captions  
        elif source == "google":
            google_captions = self.video_captions.get_captions_google(video_path)

            if google_captions:
                self.db.insert_captions_cache(video_id, google_captions)

            return google_captions
        else:
            try:
                nlp_captions = self.video_captions.get_captions_nlp(video_path)
            except Exception as e:
                logging.error(f"Error getting captions: {e}")
            
            if not nlp_captions:
                try:
                    tp_captions = self.video_captions.get_captions_thirdparty(video_path)
                    # tp_captions = [{'text': 'this is ritesh srinivasana and welcome', 'start': 0.179, 'duration': 4.681}, 
                    #                {'text': "to my channel in this video let's look", 'start': 2.22, 'duration': 5.76}]
            
                    final_tp_captions = ""
                    for data in tp_captions:
                        final_tp_captions += data.get("text", "")
                        final_tp_captions += " "
                    tp_captions = final_tp_captions
                except Exception as e:
                    logging.error(f"Error getting captions: {e}")
                
            if not tp_captions:
                try:
                    google_captions = self.video_captions.get_captions_google(video_path)
                except Exception as e:
                    logging.error(f"Error getting captions: {e}")
            
            logging.info(f"get_captions: Captions: {nlp_captions}, {tp_captions}, {google_captions}")
            if nlp_captions:
                final_caption = nlp_captions
            elif tp_captions:
                final_caption = tp_captions
            elif google_captions:
                final_caption = google_captions
            else:
                final_caption = ""

            logging.info(f"get_captions: Captions: {final_caption}")
            if final_caption != "":
                self.db.insert_captions_cache(video_id, final_caption)
        
        # will be changed later to return only one caption
        return final_caption    
        # return {"nlp": nlp_captions, \
        #         "thirdparty": tp_captions, \
        #         "google": google_captions
        #         }
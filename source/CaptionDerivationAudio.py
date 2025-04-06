# Import necessary libraries
from readProperties import PropertiesReader
from DB import Database
from Logger import Logger 

# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CaptionDerivationAudio:
    """
    A class to derive captions from a given audio.
    """
    def __init__(self, kwargs=None):
        if 'logger' in kwargs:
            self.logger = kwargs['logger']
        else:
            self.loging = Logger()
            self.logger = self.loging.get_logger()
            
        if 'properties' in kwargs:
            self.properties = kwargs['properties']
        else:
            self.properties = PropertiesReader(kwargs={"logger":self.logger})
        self.db = Database(kwargs={"logger":self.logger})

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
        self.logger.info(f"get_captions: Getting captions from {audio_path} using {source}")
        
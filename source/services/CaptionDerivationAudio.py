# Import necessary libraries
from source.services.lib.readProperties import PropertiesReader
from source.services.lib.utils import Utils
from source.services.lib.DB import Database
from source.services.lib.Logger import Logger 
import os

import speech_recognition as sr
from pydub import AudioSegment

import wave
import json
from vosk import Model, KaldiRecognizer
import vosk

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

        if 'utils' in kwargs:
            self.utils = kwargs['utils']
        else:
            self.utils = Utils(kwargs={"logger":self.logger, "properties":self.properties})


        self.db = Database(kwargs={"logger":self.logger})
        self.download_directory = self.properties.get_property("folders", "audio_directory")
        if not self.download_directory:
            self.download_directory = os.path.join(os.getcwd(), 'audioFilesDirectory')
        if not os.path.exists(self.download_directory):
            os.makedirs(self.download_directory)


    def __str__(self):
        return f"{CaptionDerivationAudio.__name__}"
    
    def get_audio_id(self, audio_path):
        audio_id = audio_path.split("=")[-1]
        if audio_id is None:
            audio_id = audio_path.split("/")[-1]

        return audio_id

    def convert_to_wav(self, input_file):
        audio = AudioSegment.from_file(input_file)
        output_file = os.path.join(self.download_directory, self.get_audio_id(input_file))
        audio.export(output_file, format="wav")
        return output_file

    def get_captions_speechrecognition(self, audio_path):
        '''
        Get captions from an audio file using SpeechRecognition library.
        Args:
            audio_path (str): Path to the audio file.
            Returns:    
            str: Recognized text from the audio file.
        '''
        self.logger.info(f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
                        f"get_captions_speechrecognition: Processing audio file at {audio_path}"
                        f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
        if (not os.path.exists(audio_path)):
            raise Exception(f"get_captions_speechrecognition: Audio file not found at: ${audio_path}");

        recognizer = sr.Recognizer()
        if not audio_path.endswith(".wav"):
            audio_path = self.convert_to_wav(audio_path)

        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio)
        except Exception as e:
            self.logger.error(f"get_captions_speechrecognition: Error recognizing audio: {e}")
            return None
    
    def get_captions_whisperai(self, audio_path):
        '''
        Get captions from an audio file using WhisperAI.
        Args:
            audio_path (str): Path to the audio file.
            Returns:    
            str: Recognized text from the audio file.
        '''
        if (not os.path.exists(audio_path)):
            raise Exception(f"get_captions_whisperai: Audio file not found at: ${audio_path}");

        self.logger.info(f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
                        f"get_captions_whisperai: Processing audio file at {audio_path}"
                        f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
        # Ensure the whisper library is installed
        # You can install it using: pip install whisper
        if not os.path.exists(audio_path):
            self.logger.error(f"get_captions_whisperai: Audio file not found at: {audio_path}")
            return None
        if not os.path.exists(self.download_directory):
            self.logger.error(f"get_captions_whisperai: Download directory does not exist: {self.download_directory}")
            return None
        if not os.path.exists("whisper"):
            self.logger.error("get_captions_whisperai: WhisperAI library is not installed. Please install it using 'pip install whisper'.")
            return None
        if not os.path.exists("whisper/whisper"):
            self.logger.error("get_captions_whisperai: WhisperAI model is not available. Please download the model.")
            return None 
        try:
            import whisper
            model = whisper.load_model("base")
            result = model.transcribe(audio_path)
            return result["text"]   
        except ImportError:
            self.logger.error("get_captions_whisperai: WhisperAI library is not installed. Please install it using 'pip install whisper'.")
            return None
        
    def get_captions_vosk(self, audio_path, model_path="vosk-model-small-en-us-0.15"):
        '''
        Get captions from an audio file using Vosk.
        Args:
            audio_path (str): Path to the audio file.
            Returns:    
            str: Recognized text from the audio file.
        '''
        if (not os.path.exists(audio_path)):
            raise Exception(f"get_captions_vosk: Audio file not found at: ${audio_path}");
        self.logger.info(f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
                        f"get_captions_vosk: Processing audio file at {audio_path}"
                        f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
        # Ensure the vosk library is installed
        # You can install it using: pip install vosk
        if not os.path.exists("vosk"):
            self.logger.error("get_captions_vosk: Vosk library is not installed. Please install it using 'pip install vosk'.")
            return None
        if not os.path.exists(model_path):
            self.logger.error(f"get_captions_vosk: Model path does not exist: {model_path}")
            return None
        if not os.path.exists(audio_path):
            self.logger.error(f"get_captions_vosk: Audio file not found at: {audio_path}")
            return None
        # Check if the model path exists
        if not os.path.exists(model_path):
            self.logger.error(f"get_captions_vosk: Model path does not exist: {model_path}")
            return None
        # Check if the audio file exists
        if not os.path.exists(audio_path):
            self.logger.error(f"get_captions_vosk: Audio file not found at: {audio_path}")
            return None
        
        try:
            vosk = __import__('vosk')
            if not os.path.exists(model_path):
                self.logger.error(f"get_captions_vosk: Model path does not exist: {model_path}")
                return None
            if not os.path.exists(audio_path):
                self.logger.error(f"get_captions_vosk: Audio file not found at: {audio_path}")
                return None
            model = vosk.Model("model")
            recognizer = vosk.KaldiRecognizer(model, 16000)
            with open(audio_path, "rb") as f:
                while True:
                    data = f.read(4000)
                    if len(data) == 0:
                        break
                    if recognizer.AcceptWaveform(data):
                        result = recognizer.Result()
                        return result["text"]
            return None
        except ImportError:
            self.logger.error("get_captions_vosk: Vosk library is not installed. Please install it using 'pip install vosk'.")
            return None
        
    def get_captions(self, audio_path, method="speechrecognition"):
        """
        Get captions from an audio file using the specified method.
        Args:
            audio_path (str): Path to the audio file.
            method (str): Method to use for captioning. Options are "speechrecognition", "whisperai", "vosk".
        Returns:    
            str: Recognized text from the audio file.
        """
        if method == "speechrecognition":
            return self.get_captions_speechrecognition(audio_path)
        elif method == "whisperai":
            return self.get_captions_whisperai(audio_path)
        elif method == "vosk":
            return self.get_captions_vosk(audio_path)
        elif method == "all":
            captions_sr = self.get_captions_speechrecognition(audio_path)
            captions_wa = self.get_captions_whisperai(audio_path)
            captions_vosk = self.get_captions_vosk(audio_path)
            return {
                "speechrecognition": captions_sr,
                "whisperai": captions_wa,
                "vosk": captions_vosk
            }
        else:
            raise ValueError(f"Unknown method: {method}")
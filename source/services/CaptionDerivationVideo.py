# Import necessary libraries
import requests
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi

from source.services.lib.readProperties import PropertiesReader
from source.services.lib.utils import Utils
from source.services.lib.DB import Database
from source.services.lib.Logger import Logger 
from source.services.lib.Authorization import Authorization
from source.services.YouTubeDownloader import YouTubeDownloader
from source.services.CaptionDerivationAudio import CaptionDerivationAudio

class CaptionDerivationVideo:
    """
    A class to derive captions from a given video.
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
        self.authorization = Authorization(kwargs={"properties":self.properties, "logger":self.logger})
        self.caption_derivation_audio = CaptionDerivationAudio(kwargs={"properties":self.properties, "logger":self.logger, "utils":self.utils})
        self.youtubeDownload = YouTubeDownloader(kwargs={"properties":self.properties, "logger":self.logger, "utils":self.utils}) 
        
    def __str__(self):
        return f"{CaptionDerivationVideo.__name__}"
    
    def get_video_id(self, video_path):
        video_id = video_path.split("=")[-1]
        if video_id is None:
            video_id = video_path.split("/")[-1]

        return video_id
    
    def get_captions_yt_dlp(self, video_path):
        return ""    

    def get_captions_nlp(self, video_path):
        '''
            Get captions from the video using the Hugging Face pipeline.
            self need to be modified to download the video or audio from you tube 
            then pass that to self API
        '''
        try:
            # TODO: Download the video or audio from the URL
            self.logger.info(f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
                            f"get_captions_nlp: video_path: {video_path}"
                            f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
            nlp = pipeline("video-to-text", device=0)
            captions = nlp(video_path)
            return captions
        except Exception as e:
            self.logger.error(f"get_captions_nlp: Error getting captions: {e}")
            return None
    
    def get_captions_thirdparty(self, video_path):
        '''
            Get captions from the video using third party app
            https://github.com/jdepoix/youtube-transcript-api?utm_source=chatgpt.com
            https://pypi.org/project/youtube-transcript-api/
            Pass in the video ID, NOT the video URL. For a video with the URL https://www.youtube.com/watch?v=12345 the ID is 12345.
        '''
        try:
            video_id = self.get_video_id(video_path)
            self.logger.info(f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
                            f"get_captions_thirdparty: video_id: {video_id} from video_path: {video_path}"+ "\n"
                            f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")

            ytt_api = YouTubeTranscriptApi()

            # Use the static get_transcript method.
            # This method fetches the transcript in the specified languages (e.g., 'en' for English).
            # It returns a list of dictionaries, where each dictionary represents a segment of the transcript
            # (e.g., {'text': 'Hello world', 'start': 0.0, 'duration': 1.23}).
            # transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            
            # The result is already a list of dictionaries, no further formatting like to_raw_data() is needed
            # unless you specifically want to process the raw format from a Transcript object,
            # which is not the case when using get_transcript().
            # self.logger.info(f"get_captions_thirdparty: Successfully fetched captions for video_id: {video_id}")
            # self.logger.debug(f"get_captions_thirdparty: Captions data: {transcript_list}") # Can be verbose

            # Verify Deprecated
            # transcript = ytt_api.get_transcript(video_id)
            # self.logger.info(f"get_captions_thirdparty: transcript: {transcript}")
            # formatter = TextFormatter()
            # input_text = formatter.format_transcript(transcript)
            # self.logger.info(f"get_captions_thirdparty: input_text: {input_text}")

            # transcript_list = ytt_api.list_transcripts(video_path)
            # for transcript in transcript_list:
            #     transcript_fulltxt = transcript.translate('en').fetch()
            #  print(transcript_fulltxt)

            # Prints the list of languages in which transcripts are available
            # both (MANUALLY CREATED) and (GENERATED). Also prints the translation languages
            # transcript_list = ytt_api.list(video_id)
            # self.logger.info(f"get_captions_thirdparty: transcript_list: {transcript_list}")
            # # filter for manually created transcripts
            # try:
            #     manual_transcript = transcript_list.find_manually_created_transcript(['en'])
            #     self.logger.info(f"get_captions_thirdparty: manual_transcript: {manual_transcript}")
            #     manual_transcript = manual_transcript.fetch()
            # except Exception as e:
            #     self.logger.error(f"get_captions_thirdparty: manual_transcript Error: {e}")
            #     manual_transcript = ""

            # # or automatically generated ones
            # try:
            #     auto_transcript = transcript_list.find_generated_transcript(['en'])
            #     self.logger.info(f"get_captions_thirdparty: auto_transcript: {auto_transcript}")
            #     auto_transcript = auto_transcript.fetch()
            # except Exception as e:
            #     self.logger.error(f"get_captions_thirdparty: auto_transcript Error: {e}")
            #     auto_transcript = ""

            # self.logger.info(f"get_captions_thirdparty: manual_transcript: {manual_transcript}\nauto_transcript: {auto_transcript}")    

            # ChatGPT API to reconstruct a likely version of the intended grammar.
            captions = ytt_api.fetch(video_id)
            self.logger.info(f"get_captions_thirdparty: captions: {captions}\n \n")
            # {captions.to_raw_data()}

            # formatter = TextFormatter()
            # input_text = formatter.format_transcript(captions)
            # self.logger.info(f"get_captions_thirdparty: input_text: {input_text}")

            return captions  #.to_raw_data()   # return the value in dictionary format
        except Exception as e:
            self.logger.error(f"get_captions_thirdparty: Error getting captions: {e}")
            return None
        
    def get_captions_google(self, video_path, language_code="en"):
        '''
            Get captions from the video using Google API and OAuth 2.0
            https://developers.google.com/youtube/v3/docs/captions/list
            https://developers.google.com/youtube/v3/docs/captions/download
            https://developers.google.com/youtube/v3/guides/implementation/captions?utm_source=chatgpt.com
        '''
        try:
            self.logger.info(f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
                            f"get_captions_google: video_path: {video_path} \n"
                            f"get_captions_google: language_code: {language_code} \n"
                            f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
            video_id = self.get_video_id(video_path)
            credentials = self.authorization.get_session_credentials()
            if not credentials:
                return "No credentials found"

            authed_session = self.authorization.get_authorized_session(credentials)

            # 1. Get the list of available caption tracks
            list_url = f"https://www.googleapis.com/youtube/v3/captions?part=snippet&video_id={video_id}"
            self.logger.info(f"get_captions_google: Getting captions from: {list_url}")
            response = authed_session.get(list_url)
            self.logger.info(f"get_captions_google: Getting captions {list_url} response: {response}")
            
            response.raise_for_status()
            data = response.json()

            caption_tracks = data.get("items", [])
            self.logger.info(f"get_captions_google: caption_tracks: {caption_tracks}")
            
            if not caption_tracks:
                self.logger.info(f"get_captions_google: No captions found for video: {video_id}")
                return "No captions found"

            # 2. Find the caption track for the desired language (or default to the first one)
            target_track_id = None
            for track in caption_tracks:
                if track["snippet"]["language"] == language_code:
                    target_track_id = track["id"]
                    break
            self.logger.info(f"get_captions_google: target_track_id: {target_track_id}")

            if not target_track_id:
                self.logger.warning(f"No captions found for language code '{language_code}'. Using the first available track.")
                target_track_id = caption_tracks[0]["id"]

            # 3. Download the caption data
            download_url = f"https://www.googleapis.com/youtube/v3/captions/{target_track_id}?tfmt=srt"
            response = authed_session.get(download_url)
            response.raise_for_status()
            self.logger.info(f"get_captions_google: download_url {download_url} response: {response}")
            
            # 4. Return the caption text
            caption_text = response.text
            self.logger.info(f"get_captions_google: Captions {caption_text} found for video: {video_id}")
            return caption_text

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                self.logger.error(f"get_captions_google: Error getting captions: {e}. Check if the video is private or if the API key has the correct permissions.")
                return None
            elif e.response.status_code == 404:
                self.logger.error(f"get_captions_google: Error getting captions: {e}. No captions found for the video.")
                return None # "No captions found"
            else:
                self.logger.error(f"get_captions_google: Error getting captions: {e}")
                return None # "Error getting captions"
        except requests.RequestException as e:
            self.logger.error(f"get_captions_google: Error getting captions: {e}")
            return None # "Error getting captions"
        except Exception as e:
            self.logger.error(f"get_captions_google: Error getting captions: {e}")
            return None # "Error getting captions"
        
    def get_captions_downloadAudio(self, video_path):
        ''''
            Get captions from the video by downloading the audio first.
            self is a fallback method if the other methods fail.
            It uses YouTubeDownloader to download the audio and then uses 
            CaptionDerivationAudio to get the captions from the audio.
        '''
        try:
            video_url = video_path
            video_id = self.get_video_id(video_path)
            self.logger.info(f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
                            f"get_captions_downloadAudio: video_path: {video_path}\n{video_id}"
                            f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
            audio_download = None

            
            # Download Audio - first option
            if (not audio_download): # (len(audio_download) == 0):
                try:
                    audio_download = self.youtubeDownload.download_youtube_audio_pytube(video_path, video_id);
                    self.logger.info(f"get_captions_downloadAudio: audio_download from download_youtube_audio_pytube: {audio_download}")
                except Exception as e:
                    self.logger.error(f"get_captions_downloadAudio: Error downloading audio using download_youtube_audio_pytube: {e}");
                
            
            # Download Audio - second option
            if (not audio_download): #  (len(audio_download) == 0):
                try:
                    video_id = self.get_video_id(video_path)
                    audio_download = self.youtubeDownload.download_youtube_video_tubedl(video_path, video_id)
                    self.logger.info(f"get_captions_downloadAudio: audio_download from download_youtube_video_tubedl: {audio_download}")
                except Exception as e:
                    self.logger.error(f"get_captions_downloadAudio: Error downloading audio using download_youtube_video_tubedl: {e}");
                
            self.logger.info(f"get_captions_downloadAudio: audio_download: {audio_download}");

            # Get Captions
            captions = None
            if (audio_download): # (len(audio_download) > 0):
                try:
                    captions = self.caption_derivation_audio.get_captions_whisperai(audio_download);
                except Exception as e:
                    self.logger.error(f"get_captions_downloadAudio: Error getting captions using get_captions_whisperai: {e}")
            
                if (not captions):
                    try:
                        captions = self.caption_derivation_audio.get_captions_vosk(audio_download);
                        # getCaptionsAudioPathWhisperNode
                    except Exception as e:
                        self.logger.error(f"get_captions_downloadAudio: get_captions_downloadAudio: Error getting captions using get_captions_vosk: {e}")

                if (not captions):
                    try:
                        captions = self.caption_derivation_audio.get_captions_speechrecognition(audio_download)
                        # getCaptionsAudioPathWhisperNode
                    except Exception as e:
                        self.logger.error(f"get_captions_downloadAudio: get_captions_downloadAudio: Error getting captions using get_captions_speechrecognition: {e}")
                    
                # getCaptionsAudioPathVoskCLI  getCaptionsAudioPathVoskNode
                self.logger.info(f"get_captions_downloadAudio: get_captions_downloadAudio: captions: {captions}")
            else:
                self.logger.error(f"get_captions_downloadAudio: get_captions_downloadAudio: Audio was not downloaded: {audio_download}")
            

            return captions;  # Returns in dictionary format
        except Exception as e:
            self.logger.error(f"get_captions_downloadAudio: get_captions_downloadAudio: Error getting captions: {e}")
            return None
# Import necessary libraries
import os
import requests
import yt_dlp
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, YouTubeRequestFailed, IpBlocked, RequestBlocked, TranscriptsDisabled
# CouldNotRetrieveTranscript

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
        self.captionDerivationAudio = CaptionDerivationAudio(kwargs={"properties":self.properties, "logger":self.logger, "utils":self.utils})
        self.youtubeDownload = YouTubeDownloader(kwargs={"properties":self.properties, "logger":self.logger, "utils":self.utils}) 
        self.captions_directory = self.properties.get_property("folders", "captions_directory")
        if not self.captions_directory:
            self.captions_directory = os.path.join(os.getcwd(), 'captionsDirectory')
        if not os.path.exists(self.captions_directory):
            os.makedirs(self.captions_directory)
        self.logger.info(f"Download directory set to: {self.captions_directory}")


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
            # nlp = pipeline("video-to-text", device=0)
            # captions = nlp(video_path)
            # return captions
            return None
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
            lang_code = 'en'
            # Use the static get_transcript method.
            # This method fetches the transcript in the specified languages (e.g., 'en' for English).
            # It returns a list of dictionaries, where each dictionary represents a segment of the transcript
            # (e.g., {'text': 'Hello world', 'start': 0.0, 'duration': 1.23}).
            captions_orig = ytt_api.fetch(video_id)  # Pre-fetch to check availability
            # captions_orig = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang_code])
            
            # The result is already a list of dictionaries, no further formatting like to_raw_data() is needed
            # unless you specifically want to process the raw format from a Transcript object,
            # which is not the case when using get_transcript().
            self.logger.info(f"get_captions_thirdparty: Successfully fetched captions for video_id: {video_id}")
            self.logger.debug(f"get_captions_thirdparty: Captions data: {captions_orig}") # Can be verbose
            
            # self.utils.saveFile(
            #     file_name=f"{video_id}_orig.json",
            #     textToBeSaved=captions_orig,
            #     directory=self.captions_directory,
            #     file_format="json"
            # )
            captions = captions_orig.to_raw_data()  # This will return the captions in a raw dictionary format
            
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
            if not captions:
                transcript_list = ytt_api.list(video_id)
                self.logger.debug(f"get_captions_thirdparty: transcript_list: {transcript_list}")
                # filter for manually created transcripts
                try:
                    manual_transcript = transcript_list.find_manually_created_transcript([lang_code])
                    self.logger.info(f"get_captions_thirdparty: manual_transcript: {manual_transcript}")
                    manual_transcript = manual_transcript.fetch()
                except Exception as e:
                    self.logger.error(f"get_captions_thirdparty: manual_transcript Error: {e}")
                    manual_transcript = None

                # # or automatically generated ones
                try:
                    auto_transcript = transcript_list.find_generated_transcript([lang_code])
                    self.logger.info(f"get_captions_thirdparty: auto_transcript: {auto_transcript}")
                    auto_transcript = auto_transcript.fetch()
                except Exception as e:
                    self.logger.error(f"get_captions_thirdparty: auto_transcript Error: {e}")
                    auto_transcript = None

                self.logger.info(f"get_captions_thirdparty: manual_transcript: {manual_transcript}\nauto_transcript: {auto_transcript}")    
                
                captions = manual_transcript if manual_transcript else auto_transcript
                
                # ChatGPT API to reconstruct a likely version of the intended grammar.
                # captions = ytt_api.fetch(video_id)
                # self.logger.info(f"get_captions_thirdparty: captions: {captions}\n \n")
                # {captions.to_raw_data()}

                # formatter = TextFormatter()
                # input_text = formatter.format_transcript(captions)
                # self.logger.info(f"get_captions_thirdparty: input_text: {input_text}")

            return captions  #.to_raw_data()   # return the value in dictionary format
        except YouTubeRequestFailed as e:
            self.logger.error(f"get_captions_thirdparty: YouTube request failed: {e}")
            return None
        
        except NoTranscriptFound as e:
            self.logger.error(f"No transcript found for this video : {e}")
            # return None
            try:
                transcript_list_obj = YouTubeTranscriptApi.list_transcripts(video_id)
                found_transcript_data = None
                # Check manually created transcripts first
                for lang_code in transcript_list_obj._manually_created_transcripts:
                    try:
                        transcript = transcript_list_obj.find_manually_created_transcript([lang_code])
                        found_transcript_data = transcript.fetch() # Returns List[Dict]
                        self.logger.info(f"get_captions_thirdparty: Found manually created transcript in '{lang_code}' for {video_id}.")
                        break
                    except Exception as e_manual_fetch:
                        self.logger.error(f"get_captions_thirdparty: Error fetching manual transcript for lang '{lang_code}', video_id {video_id}: {e_manual_fetch}")
                
                if not found_transcript_data:
                    # Then check auto-generated transcripts
                    for lang_code in transcript_list_obj._generated_transcripts:
                        try:
                            transcript = transcript_list_obj.find_generated_transcript([lang_code])
                            found_transcript_data = transcript.fetch() # Returns List[Dict]
                            self.logger.info(f"get_captions_thirdparty: Found auto-generated transcript in '{lang_code}' for {video_id}.")
                            break
                        except Exception as e_generated_fetch:
                            self.logger.error(f"get_captions_thirdparty: Error fetching auto-generated transcript for lang '{lang_code}', video_id {video_id}: {e_generated_fetch}")
                
                if found_transcript_data:
                    return found_transcript_data
                else:
                    self.logger.error(f"get_captions_thirdparty: No transcripts found for {video_id} after checking all available.")
                    return None
            except Exception as e_fallback:
                self.logger.error(f"get_captions_thirdparty: Error during fallback transcript search for {video_id}: {e_fallback}", exc_info=True)
                return None
    
        except IpBlocked as e: 
            self.logger.error(f"get_captions_thirdparty: YouTube request IP blocked: {e}")
            return None
        
        except RequestBlocked as e:
            self.logger.error(f"get_captions_thirdparty: YouTube request blocked: {e}")
            return None

        except TranscriptsDisabled as e:
            self.logger.error(f"get_captions_thirdparty: YouTube Transcript disabled: {e}")
            return None
        
        # except CouldNotRetrieveTranscript as e:
        #     self.logger.error(f"get_captions_thirdparty: Error retrieving transcript: {e}")
        #     return None
        
        except Exception as e:
            self.logger.error(f"get_captions_thirdparty: Error getting captions: {e}")
            return None
    
    def get_captions_downloadCaptions(self, video_url, video_id=None):
        """Downloads a YouTube video.
        Args:
            video_url: The URL of the YouTube video.
            output_path: The directory to save the downloaded video file.
        """
        try:
            output_dir = self.captions_directory
            self.logger.info(f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
                            f"get_captions_downloadCaptions: output_dir - {output_dir}"
                            f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
        
            video_id = self.get_video_id(video_url)
            # self.video_captions.get_video_id(video_url)
            # ydl.getVideoID(video_url)
            # Customize the filename (optional)
            # filename = f"{yt.title}.mp3"  # Or any other audio format
            file_name = f"{video_id}.txt"  # Customize the filename as needed
            output_file_path = os.path.join(output_dir, file_name)
            self.logger.info(f"get_captions_downloadCaptions: videoUrl - {video_url} \n" +
                            f"video_id - {video_id} \n" + 
                            f"output_file_path: {output_file_path}")
            
            # Verify if file is already available then use it
            if (os.path.exists(output_file_path)):
                self.logger.info("get_captions_downloadCaptions: MP3 Audio already available`")
                return output_file_path

            ydl_opts = {
                "skip_download": True,
                "writesubtitles": True,
                "subtitleslangs": ["all", "-live_chat"],
                # Looks like formats available are vtt, ttml, srv3, srv2, srv1, json3
                "subtitlesformat": "json3",
                # You can skip the following option
                "sleep_interval_subtitles": 1,
            }
            
            # ydl = youtube_dl.YoutubeDL(ydl_opts)
            ydl = yt_dlp.YoutubeDL(ydl_opts)
            ydl.download([video_id])

            return output_file_path

        except yt_dlp.utils.DownloadError as de:
            self.logger.error(f"get_captions_downloadCaptions: A yt-dlp DownloadError occurred for {video_url}: {de}")
            return None
        except Exception as e:
            self.logger.error(f"get_captions_downloadCaptions: An error occurred: {e}")
            return None
        
    def get_captions_google(self, video_path, language_code="en"):
        '''
            Get captions from the video using Google API and OAuth 2.0
            https://developers.google.com/youtube/v3/docs/captions/list
            https://developers.google.com/youtube/v3/docs/captions/download
            https://developers.google.com/youtube/v3/guides/implementation/captions?utm_source=chatgpt.com

            download is allowed only for content owner. Others cannot use download to download captions
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
                # self.logger.warning(f"No captions found for language code '{language_code}'. Using the first available track.")
                # target_track_id = caption_tracks[0]["id"]
                if caption_tracks: # If there are tracks, but not in the desired language
                    self.logger.warning(f"No captions found for language '{language_code}'. Using the first available track: {caption_tracks[0]['id']} ({caption_tracks[0]['snippet']['language']}).")
                    target_track_id = caption_tracks[0]["id"]
                    target_track_snippet_status = caption_tracks[0]["snippet"]["status"]
                else:
                    # This case should have been caught by "No captions found" earlier, but as a safeguard:
                    self.logger.info(f"get_captions_google: No caption tracks found at all for video: {video_id}")
                    return "No captions found"

            # # 2.1 check privacy status
            # self.logger.info(f"get_captions_google: snippet status {caption_tracks[0]["snippet"]["status"]}\n"
            #                 f"get_captions_google: target_track_id: {caption_tracks[0]["status"]["privacyStatus"]}")
            # if caption_tracks[0]["snippet"]["status"] != "public": 
            #     self.logger.error(f"get_captions_google: Captions for video {video_id} are not public."
            #                     f"Status: {caption_tracks[0]['snippet']['status']}")
            #     return None
            
            # 2.1 Check the status of the selected caption track.
            # Video privacy (public/private/unlisted) should be checked via the videos().list API if needed,
            # as the caption resource itself doesn't directly carry the video's privacyStatus.
            self.logger.info(f"get_captions_google: Selected caption track ID '{target_track_id}' has status: '{target_track_snippet_status}'")
            if target_track_snippet_status != "serving":
                self.logger.error(f"get_captions_google: Caption track '{target_track_id}' for video {video_id} is not in 'serving' state. "
                                f"Actual status: '{target_track_snippet_status}'. Cannot download.")
                return None
            
            # 3. Download the caption data
            download_url = f"https://www.googleapis.com/youtube/v3/captions/{target_track_id}?tfmt=srt"
            self.logger.info(f"get_captions_google: Attempting to download captions from: {download_url}")
            response = authed_session.get(download_url)
            response.raise_for_status()
            self.logger.info(f"get_captions_google: download_url {download_url} response: {response}")
            
            # 4. Return the caption text
            caption_text = response.text
            self.logger.info(f"get_captions_google: Captions {caption_text} found for video: {video_id}")
            return caption_text

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                error_message = (
                    f"get_captions_google: 403 Forbidden error for video_id '{video_id}' "
                    f"when trying to download caption track_id '{target_track_id if 'target_track_id' in locals() else 'unknown'}'. "
                    f"Original error: {e}. "
                    "Check if: 1. The video is private/restricted. 2. The specific caption track is not downloadable. "
                    "3. The authenticated user has necessary permissions (OAuth scopes granted). "
                    "4. The YouTube Data API v3 is enabled in the Google Cloud project."
                )
                self.logger.error(error_message)
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
    
    def get_captions_google_server_cred(self, video_path, language_code="en"):
        try:
            self.logger.info(f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
                            f"get_captions_google_server_cred: video_path: {video_path} \n"
                            f"get_captions_google_server_cred: language_code: {language_code} \n"
                            f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
            youtube_service = self.authorization.get_server_authenticated_service()
            video_id = self.get_video_id(video_path)

            # Retrieve list of caption tracks for the video
            caption_tracks = youtube_service.captions().list(
                part='snippet',
                videoId=video_id
            ).execute()

            captions = []
            for track in caption_tracks.get('items', []):
                caption_id = track['id']
                language = track['snippet']['language']
                name = track['snippet'].get('name', '') # Optional: caption track name
                self.logger.info(f"Caption Track ID: {caption_id}, Language: {language}")

                # Download the caption track
                caption_data = youtube_service.captions().download(
                    id=caption_id,
                    tfmt='srt'  # You can choose other formats like 'sbv', 'ttml', 'vtt'
                ).execute()
                captions.append({
                    'caption_id': caption_id,
                    'language': language,
                    'name': name,
                    'data': caption_data
                })
            return caption_data

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                error_message = (
                    f"get_captions_google: 403 Forbidden error for video_id '{video_id}' "
                    f"when trying to download caption track_id '{caption_id if 'target_track_id' in locals() else 'unknown'}'. "
                    f"Original error: {e}. "
                    "Check if: 1. The video is private/restricted. 2. The specific caption track is not downloadable. "
                    "3. The authenticated user has necessary permissions (OAuth scopes granted). "
                    "4. The YouTube Data API v3 is enabled in the Google Cloud project."
                )
                self.logger.error(error_message)
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
                    captions = self.captionDerivationAudio.get_captions_whisperai(audio_download);
                except Exception as e:
                    self.logger.error(f"get_captions_downloadAudio: Error getting captions using get_captions_whisperai: {e}")
            
                if (not captions):
                    try:
                        captions = self.captionDerivationAudio.get_captions_vosk(audio_download);
                        # getCaptionsAudioPathWhisperNode
                    except Exception as e:
                        self.logger.error(f"get_captions_downloadAudio: get_captions_downloadAudio: Error getting captions using get_captions_vosk: {e}")

                if (not captions):
                    try:
                        captions = self.captionDerivationAudio.get_captions_speechrecognition(audio_download)
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
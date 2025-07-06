# Import necessary libraries
from source.services.lib.readProperties import PropertiesReader
from source.services.lib.DB import Database
from source.services.lib.Logger import Logger 
from source.services.lib.utils import Utils

from pytube import YouTube
from pytube import exceptions as pytube_exceptions
import urllib.error


import os
# from __future__ import unicode_literals
# import youtube_dl
import yt_dlp

# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class YouTubeDownloader:
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
        self.download_directory = self.properties.get_property("folders", "audio_directory")
        if not self.download_directory:
            self.download_directory = os.path.join(os.getcwd(), 'audioFilesDirectory')
        if not os.path.exists(self.download_directory):
            os.makedirs(self.download_directory)
        self.logger.info(f"Download directory set to: {self.download_directory}")

    def __str__(self):
        return f"{YouTubeDownloader.__name__}"
    
    def download_youtube_audio_pytube(self, video_url, video_id=None):
        """Downloads audio from a YouTube video.
        Args:
            video_url: The URL of the YouTube video.
            output_path: The directory to save the downloaded audio file.
        """
        try:
            output_dir = self.download_directory
            self.logger.info(f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
                            f"download_youtube_audio_pytube: output_dir - {output_dir}"
                            f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
            yt = YouTube(video_url)

            if video_id is None:
                video_id = video_url.split("=")[-1]
                if video_id is None:
                    video_id = video_url.split("/")[-1]
            # self.video_captions.get_video_id(video_url)
            # Customize the filename (optional)
            # filename = f"{yt.title}.mp3"  # Or any other audio format
            file_name = f"{video_id}.mp3"  # Customize the filename as needed
            output_file_path = os.path.join(output_dir, file_name)
            self.logger.info(f"download_youtube_audio_pytube: videoUrl - {video_url} \n" +
                            f"video_id - {video_id} \n" + 
                            f"output_file_path: {output_file_path}")
            
            # Verify if file is already available then use it
            if (os.path.exists(output_file_path)):
                self.logger.info("download_youtube_audio_pytube: MP3 Audio already available`")
                return output_file_path

            video_info = yt.metadata
            self.logger.info(f"download_youtube_audio_pytube: Video Info: {video_info}")

            stream = yt.streams.filter(only_audio=True).first()
            if not stream:
                self.logger.error("download_youtube_audio_pytube: No audio stream found for the video.")
                return
            
            # Download the audio
            stream.download(output_path=output_dir, filename=file_name)
            self.logger.info(f"download_youtube_audio_pytube: Audio downloaded successfully to: {output_file_path}")
            return output_file_path 
        
        except pytube_exceptions.PytubeError as pe:
            self.logger.error(f"download_youtube_audio_pytube: A Pytube error occurred for {video_url}: {pe}",  exc_info=True)
            return None
        except urllib.error.HTTPError as he:
            self.logger.error(f"download_youtube_audio_pytube: An HTTPError occurred for {video_url} (likely from pytube internals): {he}", exc_info=True)
            return None
        except Exception as e:
            self.logger.error(f"download_youtube_audio_pytube: An error occurred: {e}")   
            return None 

    def download_youtube_video_tubedl(self, video_url, video_id=None):
        """Downloads a YouTube video.
        Args:
            video_url: The URL of the YouTube video.
            output_path: The directory to save the downloaded video file.
        """
        try:
            output_dir = self.download_directory
            self.logger.info(f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
                            f"download_youtube_video_tubedl: output_dir - {output_dir}"
                            f"\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
        
            if video_id is None:
                video_id = video_url.split("=")[-1]
                if video_id is None:
                    video_id = video_url.split("/")[-1]
            # self.video_captions.get_video_id(video_url)
            # ydl.getVideoID(video_url)
            # Customize the filename (optional)
            # filename = f"{yt.title}.mp3"  # Or any other audio format
            file_name = f"{video_id}.mp3"  # Customize the filename as needed
            output_file_path = os.path.join(output_dir, file_name)
            self.logger.info(f"download_youtube_video_tubedl: videoUrl - {video_url} \n" +
                            f"video_id - {video_id} \n" + 
                            f"output_file_path: {output_file_path}")
            
            # Verify if file is already available then use it
            if (os.path.exists(output_file_path)):
                self.logger.info("download_youtube_video_tubedl: MP3 Audio already available`")
                return output_file_path

            ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': output_file_path,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
            
            ffmpeg_executable_path = self.properties.get_property("tools", "ffmpeg_path")
            if ffmpeg_executable_path and os.path.exists(os.path.join(ffmpeg_executable_path, 'ffmpeg')): # Check if it's a directory
                ydl_opts['ffmpeg_location'] = os.path.join(ffmpeg_executable_path, 'ffmpeg') # Point to ffmpeg executable
            elif ffmpeg_executable_path and os.path.exists(ffmpeg_executable_path): # Check if it's the executable itself
                ydl_opts['ffmpeg_location'] = ffmpeg_executable_path
            

            # ydl = youtube_dl.YoutubeDL(ydl_opts)
            ydl = yt_dlp.YoutubeDL(ydl_opts)
            ydl.download([video_url])

            return output_file_path

        except yt_dlp.utils.DownloadError as de:
            self.logger.error(f"download_youtube_video_tubedl: A yt-dlp DownloadError occurred for {video_url}: {de}")
            return None
        except Exception as e:
            self.logger.error(f"download_youtube_video_tubedl: An error occurred: {e}")
            return None
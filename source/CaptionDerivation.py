# Import necessary libraries
from readProperties import PropertiesReader
from CaptionDerivationVideo import CaptionDerivationVideo
from CaptionDerivationAudio import CaptionDerivationAudio
from DB import Database
from Logger import Logger 
from utils import SourceTypes, CaptionSources
import wikipedia
from bs4 import *
import requests
from flask import jsonify
# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CaptionDerivation:
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
        self.db = Database(kwargs={"logger":self.logger})
        self.video_captions = CaptionDerivationVideo(kwargs={"properties":self.properties, "logger":self.logger})
        self.audio_captions = CaptionDerivationAudio(kwargs={"properties":self.properties, "logger":self.logger})
    
    def __str__(self):
        return f"{CaptionDerivation.__name__}"
    
    def get_captions(self, source_path, source_type=SourceTypes.YOUTUBE, caption_source=CaptionSources.ALL):
        '''
            Get captions from the audio or video based on soruce_type.
        '''
        self.logger.info(f"get_captions: Getting captions from {source_path} using {caption_source}")
        if source_type == SourceTypes.YOUTUBE or source_type == SourceTypes.VIDEO:
            return self.get_video_captions(source_path, caption_source)
        if source_type == SourceTypes.PODCAST or source_type == SourceTypes.AUDIO:
            return self.get_audio_captions(source_path, caption_source)
        
    def get_video_captions(self, video_path, caption_source=CaptionSources.ALL):
        '''
            Get captions from the video.
        '''
        self.logger.info(f"get_video_captions: Getting captions from {video_path} using {caption_source}")

        video_id = self.video_captions.get_video_id(video_path)

        # Temporarily disable cache
        # cached_result = self.db.get_captions_cached_result(video_id)
        # if cached_result:
        #     return cached_result

        nlp_captions = None
        tp_captions = None
        google_captions = None
        final_caption = ""

        if caption_source == CaptionSources.NLP:
            nlp_captions = self.video_captions.get_captions_nlp(video_path)
            if nlp_captions:
                self.db.insert_captions_cache(video_id, nlp_captions)

            return nlp_captions
        elif caption_source == CaptionSources.THIRD_PARTY:
            tp_captions = self.video_captions.get_captions_thirdparty(video_path)
            final_tp_captions = ""
            for data in tp_captions:
                final_tp_captions += data.get("text", "")
                final_tp_captions += ""
            tp_captions = final_tp_captions
            
            # Temp Comment
            # if tp_captions:
            #     self.db.insert_captions_cache(video_id, tp_captions)
            
            return tp_captions  
        elif caption_source == CaptionSources.GOOGLE:
            google_captions = self.video_captions.get_captions_google(video_path)

            # Temp Comment
            # if google_captions:
            #     self.db.insert_captions_cache(video_id, google_captions)

            return google_captions
        else:
            try:
                nlp_captions = self.video_captions.get_captions_nlp(video_path)
            except Exception as e:
                self.logger.error(f"Error getting captions: {e}")
            
            if not nlp_captions:
                try:
                    tp_captions = self.video_captions.get_captions_thirdparty(video_path)
                    # tp_captions = [{'text': 'this is ritesh srinivasana and welcome', 'start': 0.179, 'duration': 4.681}, 
                    #                {'text': "to my channel in this video let's look", 'start': 2.22, 'duration': 5.76}]
            
                    final_tp_captions = ""
                    for data in tp_captions:
                        final_tp_captions += data.get("text", "")
                        final_tp_captions += ""
                    tp_captions = final_tp_captions
                except Exception as e:
                    self.logger.error(f"get_video_captions: Error getting captions: {e}")
                
            # if not tp_captions:
            try:
                google_captions = self.video_captions.get_captions_google(video_path)
            except Exception as e:
                self.logger.error(f"Error getting captions: {e}")
        
            self.logger.info(f"get_video_captions: Captions: {nlp_captions}, {tp_captions}, {google_captions}")
            if nlp_captions:
                final_caption = nlp_captions
            elif tp_captions:
                final_caption = tp_captions
            elif google_captions:
                final_caption = google_captions
            else:
                final_caption = ""

            self.logger.info(f"get_video_captions: Captions: {final_caption}")
            # if final_caption != "":
            #     self.db.insert_captions_cache(video_id, final_caption)
        
        # will be changed later to return only one caption
        return final_caption
        # return {"nlp": nlp_captions, \
        #         "thirdparty": tp_captions, \
        #         "google": google_captions
        #         }

    def get_audio_captions(self, audio_path, caption_source=CaptionSources.ALL):
        '''
            Get captions from the audio.
        '''
        self.logger.info(f"get_audio_captions: Getting captions from {audio_path} using {caption_source}")

        audio_id = self.audio_captions.get_audio_id(audio_path)

        return ""
    
    def get_wiki_captions(self, source_path):
        """
            Get captions from the wiki url.
        """
        self.logger.info(f"get_wiki_captions: source_path: {source_path}")
        if source_path.startswith("https://en.wikipedia.org/wiki/"):
            return self.get_wiki_url_text(source_path)
        else:
            return self.get_wiki_search_text(source_path)
            
    def get_wiki_search_text(self, wiki_url):
        """
            Get Text from wiki url
        """
        try:
            self.logger.info(f"get_wiki_search_text: wiki_url: {wiki_url}")
            wikisearch = wikipedia.page(wiki_url, auto_suggest=True)
            wikiContent = wikisearch.content
            wikiSummary = wikisearch.summary
            wikiImages = wikisearch.images
            wikiLinks = wikisearch.links
            wikiUrls = wikisearch.url
            wikiCategories = wikisearch.categories
            wikiReferences = wikisearch.references
            
            self.logger.info(f"get_wiki_search_text: wikisearch: {wikisearch} \n"
                            f"wikiContent: {wikiContent} \n"
                            f"get_wiki_search_text: wikiSummary: {wikiSummary} \n"
                            f"get_wiki_url_text: wikiImages: {wikiImages} \n"
                            f"get_wiki_url_text: wikiLinks: {wikiLinks} \n"
                            f"get_wiki_url_text: wikiUrls: {wikiUrls} \n"
                            f"get_wiki_url_text: wikiCategories: {wikiCategories} \n"
                            f"get_wiki_url_text: wikiReferences: {wikiReferences} \n")
            # nlp = en_core_web_sm.load()
            # doc = nlp(wikicontent)
            # self.logger.info(f"get_wiki_url_text: doc: {doc}")
            
            return wikiContent
            # return {"wikiContent": wikiContent, "wikiSummary": wikiSummary, "wikiImages": wikiImages, 
            #         "wikiLinks": wikiLinks, "wikiUrls": wikiUrls, "wikiCategories": wikiCategories, 
            #         "wikiReferences": wikiReferences}
        except wikipedia.exceptions.PageError:
            self.logger.info(f"get_wiki_search_text: Error: Could not find the Wikipedia page for 'chatgp'.")
            return None
        except wikipedia.exceptions.DisambiguationError as e:
            self.logger.info(f"get_wiki_search_text: Error: Ambiguous page title. Did you mean any of these? {e.options}")
            return None
        except Exception as e:
            self.logger.info(f"get_wiki_search_text: An error occurred: {e}")
            return None
        
    def get_wiki_url_text(self, wiki_url):
        """
            Get Text from wiki url
        """
        try:
            self.logger.info(f"get_wiki_url_text: wiki_url: {wiki_url}")
            # Fetch URL Content
            r = requests.get(wiki_url)
            
            # Get body content
            soup = BeautifulSoup(r.text,'html.parser')
            self.logger.info(f"get_wiki_url_text: r: {r} \n\n")
            # soup: {soup} 

            # Initialize variable
            paragraphs = []
            wikiImages = []
            wikiLinks = []
            heading = []
            wikiContent = []
            
            soup_body = soup.select('body')[0]
            main_content = soup.find(id="mw-content-text")
            # self.logger.info(f"get_wiki_url_text: main_content: {main_content}")
            # soup_body.find_all(): {soup_body.find_all()}\n

            text_content = ""
            if main_content:
                paragraphs = main_content.find_all("p")
                text_content = "\n".join([p.text for p in paragraphs])
            self.logger.info(f"get_wiki_url_text: text_content: {text_content}")

            # Iterate through all tags
            # for tag in soup_body.find_all():
                
            #     # Check each tag name
            #     # For Paragraph use p tag
            #     if tag.name=="p":
                
            #         # use text for fetch the content inside p tag
            #         paragraphs.append(tag.text)
                    
            #     # For Image use img tag
            #     elif tag.name=="img":
                
            #         # Add url and Image source URL
            #         wikiImages.append(wiki_url+tag['src'])
                    
            #     # For Anchor use a tag
            #     elif tag.name=="a":
                
            #         # convert into string and then check href
            #         # available in tag or not
            #         if "href" in str(tag):
                    
            #         # In href, there might be possible url is not there
            #         # if url is not there
            #             if "https://en.wikipedia.org/w/" not in str(tag['href']):
            #                 wikiLinks.append(wiki_url+tag['href'])
            #             else:
            #                 wikiLinks.append(tag['href'])
                            
            #     # Similarly check for heading 
            #     # Six types of heading are there (H1, H2, H3, H4, H5, H6)
            #     # check each tag and fetch text
            #     elif "h" in tag.name:
            #         if "h1"==tag.name:
            #             heading.append(tag.text)
            #         elif "h2"==tag.name:
            #             heading.append(tag.text)
            #         elif "h3"==tag.name:
            #             heading.append(tag.text)
            #         elif "h4"==tag.name:
            #             heading.append(tag.text)
            #         elif "h5"==tag.name:
            #             heading.append(tag.text)
            #         else:
            #             heading.append(tag.text)
                        
            #     # Remain content will store here
            #     else:
            #         wikiContent.append(tag.text)
                    
            # self.logger.info(f"get_wiki_url_text: paragraphs: {paragraphs} \n"
            #                 f"wikiImages: {wikiImages} \n"
            #                 f"wikiLinks: {wikiLinks} \n"
            #                 f"heading: {heading} \n"
            #                 f"wikiContent: {wikiContent} \n")
            # return jsonify({wikiContent, paragraphs, wikiImages, wikiLinks, heading})
            # return {"wikiContent": text_content, "wikiImages": wikiImages, 
            #         "wikiLinks": wikiLinks, "paragraphs": paragraphs, "heading": heading, 
            #         "wikiReferences": [], "wikiCategories": [], "wikiSummary": "", "wikiUrls": []} # wikiContent
            return text_content
        except requests.exceptions.RequestException as e:
            self.logger.info(f"get_wiki_url_text: Error: {e}")
        except Exception as e:
            self.logger.info(f"get_wiki_url_text: An error occurred: {e}")
            return None
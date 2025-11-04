# Import necessary libraries
from source.services.CaptionDerivationVideo import CaptionDerivationVideo
from source.services.CaptionDerivationAudio import CaptionDerivationAudio
from source.services.lib.readProperties import PropertiesReader
from source.services.lib.DB import Database
from source.services.lib.Logger import Logger 
from source.services.lib.utils import Utils, SourceTypes, CaptionSources

import os
import wikipedia
from bs4 import *
import requests
from flask import jsonify
from readability import Document # <-- Import readability

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
        
        if 'utils' in kwargs:
            self.utils = kwargs['utils']
        else:
            self.utils = Utils(kwargs={"logger":self.logger, "properties":self.properties})

        self.db = Database(kwargs={"logger":self.logger})
        self.video_captions = CaptionDerivationVideo(kwargs={"properties":self.properties, "logger":self.logger})
        self.audio_captions = CaptionDerivationAudio(kwargs={"properties":self.properties, "logger":self.logger})
        self.captions_directory = self.properties.get_property("folders", "captions_directory")
        if not self.captions_directory:
            self.captions_directory = os.path.join(os.getcwd(), 'captionsDirectory')
        if not os.path.exists(self.captions_directory):
            os.makedirs(self.captions_directory)


    def __str__(self):
        return f"{CaptionDerivation.__name__}"
    
    def get_captions(self, source_path, source_type=SourceTypes.YOUTUBE, caption_source=CaptionSources.ALL):
        '''
            Get captions from the audio or video based on soruce_type.
        '''
        self.logger.info(f"\n*********************************************************\n"
                        f"get_captions: Getting captions from {source_path} using {caption_source}"
                        f"\n*********************************************************\n")
        if source_type == SourceTypes.YOUTUBE or source_type == SourceTypes.VIDEO:
            return self.get_video_captions(source_path, caption_source)
        if source_type == SourceTypes.PODCAST or source_type == SourceTypes.AUDIO:
            return self.get_audio_captions(source_path, caption_source)
        if source_type == SourceTypes.WIKI:
            return self.get_wiki_captions(source_path)
        
    def get_video_captions(self, video_path, caption_source=CaptionSources.ALL):
        '''
            Get captions from the video.
        '''
        self.logger.info(f"\n*********************************************************\n"
                        f"get_video_captions: Getting captions from {video_path} using {caption_source}"
                        f"\n*********************************************************\n")

        video_id = self.video_captions.get_video_id(video_path)
        file_path = self.captions_directory

        # Check If captions are already available
        file_content = self.utils.getFile(file_path, video_id);
        if (not file_content.startswith("Error")):
            return file_content
            
        # Temporarily disable cache
        # cached_result = self.db.get_captions_cached_result(video_id)
        # if cached_result:
        #     return cached_result

        nlp_captions = None
        tp_captions = None
        google_captions = None
        downloaded_captions = None
        final_captions = ""

        if caption_source == CaptionSources.NLP:
            nlp_captions = self.video_captions.get_captions_nlp(video_path)
            # if nlp_captions:
            #     self.db.insert_captions_cache(video_id, nlp_captions)

            final_captions = nlp_captions
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
            
            final_captions = tp_captions  
        elif caption_source == CaptionSources.GOOGLE:
            # google_captions = self.video_captions.get_captions_google(video_path)
            google_captions = self.video_captions.get_captions_downloadAudio(video_path)
        
            # Temp Comment
            # if google_captions:
            #     self.db.insert_captions_cache(video_id, google_captions)

            final_captions = google_captions
        elif caption_source == CaptionSources.DOWNLOAD:
            downloaded_captions = self.video_captions.get_captions_downloadCaptions(video_path)

            if not downloaded_captions:
                downloaded_captions = self.video_captions.get_captions_downloadAudio(video_path)

            # Temp Comment
            # if google_captions:
            #     self.db.insert_captions_cache(video_id, google_captions)

            final_captions = downloaded_captions
        else:
            try:
                nlp_captions = self.video_captions.get_captions_nlp(video_path)
            except Exception as e:
                self.logger.error(f"Error getting captions get_captions_nlp: {e}")
            
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
                    self.logger.error(f"get_video_captions: Error getting captions get_captions_thirdparty: {e}")
                
            # if not tp_captions:
            # This is allowed only for content owners
            # try:
            #     google_captions = self.video_captions.get_captions_google(video_path)
            # except Exception as e:
            #     self.logger.error(f"get_video_captions: Error getting captions: {e}")

            if not tp_captions:
                try:
                    downloaded_captions = self.video_captions.get_captions_downloadCaptions(video_path)
                except Exception as e:
                    self.logger.error(f"get_video_captions: Error getting captions get_captions_downloadCaptions: {e}")
            
            if not downloaded_captions:
                try:
                    downloaded_captions = self.video_captions.get_captions_downloadAudio(video_path)
                except Exception as e:
                    self.logger.error(f"get_video_captions: Error getting captions get_captions_downloadAudio: {e}")

            self.logger.info(f"get_video_captions: Captions: {nlp_captions}, {tp_captions}, {google_captions}, {downloaded_captions}")
            if nlp_captions:
                final_captions = nlp_captions
            elif tp_captions:
                final_captions = tp_captions
            elif google_captions:
                final_captions = google_captions
            elif downloaded_captions:
                final_captions = downloaded_captions
            else:
                final_captions = ""

            self.logger.info(f"get_video_captions: Captions: {final_captions}")
            # if final_captions != "":
            #     self.db.insert_captions_cache(video_id, final_captions)
        
        # Save captions for future reference
        if (final_captions):
            saveFileResult = self.utils.saveFile(video_id, file_path, final_captions)
            if (saveFileResult):
                self.logger.info(f"get_wiki_captions: Caption for ${video_id} are saved at ${file_path}")
            else:
                self.logger.info(f"get_wiki_captions: Caption for ${video_id} are not saved at ${file_path}")

        # will be changed later to return only one caption
        return final_captions
        # return {"nlp": nlp_captions, \
        #         "thirdparty": tp_captions, \
        #         "google": google_captions
        #         }

    def get_audio_captions(self, audio_path, caption_source=CaptionSources.ALL):
        '''
            Get captions from the audio.
        '''
        self.logger.info(f"\n*********************************************************\n"
                        f"get_audio_captions: Getting captions from {audio_path} using {caption_source}"
                        f"\n*********************************************************\n")

        audio_id = self.audio_captions.get_audio_id(audio_path)
        file_path = self.captions_directory
        # Check If captions are already available
        file_content = self.utils.getFile(file_path, audio_id);
        if (not file_content.startswith("Error")):
            return file_content
        # Temporarily disable cache

        final_captions = ""
        
        # Save captions for future reference
        if (final_captions):
            saveFileResult = self.utils.saveFile(audio_id, file_path, final_captions)
            if (saveFileResult):
                self.logger.info(f"get_audio_captions: Caption for ${audio_id} are saved at ${file_path}")
            else:
                self.logger.info(f"get_audio_captions: Caption for ${audio_id} are not saved at ${file_path}")

        return final_captions
    
    def get_wiki_captions(self, source_path):
        """
            Get captions from the wiki url.
        """
        self.logger.info(f"\n*********************************************************\n"
                        f"get_wiki_captions: source_path: {source_path}"
                        f"\n*********************************************************\n")
        # Check If captions are already available
        web_id = self.utils.get_hash_value(source_path)
        file_path = self.captions_directory

        # Check If captions are already available
        file_content = self.utils.getFile(file_path, web_id)
        if (not file_content.startswith("Error")):
            return file_content

        # return self.get_wiki_url_text(source_path)
        if source_path.startswith("https://en.wikipedia.org/wiki/"):
            final_captions = self.get_wiki_url_text(source_path)
        else:
            final_captions = self.get_web_captions(source_path)
            # return self.get_wiki_search_text(source_path)

        # Save captions for future reference
        if (final_captions):
            saveFileResult = self.utils.saveFile(web_id, file_path, final_captions)
            if (saveFileResult):
                self.logger.info(f"get_wiki_captions: Caption for ${web_id} are saved at ${file_path}")
            else:
                self.logger.info(f"get_wiki_captions: Caption for ${web_id} are not saved at ${file_path}")

        return final_captions
    
    def get_full_body_text(self, html_content):
        """
        Fallback method to get all text from the body, similar to the original approach.
        """
        try:
            # Method 2: Get text only from the main body (often cleaner)
            # This will return all adds, unnecessary content on the page like author, date, etc.
            soup = BeautifulSoup(html_content, 'lxml')
            body = soup.find('body')
            if body:
                # Remove script and style tags before extracting text
                for script_or_style in body(['script', 'style']):
                    script_or_style.decompose()
                text = body.get_text(separator=' ', strip=True)
            else:
                # Very unlikely fallback
                # Fallback if no body tag is found (unlikely for valid HTML)
                text = soup.get_text(separator=' ', strip=True)
            
            self.logger.info(f"get_full_body_text: Successfully extracted primary content  \
                            (length: {len(text)})")
            return text
        except Exception as e:
            self.logger.error(f"_get_full_body_text: Error in fallback text extraction: {e}", exc_info=True)
            return None
        
    def get_web_captions(self, source_path):
        """
            Fetches a web page and extracts its visible text content.

            Args:
                url (str): The URL of the web page to read.

            Returns:
                str: The extracted text content, or None if an error occurs.

            readability-lxml: A Python port of Mozilla's Readability library (used in Firefox). 
            Generally very effective.
            newspaper3k: Specifically designed for scraping news articles, extracting text, authors, dates, 
            images, etc.
            trafilatura: A robust library focused on extracting main text, metadata, and comments 
            from web pages, often used for large-scale crawling.
        """
        try:
            self.logger.info(f"get_web_captions: source_path: {source_path}")

            # Add headers to mimic a browser visit, which can help avoid blocks
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            # Send an HTTP GET request to the URL
            response = requests.get(source_path, headers=headers, timeout=30) # Added timeout

            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()

            # Use readability to parse and identify the main content
            doc = Document(response.content) # Pass the raw byte content
            summary_html = doc.summary() # Gets the cleaned HTML of the main content
            self.logger.info(f"get_web_captions: doc: {doc}\nsummary_html: {summary_html}")


            # Parse the HTML content using Beautiful Soup
            # Use response.content for bytes, let BS4 handle encoding detection
            # Or use response.text if you are sure about the encoding
            # If you prefer not to install lxml or encounter issues installing it, you can switch to 
            # Python's standard library HTML parser. It doesn't require any extra installation 
            # but might be slightly slower or less lenient with poorly formed HTML.
            soup = BeautifulSoup(summary_html, 'lxml') # Use 'lxml' or 'html.parser'

            # --- Extract Text ---
            # Method 1: Get all text from the entire page
            # This might include text from <script>, <style> tags, headers, footers etc.
            text = soup.get_text(separator=' ', strip=True)
            self.logger.info(f"get_web_captions: text: {text}")
            if text:
                self.logger.info(f"get_web_captions: Successfully extracted primary content from \
                                {source_path} - (length: {len(text)})")
                return text
            else:
                self.logger.warning(f"get_web_captions: Readability found no primary content in \
                                    {source_path}. Falling back to full body text.")
                # Fallback to your original method if readability fails
                return self.get_full_body_text(response.content)

            # --- Optional: Further refinement (Example: get text only from <p> tags) ---
            # paragraphs = soup.find_all('p')
            # text = '\n'.join([p.get_text(strip=True) for p in paragraphs])
            # -------------------------------------------------------------------------

            # self.logger.info(f"get_web_captions: Successfully extracted {text} from {source_path}")
            # return text

        except requests.exceptions.Timeout:
            self.logger.error(f"get_web_captions: Request timed out for URL: {source_path}")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"get_web_captions: Error fetching URL {source_path}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"get_web_captions: Error parsing URL {source_path}: {e}")
            return None
            
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
            # mw-content-text is the id attribute of an HTML element (usually a <div>) commonly 
            # found on pages generated by MediaWiki software, which powers Wikipedia.
            # this is commonly used to find the primary content area in a wiki page
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
#!/usr/bin/env python3
"""
FastMCP Server for Fact Checker Application
Much simpler implementation using FastMCP framework
"""

import sys
import os
import json
from typing import Optional

# Add the project root to sys.path to allow for absolute imports from 'source'
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    # Insert at the beginning of the path to ensure it's checked first
    sys.path.insert(0, PROJECT_ROOT)

# Import FastMCP
from fastmcp import FastMCP

# Import Fact Checker components
from source.services.lib.DB import Database
from source.services.lib.Logger import Logger
from source.services.lib.readProperties import PropertiesReader
from source.services.lib.utils import Utils, SourceTypes, CaptionSources, SummarizationTypes, TextToAudioSources, AvailableLanguages, AvailableCountryCodes
from source.services.CaptionDerivation import CaptionDerivation
from source.services.StatementDerivation import StatementDerivation
from source.services.SummarizedStatementDerivation import SummarizedStatementDerivation
from source.services.FactDerivation import FactDerivation
from source.services.TextToAudio import TextToAudio

class Services:
    """A container for initialized services to reduce boilerplate."""
    def __init__(self):
        self.logger = Logger().get_logger()
        self.properties = PropertiesReader(kwargs={"logger": self.logger})
        self.utils = Utils(kwargs={"properties": self.properties, "logger": self.logger})
        
        common_kwargs = {
            "properties": self.properties,
            "logger": self.logger,
            "utils": self.utils
        }
        
        self.db = Database(kwargs={**common_kwargs, "utils": self.utils})
        self.captionDerivation = CaptionDerivation(kwargs=common_kwargs)
        self.statementDerivation = StatementDerivation(kwargs=common_kwargs)
        self.summarizedStatementDerivation = SummarizedStatementDerivation(kwargs=common_kwargs)
        self.factDerivation = FactDerivation(kwargs=common_kwargs)
        self.textToAudio = TextToAudio(kwargs=common_kwargs)

# Initialize FastMCP server
mcp = FastMCP("fact-checker-fastmcp")
services = Services()

# Load NLP model
from transformers import pipeline
nlp = pipeline("text-classification", model="bert-base-uncased")

def _get_content_from_source(
    youtube_video_url: Optional[str] = None,
    video_url: Optional[str] = None,
    audio_url: Optional[str] = None,
    podcast_url: Optional[str] = None,
    web_url: Optional[str] = None,
    raw_text: Optional[str] = None
) -> Optional[str]:
    """Helper function to extract content from various sources."""
    if youtube_video_url:
        return services.captionDerivation.get_captions(
            source_path=youtube_video_url,
            source_type=SourceTypes.YOUTUBE,
            caption_source=CaptionSources.ALL
        )
    if video_url:
        return services.captionDerivation.get_captions(
            source_path=video_url,
            source_type=SourceTypes.VIDEO,
            caption_source=CaptionSources.ALL
        )
    if audio_url:
        return services.captionDerivation.get_captions(
            source_path=audio_url,
            source_type=SourceTypes.AUDIO,
            caption_source=CaptionSources.ALL
        )
    if podcast_url:
        return services.captionDerivation.get_captions(
            source_path=podcast_url,
            source_type=SourceTypes.PODCAST,
            caption_source=CaptionSources.ALL
        )
    if web_url:
        return services.captionDerivation.get_captions(source_path=web_url, source_type=SourceTypes.WIKI)
    if raw_text:
        return raw_text
    return None

@mcp.tool()
def register_user(username: str, password: str) -> str:
    """Register a new user with username and password."""
    services.logger.info(f"FastMCP register: Registering user: {username}")
    result = services.db.create_user(username, password)
    services.logger.info(f"FastMCP register: User registration result: {result}")
    return json.dumps(result, indent=2)

@mcp.tool()
def login_user(username: str, password: str) -> str:
    """Login a user with username and password."""
    result = services.db.verify_user(username, password)
    if result:
        return "Login successful"
    else:
        return "Invalid credentials"

@mcp.tool()
def logout_user() -> str:
    """Logout the current user and clear session."""
    return "Logout successful"

@mcp.tool()
def get_captions(
    youtube_video_url: Optional[str] = None,
    video_url: Optional[str] = None,
    audio_url: Optional[str] = None,
    podcast_url: Optional[str] = None,
    web_url: Optional[str] = None
) -> str:
    """Extract captions/transcripts from various media sources."""
    if not any([youtube_video_url, video_url, audio_url, podcast_url, web_url]):
        return json.dumps({"error": "No URL provided"}, indent=2)
    
    services.logger.info("FastMCP get_captions: Processing captions for provided URL")
    content = _get_content_from_source(
        youtube_video_url, video_url, audio_url, podcast_url, web_url
    )
    
    return json.dumps({"captions": content}, indent=2)

@mcp.tool()
def get_summarization(
    youtube_video_url: Optional[str] = None,
    video_url: Optional[str] = None,
    audio_url: Optional[str] = None,
    podcast_url: Optional[str] = None,
    web_url: Optional[str] = None,
    raw_text: Optional[str] = None,
    selectedSize: Optional[str] = None
) -> str:
    """Get summarized content from various sources with optional size selection."""
    if not any([youtube_video_url, video_url, audio_url, podcast_url, web_url, raw_text]):
        return json.dumps({"error": "No text provided"}, indent=2)
    
    services.logger.info("FastMCP get_summarization: Processing summarization")
    
    content = _get_content_from_source(
        youtube_video_url, video_url, audio_url, podcast_url, web_url, raw_text
    )
    
    if not content:
        return json.dumps({"error": "Not able to get captions/transcript for Summarization"}, indent=2)
    
    paraphrasing = bool(raw_text)
    summarized_text = services.summarizedStatementDerivation.get_summarized_statements(
        content,
        summary_type=SummarizationTypes.ABSTRACTIVE_SUMMARY, 
        parapharizing=paraphrasing, 
        selectedSize=selectedSize
    )
    
    return json.dumps({"summarized_text": summarized_text}, indent=2)

@mcp.tool()
def get_statements(
    youtube_video_url: Optional[str] = None,
    video_url: Optional[str] = None,
    audio_url: Optional[str] = None,
    podcast_url: Optional[str] = None,
    web_url: Optional[str] = None,
    raw_text: Optional[str] = None
) -> str:
    """Extract factual statements from various media sources."""
    if not any([youtube_video_url, video_url, audio_url, podcast_url, web_url, raw_text]):
        return json.dumps({"error": "No text provided"}, indent=2)
    
    services.logger.info("FastMCP get_statements: Processing statements")
    
    content = _get_content_from_source(
        youtube_video_url, video_url, audio_url, podcast_url, web_url, raw_text
    )
    
    if not content:
        return json.dumps({"error": "Not able to get captions/transcript for Factual Statements"}, indent=2)
    
    factual_statements = services.statementDerivation.get_factual_statements(content, "nltk")
    
    return json.dumps({"factual_statements": factual_statements}, indent=2)

@mcp.tool()
def fact_check(claim: str) -> str:
    """Check the veracity of a claim using database, external APIs, and NLP analysis."""
    if not claim:
        return json.dumps({"error": "No claim provided"}, indent=2)
    
    services.logger.info(f"FastMCP fact_check: Checking claim: {claim}")
    
    # Check cache first
    cached_result = services.db.get_cached_result(claim)
    if cached_result:
        services.logger.info("FastMCP fact_check: Cache hit")
        return json.dumps({"claim": claim, "result": cached_result}, indent=2)
    
    # Check database
    result = services.db.check_fact_db(claim)
    if result is not None:
        services.logger.info("FastMCP fact_check: Database hit")
        services.db.cache_result(claim, str(bool(result)))
        return json.dumps({"claim": claim, "truth": bool(result)}, indent=2)
    
    # Check external API
    external_result = services.factDerivation.check_external_api(claim)
    if external_result != "Unknown":
        services.logger.info("FastMCP fact_check: External API hit")
        services.db.cache_result(claim, external_result)
        return json.dumps({"claim": claim, "external_result": external_result}, indent=2)
    
    # Perform NLP analysis
    services.logger.info("FastMCP fact_check: Performing NLP analysis")
    analysis = nlp(claim)
    services.db.cache_result(claim, str(analysis))
    
    return json.dumps({"claim": claim, "analysis": analysis}, indent=2)

@mcp.tool()
def text_to_speech(text: str, action: Optional[str] = None) -> str:
    """Convert text to speech audio file."""
    if not text:
        return json.dumps({"error": "No text provided"}, indent=2)
    
    services.logger.info(f"FastMCP text_to_speech: Converting text to speech")
    
    speech_path = services.textToAudio.getAudio(
        text=text, 
        source=TextToAudioSources.GTTS, 
        language=AvailableLanguages.ENGLISH, 
        countryCode=AvailableCountryCodes.US, 
        action=action
    )
    
    if speech_path:
        speech_path = services.textToAudio.get_file_without_folder_name(speech_path)
    
    services.logger.info(f"FastMCP text_to_speech: speech_path: {speech_path}")
    
    return json.dumps({"speech_path": speech_path}, indent=2)

if __name__ == "__main__":
    import sys
    
    # Get port from command line argument or use default
    port = 6278  # Default port
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"❌ Invalid port number: {sys.argv[1]}")
            print("Usage: python fastmcp_server.py [port]")
            sys.exit(1)
    
    print(f"🚀 Starting FastMCP Fact Checker Server on port {port}...")
    mcp.run(port=port, transport='streamable-http',
            proxy_token=os.environ.get("MCP_PROXY_TOKEN"))
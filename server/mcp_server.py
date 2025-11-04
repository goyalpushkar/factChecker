#!/usr/bin/env python3
"""
MCP Server for Fact Checker Application
Exposes Flask endpoints from views.py as MCP tools
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional, Union
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Import Flask app and dependencies
from source.views import app, db, captionDerivation, statementDerivation, summarizedStatementDerivation, factDerivation, textToAudio, authorization, logger
from source.services.lib.utils import SourceTypes, CaptionSources, SummarizationTypes, TextToAudioSources, AvailableLanguages, AvailableCountryCodes

# Create MCP server instance
server = Server("fact-checker-mcp")

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List all available tools from the Fact Checker application."""
    tools = [
        Tool(
            name="register_user",
            description="Register a new user with username and password",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Username for the new user"
                    },
                    "password": {
                        "type": "string",
                        "description": "Password for the new user"
                    }
                },
                "required": ["username", "password"]
            }
        ),
        Tool(
            name="login_user",
            description="Login a user with username and password",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Username for login"
                    },
                    "password": {
                        "type": "string",
                        "description": "Password for login"
                    }
                },
                "required": ["username", "password"]
            }
        ),
        Tool(
            name="logout_user",
            description="Logout the current user and clear session",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_captions",
            description="Extract captions/transcripts from various media sources (YouTube, video, audio, podcast, web)",
            inputSchema={
                "type": "object",
                "properties": {
                    "youtube_video_url": {
                        "type": "string",
                        "description": "YouTube video URL"
                    },
                    "video_url": {
                        "type": "string",
                        "description": "Direct video file URL"
                    },
                    "audio_url": {
                        "type": "string",
                        "description": "Direct audio file URL"
                    },
                    "podcast_url": {
                        "type": "string",
                        "description": "Podcast URL"
                    },
                    "web_url": {
                        "type": "string",
                        "description": "Web page URL for content extraction"
                    }
                },
                "anyOf": [
                    {"required": ["youtube_video_url"]},
                    {"required": ["video_url"]},
                    {"required": ["audio_url"]},
                    {"required": ["podcast_url"]},
                    {"required": ["web_url"]}
                ]
            }
        ),
        Tool(
            name="get_summarization",
            description="Get summarized content from various sources with optional size selection",
            inputSchema={
                "type": "object",
                "properties": {
                    "youtube_video_url": {
                        "type": "string",
                        "description": "YouTube video URL"
                    },
                    "video_url": {
                        "type": "string",
                        "description": "Direct video file URL"
                    },
                    "audio_url": {
                        "type": "string",
                        "description": "Direct audio file URL"
                    },
                    "podcast_url": {
                        "type": "string",
                        "description": "Podcast URL"
                    },
                    "web_url": {
                        "type": "string",
                        "description": "Web page URL for content extraction"
                    },
                    "raw_text": {
                        "type": "string",
                        "description": "Raw text to summarize"
                    },
                    "selectedSize": {
                        "type": "string",
                        "description": "Size of summary (optional)",
                        "enum": ["small", "medium", "large"]
                    }
                },
                "anyOf": [
                    {"required": ["youtube_video_url"]},
                    {"required": ["video_url"]},
                    {"required": ["audio_url"]},
                    {"required": ["podcast_url"]},
                    {"required": ["web_url"]},
                    {"required": ["raw_text"]}
                ]
            }
        ),
        Tool(
            name="get_statements",
            description="Extract factual statements from various media sources",
            inputSchema={
                "type": "object",
                "properties": {
                    "youtube_video_url": {
                        "type": "string",
                        "description": "YouTube video URL"
                    },
                    "video_url": {
                        "type": "string",
                        "description": "Direct video file URL"
                    },
                    "audio_url": {
                        "type": "string",
                        "description": "Direct audio file URL"
                    },
                    "podcast_url": {
                        "type": "string",
                        "description": "Podcast URL"
                    },
                    "web_url": {
                        "type": "string",
                        "description": "Web page URL for content extraction"
                    },
                    "raw_text": {
                        "type": "string",
                        "description": "Raw text to extract statements from"
                    }
                },
                "anyOf": [
                    {"required": ["youtube_video_url"]},
                    {"required": ["video_url"]},
                    {"required": ["audio_url"]},
                    {"required": ["podcast_url"]},
                    {"required": ["web_url"]},
                    {"required": ["raw_text"]}
                ]
            }
        ),
        Tool(
            name="fact_check",
            description="Check the veracity of a claim using database, external APIs, and NLP analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "claim": {
                        "type": "string",
                        "description": "The claim to fact-check"
                    }
                },
                "required": ["claim"]
            }
        ),
        Tool(
            name="text_to_speech",
            description="Convert text to speech audio file",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to convert to speech"
                    },
                    "action": {
                        "type": "string",
                        "description": "Action type for TTS processing (optional)"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="oauth2_authorize",
            description="Get Google OAuth2 authorization URL",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="oauth2_callback",
            description="Handle OAuth2 callback from Google",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Authorization code from Google"
                    },
                    "state": {
                        "type": "string",
                        "description": "State parameter for OAuth2"
                    }
                },
                "required": ["code", "state"]
            }
        )
    ]
    return ListToolsResult(tools=tools)

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls for the Fact Checker application."""
    
    try:
        if name == "register_user":
            username = arguments.get("username")
            password = arguments.get("password")
            
            if not username or not password:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: Username and password are required")]
                )
            
            logger.info(f"MCP register: Registering user: {username}")
            result = db.create_user(username, password)
            logger.info(f"MCP register: User registration result: {result}")
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        
        elif name == "login_user":
            username = arguments.get("username")
            password = arguments.get("password")
            
            if not username or not password:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: Username and password are required")]
                )
            
            result = db.verify_user(username, password)
            
            if result:
                return CallToolResult(
                    content=[TextContent(type="text", text="Login successful")]
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text="Invalid credentials")]
                )
        
        elif name == "logout_user":
            return CallToolResult(
                content=[TextContent(type="text", text="Logout successful")]
            )
        
        elif name == "get_captions":
            youtube_video_url = arguments.get("youtube_video_url")
            web_url = arguments.get("web_url")
            video_url = arguments.get("video_url")
            audio_url = arguments.get("audio_url")
            podcast_url = arguments.get("podcast_url")
            
            if not any([youtube_video_url, video_url, audio_url, podcast_url, web_url]):
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: No URL provided")]
                )
            
            logger.info(f"MCP get_captions: Processing captions for provided URL")
            
            captions = None
            if youtube_video_url:
                captions = captionDerivation.get_captions(
                    source_path=youtube_video_url, 
                    source_type=SourceTypes.YOUTUBE, 
                    caption_source=CaptionSources.ALL
                )
            elif video_url:
                captions = captionDerivation.get_captions(
                    source_path=video_url, 
                    source_type=SourceTypes.VIDEO, 
                    caption_source=CaptionSources.ALL
                )
            elif audio_url:
                captions = captionDerivation.get_captions(
                    source_path=audio_url, 
                    source_type=SourceTypes.AUDIO, 
                    caption_source=CaptionSources.ALL
                )
            elif podcast_url:
                captions = captionDerivation.get_captions(
                    source_path=podcast_url, 
                    source_type=SourceTypes.PODCAST, 
                    caption_source=CaptionSources.ALL
                )
            elif web_url:
                captions = captionDerivation.get_captions(
                    source_path=web_url, 
                    source_type=SourceTypes.WIKI
                )
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"captions": captions}, indent=2))]
            )
        
        elif name == "get_summarization":
            youtube_video_url = arguments.get("youtube_video_url")
            web_url = arguments.get("web_url")
            video_url = arguments.get("video_url")
            audio_url = arguments.get("audio_url")
            podcast_url = arguments.get("podcast_url")
            raw_text = arguments.get("raw_text")
            selectedSize = arguments.get("selectedSize")
            
            if not any([youtube_video_url, video_url, audio_url, podcast_url, web_url, raw_text]):
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: No text provided")]
                )
            
            logger.info(f"MCP get_summarization: Processing summarization")
            
            captions = None
            paraphrasing = False
            
            if youtube_video_url:
                captions = captionDerivation.get_captions(
                    source_path=youtube_video_url, 
                    source_type=SourceTypes.YOUTUBE, 
                    caption_source=CaptionSources.ALL
                )
            elif video_url:
                captions = captionDerivation.get_captions(
                    source_path=video_url, 
                    source_type=SourceTypes.VIDEO, 
                    caption_source=CaptionSources.ALL
                )
            elif audio_url:
                captions = captionDerivation.get_captions(
                    source_path=audio_url, 
                    source_type=SourceTypes.AUDIO, 
                    caption_source=CaptionSources.ALL
                )
            elif podcast_url:
                captions = captionDerivation.get_captions(
                    source_path=podcast_url, 
                    source_type=SourceTypes.PODCAST, 
                    caption_source=CaptionSources.ALL
                )
            elif web_url:
                captions = captionDerivation.get_captions(
                    source_path=web_url, 
                    source_type=SourceTypes.WIKI
                )
            elif raw_text:
                captions = raw_text
                paraphrasing = True
            
            if not captions:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: Not able to get captions/transcript for Summarization")]
                )
            
            summarized_text = summarizedStatementDerivation.get_summarized_statements(
                captions, 
                summary_type=SummarizationTypes.ABSTRACTIVE_SUMMARY, 
                parapharizing=paraphrasing, 
                selectedSize=selectedSize
            )
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"summarized_text": summarized_text}, indent=2))]
            )
        
        elif name == "get_statements":
            youtube_video_url = arguments.get("youtube_video_url")
            web_url = arguments.get("web_url")
            video_url = arguments.get("video_url")
            audio_url = arguments.get("audio_url")
            podcast_url = arguments.get("podcast_url")
            raw_text = arguments.get("raw_text")
            
            if not any([youtube_video_url, video_url, audio_url, podcast_url, web_url, raw_text]):
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: No text provided")]
                )
            
            logger.info(f"MCP get_statements: Processing statements")
            
            captions = None
            if youtube_video_url:
                captions = captionDerivation.get_captions(
                    source_path=youtube_video_url, 
                    source_type=SourceTypes.YOUTUBE, 
                    caption_source=CaptionSources.ALL
                )
            elif video_url:
                captions = captionDerivation.get_captions(
                    source_path=video_url, 
                    source_type=SourceTypes.VIDEO, 
                    caption_source=CaptionSources.ALL
                )
            elif audio_url:
                captions = captionDerivation.get_captions(
                    source_path=audio_url, 
                    source_type=SourceTypes.AUDIO, 
                    caption_source=CaptionSources.ALL
                )
            elif podcast_url:
                captions = captionDerivation.get_captions(
                    source_path=podcast_url, 
                    source_type=SourceTypes.PODCAST, 
                    caption_source=CaptionSources.ALL
                )
            elif web_url:
                captions = captionDerivation.get_captions(
                    source_path=web_url, 
                    source_type=SourceTypes.WIKI
                )
            elif raw_text:
                captions = raw_text
            
            if not captions:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: Not able to get captions/transcript for Factual Statements")]
                )
            
            factual_statements = statementDerivation.get_factual_statements(captions, "nltk")
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"factual_statements": factual_statements}, indent=2))]
            )
        
        elif name == "fact_check":
            claim = arguments.get("claim")
            
            if not claim:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: No claim provided")]
                )
            
            logger.info(f"MCP fact_check: Checking claim: {claim}")
            
            # Check cache first
            cached_result = db.get_cached_result(claim)
            if cached_result:
                logger.info("MCP fact_check: Cache hit")
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps({"claim": claim, "result": cached_result}, indent=2))]
                )
            
            # Check database
            result = db.check_fact_db(claim)
            if result is not None:
                logger.info("MCP fact_check: Database hit")
                db.cache_result(claim, str(bool(result)))
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps({"claim": claim, "truth": bool(result)}, indent=2))]
                )
            
            # Check external API
            external_result = factDerivation.check_external_api(claim)
            if external_result != "Unknown":
                logger.info("MCP fact_check: External API hit")
                db.cache_result(claim, external_result)
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps({"claim": claim, "external_result": external_result}, indent=2))]
                )
            
            # Perform NLP analysis
            logger.info("MCP fact_check: Performing NLP analysis")
            from transformers import pipeline
            nlp = pipeline("text-classification", model="bert-base-uncased")
            analysis = nlp(claim)
            db.cache_result(claim, str(analysis))
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"claim": claim, "analysis": analysis}, indent=2))]
            )
        
        elif name == "text_to_speech":
            text_for_speech = arguments.get("text")
            action = arguments.get("action")
            
            if not text_for_speech:
                return CallToolResult(
                    content=[TextContent(type="text", text="Error: No text provided")]
                )
            
            logger.info(f"MCP text_to_speech: Converting text to speech")
            
            speech_path = textToAudio.getAudio(
                text=text_for_speech, 
                source=TextToAudioSources.GTTS, 
                language=AvailableLanguages.ENGLISH, 
                countryCode=AvailableCountryCodes.US, 
                action=action
            )
            
            if speech_path:
                speech_path = textToAudio.get_file_without_folder_name(speech_path)
            
            logger.info(f"MCP text_to_speech: speech_path: {speech_path}")
            
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"speech_path": speech_path}, indent=2))]
            )
        
        elif name == "oauth2_authorize":
            # This would need to be implemented based on your OAuth flow
            # For now, return a placeholder
            return CallToolResult(
                content=[TextContent(type="text", text="OAuth2 authorization not implemented in MCP context")]
            )
        
        elif name == "oauth2_callback":
            # This would need to be implemented based on your OAuth flow
            # For now, return a placeholder
            return CallToolResult(
                content=[TextContent(type="text", text="OAuth2 callback not implemented in MCP context")]
            )
        
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {name}")]
            )
    
    except Exception as e:
        logger.error(f"MCP Error in {name}: {str(e)}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )

async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="fact-checker-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(prompts_changed=False,resources_changed=False,tools_changed=False),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())


#!/usr/bin/env python3
"""
Text-to-SQL Generator for Oracle Analytics Agent

This module uses an LLM to convert natural language questions into executable
Oracle SQL queries, using database schema as context.
"""

import os
# from anthropic import Anthropic
# import aisuite as ai
# from mcp import ClientSession
from typing import List, Dict, Any, TypedDict


# Add the project root to sys.path for consistent imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
import sys
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

class ToolDefinition(TypedDict):
    name: str
    description: str
    input_schema: dict

class SearchYouTubeVideos:
    """
    Handles the generation of SQL queries from natural language using an LLM.
    """

    # def __init__(self):
    def __init__(self):
        """
        Initializes the generator with a database connection pool and LLM client.

        Args:
            
        """

    def build_prompt(self, natural_language_query: str) -> str:
        """
        Constructs the summary for the provided text by LLM.
        """
        prompt = f"""Human: You are an expert search engine. Your task is to search you tube videos for a natural language question.

Follow these rules strictly:
1.  Search only on YouTube platform.
2.  ***STRICT RESTRICTION***: Don't use any of the custom mcp tools.
3.  ***STRICT RESTRICTION***: Don't generate any videos by yourself, only add videos available on YouTube.
4.  Ensure that video links are valid YouTube URLs.
5.  Search most relevant videos for the provided keywords. 
6.  Get aleast top 3 videos for each keyword. Dont return more than 9 videos in total
7.  if no relevant info is found, respond with "No relevant information found."
8.  Return the response in json format as mentioned below.

Here are the keywords to search videos for:
<keywords>
{natural_language_query}
</keywords>

Return the response in Json format as below:
<<relevant_videos>>
{{
"keyword": [{{"title": "video title 1", "url": "video url 1", "channel": "channel name 1"}},
{{"title": "video title 2", "url": "video url 2", "channel": "channel name 2"}},
{{"title": "video title 3", "url": "video url 3", "channel": "channel name 3"}},
{{"title": "video title 4", "url": "video url 4", "channel": "channel name 4"}},
{{"title": "video title 5", "url": "video url 5", "channel": "channel name 5"}} ]
}}
<<relevant_videos>>

Assistant:
"""
        # 3.  Don't add any thing extra just search for the relevant videos.
        return prompt
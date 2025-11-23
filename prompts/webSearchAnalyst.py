
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

class WebSearchAnalyst:
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
        prompt = f"""Human: You are an expert research analyst. Your task is to search web for a natural language question.

Follow these rules strictly:
1.  Search web links, you tube videos, news articles, blogs, research papers etc.
2.  ***STRICT RESTRICTION***: Don't use any of the custom mcp tools.
3.  ***STRICT RESTRICTION***: Don't generate any videos, links by yourself, add only genuine links.
4.  Ensure that video links are valid YouTube URLs and web links are valid urls
5.  Search most relevant details for the provided keywords. 
6.  Get aleast top 3 links for each keyword. Dont return more than 9 links in total
7.  if no relevant info is found, respond with "No relevant information found."
8.  Return the response strictly in json format and ensure it is a valid json.

Here are the keywords to search videos for:
<keywords>
{natural_language_query}
</keywords>

Return the response in Json format as below:
<<relevant_links>>
{{
"keyword": [{{"title": "title 1", "url": "web/video url 1", "channel": "channel name 1"}},
{{"title": "title 2", "url": "web/video url 2", "channel": "channel name 2"}},
{{"title": "title 3", "url": "web/video url 3", "channel": "channel name 3"}},
{{"title": "title 4", "url": "web/video url 4", "channel": "channel name 4"}},
{{"title": "title 5", "url": "web/video url 5", "channel": "channel name 5"}} ]
}}
<<relevant_links>>

Assistant:
"""
        # 3.  Don't add any thing extra just search for the relevant videos.
        return prompt

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
from typing import TypedDict


# Add the project root to sys.path for consistent imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
import sys
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

class ToolDefinition(TypedDict):
    name: str
    description: str
    input_schema: dict

class CaptionDerivation:
    """
    Handles the caption generation for provided source using an LLM.
    """

    # def __init__(self):
    def __init__(self):
        """
        Initializes the generator with a database connection pool and LLM client.

        Args:
            
        """

    def build_prompt(self, natural_language_query: str) -> str:
        """
        Constructs the prompt for the LLM to get the captions.
        """
        prompt = f"""Human: You are an expert Caption Generator or Derivator. Your task is to get captions using available tools based on the provided natural language question.

Follow these rules strictly:
1.  Use available tools to get captions relevant to the user's question.
2.  Try to identify the url type (e.g., youtube_video_url, web_url, video_url, audio_url) from the question if possible.
3.  If no captions are found, respond with an empty list.
4.  Do not attempt to generate captions yourself; rely solely on the tools provided.


Here is the user's question:
<question>
{natural_language_query}
</question>

Return the response as a json with captions
<captions>
{{"captions": ["caption1", "caption2", "..."]}}
</captions>

Assistant:
"""
        
        # TODO: provide context to get info from CLOB columns too
#         3.  Focus on extracting captions that directly address the user's query.
# 4.  Ensure the captions are clear, concise, and informative.
# 5.  If multiple captions are relevant, provide a list of captions.

        return prompt
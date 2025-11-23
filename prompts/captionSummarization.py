
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

class CaptionSummarization:
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
        prompt = f"""Human: You are an expert text summarizer. Your task is to get summarize the text based on the provided natural language question.

Follow these rules strictly:
1.  dont add any thing extra just summarize the captions.
2.  keep it short and precise.
3.  focus on the main points.
4.  Add examples used in the text to support the summary.
5.  if no relevant info is found, respond with "No relevant information found."
6.  Return a list of only 5 keywords that summarize the main points.
7.  Return the response in json format as mentioned below.

Here is the text to summarize:
<text>
{natural_language_query}
</text>

Return the response as a json with summary and keywords
{{ "summary": "your summarized text",
"keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
}}

Assistant:
"""
        return prompt
#!/usr/bin/env python3
"""
Text-to-SQL Generator for Oracle Analytics Agent

This module uses an LLM to convert natural language questions into executable
Oracle SQL queries, using database schema as context.
"""

import os
import re
import asyncio
import uuid
from typing import List, Dict, TypedDict,Optional, Any
import json
import pandas as pd

from anthropic import Anthropic
# import aisuite as ai
from mcp import ClientSession

# Add the project root to sys.path for consistent imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
import sys
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from source.services.lib import readProperties as PropertiesReader
from source.services.lib import Logger
from clients.utils import Utils
from prompts.captionDerivation import CaptionDerivation
from prompts.captionSummarization import CaptionSummarization
from prompts.searchYouTubeVideos import SearchYouTubeVideos
from prompts.webSearchAnalyst import WebSearchAnalyst

from fastmcp import FastMCP

# from client.text_to_sql_generator import TextToSQLGenerator
# from client.sql_verification import SQLVerifier
# from client.chart_generator import ChartGenerator
# from client.chart_verification import ChartVerifier
# from clients.utils import Utils

class ToolDefinition(TypedDict):
    name: str
    description: str
    input_schema: dict

class LLMCallChat:
    """
    Handles the generation of SQL queries from natural language using an LLM.
    """

    # def __init__(self, connection_pool: oracledb.SessionPool):
    def __init__(self):
        """
        Initializes the generator with a database connection pool and LLM client.

        Args:
            connection_pool: An oracledb.SessionPool for database schema fetching.
        """
        self.property_reader = PropertiesReader.PropertiesReader()
        self.logger = Logger.Logger.get_logger()
        self.utils = Utils()

        anthropic_api_key = self.property_reader.get_property('api', 'ANTHROPIC_API_KEY', default='NA') # openai_api_key
        # openai_api_key = self.property_reader.get_property('api', 'OPEN_API_KEY', default='NA')
        # self.logger.info(f"Log File Path from Properties: {log_file_path}")
        # self.chart_path = self.property_reader.get_property('folders', 'chart_path', default='./charts/')
        # self.charts_refined = self.property_reader.get_property('folders', 'charts_refined', default='./charts_refined')
        # self.output_chart_path = os.path.join(chart_path, "output_chart.png")

        # Get available tools and sessions from ServerConnection
        self.available_tools: List[ToolDefinition] = [] # new
        self.tool_to_session: Dict[str, ClientSession] = {} # new
        # Prompts list for quick display 
        self.available_prompts = []
        # Sessions dict maps tool/prompt names or resource URIs to MCP client sessions
        self.sessions = {}

        # Initialize the Anthropic and AI clients
        # self.pool = connection_pool
        self.anthropic_client = Anthropic(api_key=anthropic_api_key)
        # self.ai_client = ai.Client({"openai": {"api_key": openai_api_key}})
        self.conn_name = "oms_dev"

    # Iterable[MessageParam]. list[dict[str, str]]
    def _call_llm(self, message: list[dict[str, str]], model: str="claude-3-haiku-20240307") -> str:
        message = self.anthropic_client.messages.create(
                # Temporarily switch to Haiku to test API key access.
                model=model, # Fastest model, good for testing.
                max_tokens=1024,
                messages=message,
                tools=self.available_tools
            )
        
        return message
    
    async def chat_loop(self, schema_context: str):
        """
        Runs an interactive chat loop where the user can continuously ask questions.
        """
        self.logger.info("\n--- Caption Generator Chat ---")
        self.logger.info("Enter your question to generate Captions. Type 'quit' or 'exit' to end the chat.")

        while True:
            
            try:
                natural_language_query = input("\nYour question: ").strip()

                if natural_language_query.lower() in ['quit', 'exit']:
                    self.logger.info("Exiting chat. Goodbye!")
                    break
                
                caption_result = ""
                summary = ""
                if natural_language_query:
                    # 1. Generate SQL query
                    caption_result = await self._get_captions(natural_language_query, schema_context)
                    self.logger.info("-------------------LLM Generated Captions-------------")
                    self.logger.info(caption_result)
                    self.logger.info("--------------------------\n")

                    # 2. Generate summary from captions
                    if caption_result:
                        # instruction = f"Generate a chart for the following data to answer the question: {natural_language_query}"
                        summary = await self._summarize_content(caption_result)
                        self.logger.info("-------------------LLM Generated Summary-------------")
                        self.logger.info(summary)
                        self.logger.info("--------------------------\n")

                    # 3. Search more videos based on summary keywords
                    if summary and 'keywords' in summary:
                        keywords = summary['keywords']
                        search_query = ", ".join(keywords)
                        more_videos = await self._search_more_videos(search_query)
                        self.logger.info("-------------------LLM Searched More Videos-------------")
                        self.logger.info(more_videos)
                        self.logger.info("--------------------------\n")
                        # Process more_videos as needed
                        # e.g., display to user or integrate into further analysis  

                    # return summary
                
            except Exception as e:
                self.logger.info(f"❌ An error occurred: {e}")

            
        
    async def _get_captions(self, natural_language_query:str, schema_context: str) -> str:
        try:
            # Generate and process the SQL for the user's question
            # 1. Build the prompt for the LLM
            self.logger.info("--------------------------\n")
            self.logger.info("\n-------------------Generate Caption-------------------")
            captionDerivator = CaptionDerivation()
            prompt = captionDerivator.build_prompt(natural_language_query)

            # 2. Call the LLM to get the SQL
            generated_caption = await self.process_query(prompt)
            # self.logger.info(generated_sql) 

            # self.logger.info("-------------------LLM Generated Caption-------------")
            # self.logger.info(generated_caption)

            return generated_caption
        except Exception as e:
            self.logger.error(f"❌ Error generating Captions: {e}")
            return ""

    async def _summarize_content(self, natural_language_query:str) -> Optional[Dict[str, Any]]:
        try:
            # Generate and process the SQL for the user's question
            # 1. Build the prompt for the LLM
            self.logger.info("--------------------------\n")
            self.logger.info("\n-------------------Generate Summary-------------------")
            captionSummarizer = CaptionSummarization()
            prompt = captionSummarizer.build_prompt(natural_language_query)

            # 2. Call the LLM to get the SQL
            generated_summary = await self.process_query(prompt)
            # self.logger.info(generated_sql)

            # self.logger.info("-------------------LLM Generated Summary-------------")
            # self.logger.info(generated_summary)

            return self.utils.read_json(generated_summary)
        except Exception as e:
            self.logger.error(f"❌ Error generating summary: {e}")
            return {}
        
    async def _search_more_videos(self, natural_language_query:str) -> Optional[Dict[str, Any]]:
        try:
            # Generate and process the SQL for the user's question
            # 1. Build the prompt for the LLM
            self.logger.info("--------------------------\n")
            self.logger.info("\n-------------------Search More Videos-------------------")
            # searchYouTubeVideos = SearchYouTubeVideos()
            webSearchAnalyst = WebSearchAnalyst()
            prompt = webSearchAnalyst.build_prompt(natural_language_query)

            # 2. Call the LLM to get the SQL
            searched_links = await self.process_query(prompt)
            # self.logger.info(generated_sql)

            # self.logger.info("-------------------LLM Generated Summary-------------")
            # self.logger.info(searched_links)

            return self.utils.read_json(searched_links)
        except Exception as e:
            self.logger.error(f"❌ Error searching more videos: {e}")
            return {}
        
    async def process_query(self, prompt: str) -> str:
        # , natural_language_query: str, table_names: List[str], schema_context: str
        """
        High-level method to process a natural language query and return the SQL.

        Args:
            prompt: The constructed prompt for the LLM.

        Returns:
            A string containing the generated SQL query.
        """
        # 1. Build the prompt for the LLM
        # text_to_sql_generator = TextToSQLGenerator()
        # prompt = text_to_sql_generator.build_prompt(natural_language_query, table_names, schema_context)
        
        messages = [{'role':'user', 'content':prompt}]
        # 2. Display the constructed prompt (for debugging)
        self.logger.info("\n--- Constructed Prompt ---")
        self.logger.info(messages)
        self.logger.info("--------------------------\n")   

        # 3. Call the Anthropic API
        try:
            # message = self.ai_client.chat.completions.create(
            # model="openai:gpt-4.1",
            message = self._call_llm(message=messages, model="claude-3-haiku-20240307")
            
            self.logger.info("--- LLM Response ---")
            self.logger.info(message.content)
            # generated_sql = message.content[0].text.strip()

            generated_response = ""
            process_query = True
            while process_query:
                assistant_content = []
                for content in message.content:
                    assistant_content.append(content)
                    if content.type =='text':
                        # self.logger.info(content.text)
                        if(len(message.content) == 1):
                            generated_response = content.text.strip()
                            process_query= False
                    elif content.type == 'tool_use':
                        messages.append({'role':'assistant', 'content':assistant_content})
                        tool_id = content.id
                        tool_args = content.input
                        tool_name = content.name
                        
                        self.logger.info(f"Calling tool {tool_name} with args {tool_args}")
                        
                        # Call a tool
                        session = self.tool_to_session[tool_name] # new
                        result = await session.call_tool(tool_name, arguments=tool_args)
                        self.logger.info(f"--- {tool_name} Tool Call Result ---")
                        self.logger.info(result.content)
                        # messages.append({"role": "user",
                        #                 "content": [
                        #                     {
                        #                         "type": "tool_result",
                        #                         "tool_use_id":tool_id,
                        #                         "content": result.content
                        #                     }
                        #                 ]
                        #                 })
                        # response = self._call_llm(message=messages, model="claude-3-haiku-20240307") 
                        # self.logger.info("--- LLM Response After Tool Call ---")
                        # self.logger.info(response.content)
                        # messages.append({'role':'assistant', 'content':response.content})
                        response = result

                        if(len(response.content) == 1 and response.content[0].type == "text"):
                            tool_output_text = response.content[0].text.strip()
                            self.logger.info(tool_output_text)
                            try:
                                # Attempt to parse the JSON output from the tool
                                tool_output_json = json.loads(tool_output_text)
                                # Extract the 'captions' value, join if it's a list
                                generated_response = tool_output_json.get("captions", "No captions found.")
                            except json.JSONDecodeError:
                                generated_response = tool_output_text
                            process_query= False

            # Basic validation to ensure it's a SELECT statement
            # if not generated_response.upper().startswith("SELECT"):
            #     raise ValueError("LLM did not return a valid SELECT query.")

            self.logger.info(f"--- Generated Result ---\n{generated_response}\n---------------------")
            return generated_response

        except Exception as e:
            self.logger.info(f"❌ Error calling LLM API: {e}")
            raise

async def main():
    from clients.serverConnection import ServerConnection
    # serverConn = ServerConnection(server_config_path="server_config.json")
    logger = Logger.Logger.get_logger()
    async with ServerConnection(server_config_path="server_config.json") as serverConn:
        logger.info("--- Connections Established ---")
        logger.info(serverConn.sessions)
        logger.info(serverConn.available_tools)
        logger.info(serverConn.available_prompts)
        logger.info(serverConn.tool_to_session)
        logger.info("-----------------------------")

        llmCallChat = LLMCallChat()
        llmCallChat.sessions = serverConn.sessions
        llmCallChat.available_tools = serverConn.available_tools
        llmCallChat.available_prompts = serverConn.available_prompts
        llmCallChat.tool_to_session = serverConn.tool_to_session

        # different questions to the AI - 
        # "What is the total sale for today?",
        # "Who is the largest customer by revenue?",
        # "Show me the monthly sales trend for the last year.", 
        # "List the top 5 products by sales volume."
    
        # Start the interactive chat loop
        await llmCallChat.chat_loop(schema_context="")  # schema_context can be populated as needed

# mcp = FastMCP("fact-checker-fastmcp")

if __name__ == "__main__":
    asyncio.run(main())

    # import sys
    
    # # Get port from command line argument or use default
    # port = 6278  # Default port
    # if len(sys.argv) > 1:
    #     try:
    #         port = int(sys.argv[1])
    #     except ValueError:
    #         print(f"❌ Invalid port number: {sys.argv[1]}")
    #         print("Usage: python fastmcp_server.py [port]")
    #         sys.exit(1)
    
    # print(f"🚀 Starting FastMCP Fact Checker Client on port {port}...")
    # mcp.run(transport='stdio')
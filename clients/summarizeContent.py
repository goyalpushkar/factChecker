#!/usr/bin/env python3
"""
A client script to connect to MCP servers, take a URL from the user,
and fetch captions for the given URL.
"""

import asyncio
import json
import os
import sys
from typing import Optional

# Add the project root to sys.path for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from clients.serverConnection import ServerConnection

class ContentFetcher:
    """
    Handles connecting to MCP servers and fetching content.
    """

    def __init__(self):
        self.server_connection = ServerConnection()

    async def connect(self):
        """Connect to all configured MCP servers."""
        print("📡 Connecting to MCP servers...")
        await self.server_connection.connect_to_servers()
        if not self.server_connection.tool_to_session:
            print("❌ No tools found. Please check server configurations and connections.")
            return False
        print("✅ Connected successfully!")
        return True

    def _get_url_type(self, url: str) -> Optional[str]:
        """Determine the type of URL to use as an argument key for the tool."""
        if "youtube.com" in url or "youtu.be" in url:
            return "youtube_video_url"
        elif url.startswith("http") and "wikipedia.org" in url:
            return "web_url"
        elif url.endswith(('.mp4', '.mov', '.avi')):
            return "video_url"
        elif url.endswith(('.mp3', '.wav', '.m4a')):
            return "audio_url"
        elif url.startswith("http"): # Generic fallback for other web pages/podcasts
            return "web_url"
        return None

    async def fetch_captions_from_url(self, url: str) -> Optional[str]:
        """
        Calls the 'get_captions' tool on the MCP server for the given URL.
        """
        tool_name = "get_captions"
        if tool_name not in self.server_connection.tool_to_session:
            print(f"❌ Tool '{tool_name}' not available on any connected server.")
            return None

        url_type = self._get_url_type(url)
        if not url_type:
            print("❌ Could not determine the type of URL provided.")
            return None

        session = self.server_connection.tool_to_session[tool_name]
        arguments = {url_type: url}

        try:
            print(f"🤖 Calling tool '{tool_name}' with arguments: {arguments}")
            result = await session.call_tool(tool_name, arguments=arguments)
            
            if result and result.content:
                # Assuming the result content is a JSON string in a TextContent object
                json_string = result.content[0].text
                data = json.loads(json_string)
                return data.get("captions")
            else:
                print("Tool did not return any content.")
                return None
        except Exception as e:
            print(f"❌ An error occurred while calling the tool: {e}")
            return None

    async def run_interactive(self):
        """Run an interactive loop to get a URL from the user."""
        if not await self.connect():
            return

        try:
            url = input("\nPlease enter a URL to fetch captions from: ").strip()
            if url:
                captions = await self.fetch_captions_from_url(url)
                if captions:
                    print("\n✅ Successfully fetched captions:\n")
                    print(captions)
                else:
                    print("\n❌ Failed to fetch captions for the provided URL.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        finally:
            await self.server_connection.exit_stack.aclose()

async def main():
    fetcher = ContentFetcher()
    await fetcher.run_interactive()

if __name__ == "__main__":
    asyncio.run(main())

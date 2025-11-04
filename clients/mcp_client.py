#!/usr/bin/env python3
"""
MCP Client for Fact Checker Application
Provides a chat interface to interact with the Fact Checker MCP server
"""

import asyncio
import json
import os
import sys
import subprocess
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import threading
import time

# Add the project root to sys.path for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

class FactCheckerMCPClient:
    """MCP Client for interacting with the Fact Checker MCP server."""
    
    def __init__(self):
        self.session = None
        self.tools = []
        self.server_process = None
        self.is_connected = False
        
    async def connect(self):
        """Connect to the MCP server."""
        try:
            # Start the MCP server process
            server_path = os.path.join(PROJECT_ROOT, "mcp_server.py")
            if not os.path.exists(server_path):
                raise FileNotFoundError(f"MCP server not found at {server_path}")
            
            # Start the server process
            self.server_process = subprocess.Popen(
                [sys.executable, server_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Create client session
            self.session = ClientSession()
            
            # Connect via stdio
            await self.session.connect(
                read_stream=self.server_process.stdout,
                write_stream=self.server_process.stdin
            )
            
            # Initialize the session
            await self.session.initialize()
            
            # List available tools
            await self.list_tools()
            
            self.is_connected = True
            print("✅ Connected to Fact Checker MCP server successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to MCP server: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the MCP server."""
        try:
            if self.session:
                await self.session.close()
            if self.server_process:
                self.server_process.terminate()
                self.server_process.wait()
            self.is_connected = False
            print("🔌 Disconnected from MCP server")
        except Exception as e:
            print(f"Error disconnecting: {e}")
    
    async def list_tools(self):
        """List all available tools from the MCP server."""
        try:
            request = ListToolsRequest()
            result = await self.session.list_tools(request)
            self.tools = result.tools
            print(f"📋 Found {len(self.tools)} available tools:")
            for tool in self.tools:
                print(f"  • {tool.name}: {tool.description}")
            return self.tools
        except Exception as e:
            print(f"Error listing tools: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[str]:
        """Call a tool on the MCP server."""
        if not self.is_connected:
            print("❌ Not connected to MCP server")
            return None
        
        try:
            request = CallToolRequest(name=tool_name, arguments=arguments)
            result = await self.session.call_tool(request)
            
            # Extract text content from result
            if result.content:
                for content in result.content:
                    if isinstance(content, TextContent):
                        return content.text
            return "No result returned"
            
        except Exception as e:
            print(f"❌ Error calling tool {tool_name}: {e}")
            return None
    
    def get_tool_by_name(self, name: str) -> Optional[Tool]:
        """Get a tool by its name."""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None
    
    def print_help(self):
        """Print help information."""
        print("\n🤖 Fact Checker MCP Client - Available Commands:")
        print("=" * 60)
        print("📝 Content Processing:")
        print("  • get_captions - Extract captions from videos/audio")
        print("  • get_summarization - Generate summaries")
        print("  • get_statements - Extract factual statements")
        print("")
        print("🔍 Fact Checking:")
        print("  • fact_check - Verify claims")
        print("")
        print("🎵 Audio:")
        print("  • text_to_speech - Convert text to speech")
        print("")
        print("👤 User Management:")
        print("  • register_user - Register new user")
        print("  • login_user - Login user")
        print("  • logout_user - Logout user")
        print("")
        print("🔧 System:")
        print("  • help - Show this help")
        print("  • tools - List all available tools")
        print("  • quit/exit - Exit the client")
        print("=" * 60)
    
    def print_tool_help(self, tool_name: str):
        """Print help for a specific tool."""
        tool = self.get_tool_by_name(tool_name)
        if not tool:
            print(f"❌ Tool '{tool_name}' not found")
            return
        
        print(f"\n📖 Help for '{tool_name}':")
        print(f"Description: {tool.description}")
        print("Parameters:")
        
        if tool.inputSchema and "properties" in tool.inputSchema:
            for param_name, param_info in tool.inputSchema["properties"].items():
                required = param_name in tool.inputSchema.get("required", [])
                required_text = " (required)" if required else " (optional)"
                print(f"  • {param_name}{required_text}: {param_info.get('description', 'No description')}")
                if "enum" in param_info:
                    print(f"    Options: {', '.join(param_info['enum'])}")
        else:
            print("  No parameters required")
    
    async def interactive_chat(self):
        """Start an interactive chat session."""
        print("\n🎯 Starting Fact Checker Chat Session")
        print("Type 'help' for available commands or 'quit' to exit")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                elif user_input.lower() == 'help':
                    self.print_help()
                    continue
                
                elif user_input.lower() == 'tools':
                    await self.list_tools()
                    continue
                
                elif user_input.lower().startswith('help '):
                    tool_name = user_input[5:].strip()
                    self.print_tool_help(tool_name)
                    continue
                
                # Parse command and arguments
                parts = user_input.split()
                command = parts[0]
                
                # Handle different commands
                if command == "register_user":
                    if len(parts) < 3:
                        print("❌ Usage: register_user <username> <password>")
                        continue
                    username, password = parts[1], parts[2]
                    result = await self.call_tool("register_user", {"username": username, "password": password})
                    print(f"🤖 Bot: {result}")
                
                elif command == "login_user":
                    if len(parts) < 3:
                        print("❌ Usage: login_user <username> <password>")
                        continue
                    username, password = parts[1], parts[2]
                    result = await self.call_tool("login_user", {"username": username, "password": password})
                    print(f"🤖 Bot: {result}")
                
                elif command == "logout_user":
                    result = await self.call_tool("logout_user", {})
                    print(f"🤖 Bot: {result}")
                
                elif command == "get_captions":
                    if len(parts) < 3:
                        print("❌ Usage: get_captions <source_type> <url>")
                        print("   Source types: youtube, video, audio, podcast, web")
                        continue
                    source_type, url = parts[1], parts[2]
                    arg_name = f"{source_type}_url"
                    result = await self.call_tool("get_captions", {arg_name: url})
                    print(f"🤖 Bot: {result}")
                
                elif command == "get_summarization":
                    if len(parts) < 3:
                        print("❌ Usage: get_summarization <source_type> <url/text> [size]")
                        print("   Source types: youtube, video, audio, podcast, web, text")
                        print("   Size options: small, medium, large")
                        continue
                    
                    source_type = parts[1]
                    if source_type == "text":
                        text_content = " ".join(parts[2:])
                        args = {"raw_text": text_content}
                    else:
                        url = parts[2]
                        arg_name = f"{source_type}_url"
                        args = {arg_name: url}
                    
                    if len(parts) > 3 and source_type != "text":
                        size = parts[3]
                        args["selectedSize"] = size
                    
                    result = await self.call_tool("get_summarization", args)
                    print(f"🤖 Bot: {result}")
                
                elif command == "get_statements":
                    if len(parts) < 3:
                        print("❌ Usage: get_statements <source_type> <url/text>")
                        print("   Source types: youtube, video, audio, podcast, web, text")
                        continue
                    
                    source_type = parts[1]
                    if source_type == "text":
                        text_content = " ".join(parts[2:])
                        args = {"raw_text": text_content}
                    else:
                        url = parts[2]
                        arg_name = f"{source_type}_url"
                        args = {arg_name: url}
                    
                    result = await self.call_tool("get_statements", args)
                    print(f"🤖 Bot: {result}")
                
                elif command == "fact_check":
                    if len(parts) < 2:
                        print("❌ Usage: fact_check <claim>")
                        continue
                    claim = " ".join(parts[1:])
                    result = await self.call_tool("fact_check", {"claim": claim})
                    print(f"🤖 Bot: {result}")
                
                elif command == "text_to_speech":
                    if len(parts) < 2:
                        print("❌ Usage: text_to_speech <text>")
                        continue
                    text = " ".join(parts[1:])
                    result = await self.call_tool("text_to_speech", {"text": text})
                    print(f"🤖 Bot: {result}")
                
                else:
                    print(f"❌ Unknown command: {command}")
                    print("Type 'help' for available commands")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

class ChatInterface:
    """Simple chat interface wrapper."""
    
    def __init__(self):
        self.client = FactCheckerMCPClient()
    
    async def start(self):
        """Start the chat interface."""
        print("🚀 Fact Checker MCP Client")
        print("=" * 40)
        
        # Connect to MCP server
        if not await self.client.connect():
            print("❌ Failed to connect to MCP server. Please ensure:")
            print("   1. MCP server is properly configured")
            print("   2. All dependencies are installed")
            print("   3. Fact Checker application is set up correctly")
            return
        
        try:
            # Start interactive chat
            await self.client.interactive_chat()
        finally:
            # Cleanup
            await self.client.disconnect()

async def main():
    """Main entry point."""
    chat = ChatInterface()
    await chat.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")

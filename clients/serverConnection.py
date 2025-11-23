import os
import sys
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client
from typing import List, Dict, TypedDict
from contextlib import AsyncExitStack
import json

# Add the project root to sys.path for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

class ToolDefinition(TypedDict):
    name: str
    description: str
    input_schema: dict

class ServerConnection:

    def __init__(self, server_config_path: str = "../server_config.json"):
        # Initialize session and client objects
        # self.sessions: List[ClientSession] = [] # new
        self.exit_stack = AsyncExitStack() # new
        self.anthropic = Anthropic()
        self.available_tools: List[ToolDefinition] = [] # new
        self.tool_to_session: Dict[str, ClientSession] = {} # new
        # Prompts list for quick display 
        self.available_prompts = []
        # Sessions dict maps tool/prompt names or resource URIs to MCP client sessions
        self.sessions = {}
        self.server_config_path = server_config_path # new

    async def __aenter__(self):
        """Connect to all configured MCP servers when entering the async context."""
        await self.connect_to_servers()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanly close all resources managed by the exit stack when exiting the async context."""
        await self.exit_stack.aclose()
    
    async def connect_to_server(self, server_name: str, server_config: dict) -> None:
        """Connect to a single MCP server."""
        try:
            server_params = StdioServerParameters(**server_config)
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            ) # new
            # sse_client(url= "http://127.0.0.1:8000/sse" )
            # streamablehttp_client(url= "server_url/mcp/"
            
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            ) # new
            await session.initialize()
            # self.sessions.append(session)
            
            # List available tools for this session
            response = await session.list_tools()
            tools = response.tools
            print(f"\nConnected to {server_name} with tools:", [t.name for t in tools])
            
            for tool in tools: # new
                self.tool_to_session[tool.name] = session
                self.available_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": {
                        "type": "object",
                        "properties": tool.inputSchema.get("properties", {})
                    }
                })

            # List available prompts
            prompts_response = await session.list_prompts()
            if prompts_response and prompts_response.prompts:
                for prompt in prompts_response.prompts:
                    self.sessions[prompt.name] = session
                    self.available_prompts.append({
                        "name": prompt.name,
                        "description": prompt.description,
                        "arguments": prompt.arguments
                    })
                    
            # List available resources
            resources_response = await session.list_resources()
            if resources_response and resources_response.resources:
                for resource in resources_response.resources:
                    resource_uri = str(resource.uri)
                    self.sessions[resource_uri] = session

        except Exception as e:
            print(f"Failed to connect to {server_name}: {e}")

    async def connect_to_servers(self): # new
        """Connect to all configured MCP servers."""
        try:
            with open(f"{self.server_config_path}", "r") as file:
                data = json.load(file)
            
            servers = data.get("mcpServers", {})
            
            for server_name, server_config in servers.items():
                await self.connect_to_server(server_name, server_config)
        except Exception as e:
            print(f"Error loading server configuration: {e}")
            raise
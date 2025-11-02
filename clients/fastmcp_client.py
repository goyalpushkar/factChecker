#!/usr/bin/env python3
"""
FastMCP Client for Fact Checker Application
Simplified client for FastMCP server
"""

import asyncio
import json
import os
import sys
import subprocess
from typing import Any, Dict, List, Optional

# Add the project root to sys.path for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import FastMCP client
from fastmcp.client import Client

class FastMCPClient:
    """Simplified client for FastMCP server."""
    
    def __init__(self, port: int = 6278):
        self.port = port
        self.mcp_client: Optional[Client] = None # Store the FastMCP client instance
        self.is_connected = False
        
    async def connect(self):
        """Connect to the FastMCP server."""
        try:
            self.mcp_client = Client(f"http://localhost:{self.port}")
            await self.mcp_client.list_tools() # Test connection by listing tools
            self.is_connected = True
            print(f"✅ Connected to FastMCP server on port {self.port}!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to FastMCP server: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the FastMCP server."""
        # With FastMCP client, there's no explicit disconnect for HTTP-based communication
        self.is_connected = False
        print("🔌 Disconnected from FastMCP server") # This is more of a logical disconnect
    
    def print_help(self):
        """Print help information."""
        print("\n🤖 FastMCP Fact Checker Client - Available Commands:")
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
        print("  • quit/exit - Exit the client")
        print("=" * 60)
    
    async def interactive_chat(self):
        """Start an interactive chat session."""
        print(f"\n🎯 Starting FastMCP Fact Checker Chat Session (Port {self.port})")
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
                
                # Parse command and arguments
                parts = user_input.split(maxsplit=1) # Split only once to get command and rest of arguments
                command = parts[0]
                args_str = parts[1] if len(parts) > 1 else ""

                # Helper to parse arguments
                def parse_args_to_dict(arg_string: str) -> Dict[str, Any]:
                    parsed_args = {}
                    if not arg_string: # Handle empty argument string
                        return parsed_args
                    
                    # Split by spaces, but respect quotes for values with spaces
                    # This is a simple parser and might need enhancement for complex cases
                    import shlex
                    split_args = shlex.split(arg_string)
                    
                    # Assuming simple key-value pairs or positional arguments for now
                    # For more robustness, would need to query tool schema
                    if command == "register_user" or command == "login_user":
                        if len(split_args) >= 2:
                            parsed_args["username"] = split_args[0]
                            parsed_args["password"] = split_args[1]
                    elif command in ["get_captions", "get_summarization", "get_statements"]:
                        if len(split_args) >= 2:
                            source_type = split_args[0]
                            value = split_args[1] # This could be URL or raw_text
                            
                            if source_type == "text":
                                parsed_args["raw_text"] = value
                            else:
                                parsed_args[f"{source_type}_url"] = value

                            if command == "get_summarization" and len(split_args) > 2:
                                parsed_args["selectedSize"] = split_args[2]
                                
                    elif command == "fact_check":
                        parsed_args["claim"] = arg_string
                    elif command == "text_to_speech":
                        parsed_args["text"] = arg_string
                    
                    return parsed_args
                
                arguments = parse_args_to_dict(args_str)

                if self.mcp_client:
                    print(f"🤖 Bot: Calling {command} with arguments: {arguments}")
                    result = await self.mcp_client.call_tool(tool_name=command, **arguments)
                    print(f"✅ Result: {json.dumps(result, indent=2)}")
                else:
                    print("❌ MCP client not connected.")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

class ChatInterface:
    """Simple chat interface wrapper."""
    
    def __init__(self, port: int = 6278):
        self.client = FastMCPClient(port)
    
    async def start(self):
        """Start the chat interface."""
        print("🚀 FastMCP Fact Checker Client")
        print("=" * 40)
        
        # Connect to FastMCP server
        if not await self.client.connect():
            print("❌ Failed to connect to FastMCP server. Please ensure:")
            print("   1. FastMCP server is properly configured")
            print("   2. All dependencies are installed")
            print("   3. Fact Checker application is set up correctly")
            return
        
        try:
            # Start interactive chat
            await self.client.interactive_chat()
        finally:
            # Cleanup
            pass # Server is managed externally

async def main():
    """Main entry point."""
    import sys
    
    # Get port from command line or use default
    port = 6278
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"❌ Invalid port number: {sys.argv[1]}")
            print("Usage: python fastmcp_client.py [port]")
            sys.exit(1)
    
    chat = ChatInterface(port)
    await chat.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")

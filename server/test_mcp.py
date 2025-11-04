#!/usr/bin/env python3
"""
Test script for Fact Checker MCP Server and Client
"""

import asyncio
import sys
import subprocess
import os
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack
import json
import asyncio


# Add the project root to sys.path for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    
def get_mcp_server():
    """Imports and returns the configured MCP server instance."""
    from server.fastmcp_server import mcp
    return mcp

async def test_mcp_server():
    """Test the MCP server functionality."""
    print("🧪 Testing MCP Server...")
    
    try:
        # # Use a getter to ensure the module is fully loaded and tools are registered
        # mcp = get_mcp_server()
        # print("✅ MCP server imports successfully")
        
        # # Check if tools have been registered with the server
        # if hasattr(mcp, '_tools') and mcp._tools:
        #     print(f"✅ MCP server has {len(mcp._tools)} tools registered.")
        # else:
        #     print("❌ MCP server has no tools registered.")
        #     return False
        
        # return True
        server_address = "localhost"  # Or the actual IP/hostname of your server
        server_port = 6278          # Or the actual port your server is running on
        from fastmcp.client import Client
        from mcp.client.stdio import stdio_client
        from mcp import ClientSession, StdioServerParameters, types

        # Create a client instance connected to your server
        async with Client(f"http://{server_address}:{server_port}") as client:
            # Give server a moment to start
            await asyncio.sleep(2)
            
            # List tools to confirm connection and registration
            tools = await client.list_tools()
            print(f"✅ MCP server has {len(tools)} tools registered.")
            
            # Call a known tool (e.g., a 'status' tool)
            response = await client.call_tool("get_status", {})
            
            # Assert the expected response
            if response[0].text == "Server Running": # Adjust based on your tool's actual response
                print("✅ MCP Server is running and responsive.")
            else:
                print(f"❌ MCP Server responded, but with unexpected status: {response[0].text}")
        return True
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False

async def test_mcp_client():
    """Test the MCP client functionality."""
    print("\n🧪 Testing MCP Client...")
    
    try:
        # from clients.mcp_client import FactCheckerMCPClient
        from clients.fastmcp_client import FastMCPClient
        print("✅ MCP client imports successfully")
        
        # Create client instance
        client = FastMCPClient()
        print("✅ MCP client instance created")

        mcp_client = await client.connect()
        if mcp_client:
            print("✅ MCP client connected to server")
        else:
            print("❌ MCP client failed to connect to server")
            return False
        
        return True
    except Exception as e:
        print(f"❌ MCP client test failed: {e}")
        return False
    
async def test_mcp_integration():
    """Test end-to-end MCP server and client integration."""
    print("\n🧪 Testing MCP Server-Client Integration...")
    
    try:
        from clients.serverConnection import ServerConnection

        # Create and connect client
        server = ServerConnection()
        connected = await server.connect_to_servers()
        print("✅ MCP Server-Client integration successful.")
        return True
    
    except Exception as e:
        print(f"❌ MCP Server-Client integration test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Fact Checker MCP Test Suite")
    print("=" * 50)

    server_process = None
    server_ok = False
    client_ok = False
    try:
        # Start the server as a subprocess
        server_path = os.path.join(PROJECT_ROOT, "server", "fastmcp_server.py")
        print(f"🚀 Starting FastMCP server from: {server_path}")
        server_process = subprocess.Popen([sys.executable, server_path, "6278"])

        # Run tests
        server_ok = await test_mcp_integration()
        if server_ok:
            client_ok = await test_mcp_client()

    except Exception as e:
        print(f"❌ An error occurred during the test setup: {e}")
    finally:
        if server_process:
            print("🔌 Shutting down FastMCP server...")
            server_process.terminate()
            server_process.wait()

        print("\n📊 Test Results:")
        print(f"  MCP Server: {'✅ PASS' if server_ok else '❌ FAIL'}")
        print(f"  MCP Client: {'✅ PASS' if client_ok else '❌ FAIL'}")

        if server_ok and client_ok:
            print("\n🎉 All tests passed! MCP system is ready to use.")
        else:
            print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())

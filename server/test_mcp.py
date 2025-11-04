#!/usr/bin/env python3
"""
Test script for Fact Checker MCP Server and Client
"""

import asyncio
import sys
import os

async def test_mcp_server():
    """Test the MCP server functionality."""
    print("🧪 Testing MCP Server...")
    
    try:
        from mcp_server import server
        print("✅ MCP server imports successfully")
        
        # Check if server has the expected methods
        if hasattr(server, 'list_tools') and hasattr(server, 'call_tool'):
            print("✅ MCP server has required methods")
        else:
            print("❌ MCP server missing required methods")
            return False
        
        return True
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False

async def test_mcp_client():
    """Test the MCP client functionality."""
    print("\n🧪 Testing MCP Client...")
    
    try:
        from models.mcp_client import FactCheckerMCPClient
        print("✅ MCP client imports successfully")
        
        # Create client instance
        client = FactCheckerMCPClient()
        print("✅ MCP client instance created")
        
        return True
    except Exception as e:
        print(f"❌ MCP client test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Fact Checker MCP Test Suite")
    print("=" * 50)
    
    server_ok = await test_mcp_server()
    client_ok = await test_mcp_client()
    
    print("\n📊 Test Results:")
    print(f"  MCP Server: {'✅ PASS' if server_ok else '❌ FAIL'}")
    print(f"  MCP Client: {'✅ PASS' if client_ok else '❌ FAIL'}")
    
    if server_ok and client_ok:
        print("\n🎉 All tests passed! MCP system is ready to use.")
        print("\nTo start the chat client, run:")
        print("  cd /Users/goyalpushkar/GitHub/factChecker/models")
        print("  python run_client.py")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())

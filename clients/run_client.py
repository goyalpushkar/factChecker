#!/usr/bin/env python3
"""
Simple launcher script for the Fact Checker MCP Client
"""

import os
import sys
import subprocess

def main():
    """Launch the MCP client."""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    client_path = os.path.join(script_dir, "mcp_client.py")
    
    if not os.path.exists(client_path):
        print(f"❌ MCP client not found at {client_path}")
        return
    
    print("🚀 Starting Fact Checker MCP Client...")
    print("=" * 50)
    
    try:
        # Run the MCP client
        subprocess.run([sys.executable, client_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running MCP client: {e}")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()

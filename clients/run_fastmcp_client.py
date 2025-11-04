#!/usr/bin/env python3
"""
Simple launcher script for the FastMCP Fact Checker Client
"""

import os
import sys
import subprocess

def main():
    """Launch the FastMCP client."""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    client_path = os.path.join(script_dir, "fastmcp_client.py")
    
    if not os.path.exists(client_path):
        print(f"❌ FastMCP client not found at {client_path}")
        return
    
    # Get port from command line or use default
    port = 6278
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"❌ Invalid port number: {sys.argv[1]}")
            print("Usage: python run_fastmcp_client.py [port]")
            return
    
    print(f"🚀 Starting FastMCP Fact Checker Client on port {port}...")
    print("=" * 50)
    
    try:
        # Run the FastMCP client
        subprocess.run([sys.executable, client_path, str(port)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running FastMCP client: {e}")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()

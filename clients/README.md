# Fact Checker MCP Client

This directory contains the MCP client for the Fact Checker application, providing a chat interface to interact with the Fact Checker MCP server.

## Files

- **`fastmcp_client.py`** - Main FastMCP client implementation with chat interface
- **`run_fastmcp_client.py`** - Simple launcher script for the FastMCP client
- **`client_requirements.txt`** - Dependencies for the MCP client
- **`README.md`** - This documentation file

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/goyalpushkar/GitHub/factChecker/models
pip install -r client_requirements.txt
```

### 2. Run the FastMCP Server (in /Users/goyalpushkar/GitHub/factChecker/)

```bash
cd /Users/goyalpushkar/GitHub/factChecker
.venv/bin/uvicorn fastmcp_server:mcp --port 6279 --reload
```

### 3. Run the FastMCP Client (in /Users/goyalpushkar/GitHub/factChecker/models/)

```bash
cd /Users/goyalpushkar/GitHub/factChecker/models
python run_fastmcp_client.py 6279 # Use the same port as the server
```

## Features

The FastMCP client provides an interactive chat interface with the following capabilities:

### 📝 Content Processing
- **Extract Captions**: Get captions/transcripts from YouTube videos, audio files, podcasts, and web pages
- **Generate Summaries**: Create summaries with optional size selection (small, medium, large)
- **Extract Statements**: Identify factual statements from various content sources

### 🔍 Fact Checking
- **Verify Claims**: Check the veracity of claims using database lookups, external APIs, and NLP analysis

### 🎵 Audio Processing
- **Text-to-Speech**: Convert text to speech audio files

### 👤 User Management
- **User Registration**: Register new users
- **User Login**: Authenticate users
- **User Logout**: Clear user sessions

## Usage Examples

### Basic Commands

```
💬 You: help
💬 You: quit
```

### User Management

```
💬 You: register_user john_doe mypassword123
💬 You: login_user john_doe mypassword123
💬 You: logout_user
```

### Content Processing

```
💬 You: get_captions youtube https://www.youtube.com/watch?v=example
💬 You: get_summarization text "This is a long text that needs to be summarized..." medium
💬 You: get_statements web https://example.com/article
```

### Fact Checking

```
💬 You: fact_check "The Earth is round"
💬 You: fact_check "Climate change is a hoax"
```

### Text-to-Speech

```
💬 You: text_to_speech "Hello, this is a test message"
```

## Command Reference

| Command | Usage | Description |
|---------|-------|-------------|
| `help` | `help` | Show available commands |
| `register_user` | `register_user <username> <password>` | Register a new user |
| `login_user` | `login_user <username> <password>` | Login user |
| `logout_user` | `logout_user` | Logout current user |
| `get_captions` | `get_captions <source_type> <url>` | Extract captions from media |
| `get_summarization` | `get_summarization <source_type> <url/text> [size]` | Generate summaries |
| `get_statements` | `get_statements <source_type> <url/text>` | Extract factual statements |
| `fact_check` | `fact_check <claim>` | Verify a claim |
| `text_to_speech` | `text_to_speech <text>` | Convert text to speech |
| `quit`/`exit` | `quit` or `exit` | Exit the client |

### Source Types

- `youtube` - YouTube video URLs
- `video` - Direct video file URLs
- `audio` - Direct audio file URLs
- `podcast` - Podcast URLs
- `web` - Web page URLs
- `text` - Raw text input

### Summary Sizes

- `small` - Brief summary
- `medium` - Moderate length summary
- `large` - Detailed summary

## Architecture

The FastMCP client works by:

1. **Starting the FastMCP Server**: Launches the Fact Checker FastMCP server as a subprocess.
2. **Establishing Connection**: Connects to the server via the specified port.
3. **Interactive Chat**: Provides a command-line interface for tool interaction.
4. **Tool Execution**: Sends tool calls to the server and displays results.
5. **Cleanup**: Properly disconnects and terminates the server process.

## Error Handling

The client includes comprehensive error handling:

- **Connection Errors**: Graceful handling of server connection failures
- **Tool Errors**: Clear error messages for tool execution failures
- **Input Validation**: Validation of command syntax and parameters
- **Process Management**: Proper cleanup of server processes

## Troubleshooting

### Common Issues

1. **Connection Failed**: 
   - Ensure the FastMCP server (`fastmcp_server.py`) is running on the correct port.
   - Check that all Fact Checker dependencies are installed.
   - Verify the Fact Checker application is properly configured.

2. **Permission Errors**:
   - Ensure you have read/write permissions in the Fact Checker directory.
   - Check that audio file directories are accessible.

3. **Import Errors**:
   - Install FastMCP dependencies: `pip install fastmcp`
   - Ensure Python path includes the Fact Checker project root.

### Debug Mode

For debugging, you can modify the client to include more verbose logging by adding print statements or using Python's logging module.

## Integration

This FastMCP client can be integrated with:

- **AI Assistants**: Use as a backend for AI-powered fact-checking
- **Web Applications**: Embed in web interfaces
- **Automation Scripts**: Use for automated content processing
- **Research Tools**: Integrate with academic or research workflows

## Development

To extend the client:

1. **Add New Commands**: Modify the `interactive_chat()` method
2. **Enhance Error Handling**: Add more specific error handling
3. **Improve UI**: Add colors, formatting, or GUI elements
4. **Add Features**: Implement additional functionality like batch processing

## Dependencies

The client requires minimal dependencies:

- `fastmcp` - FastMCP implementation
- Standard Python libraries (asyncio, subprocess, json, etc.)

The client automatically manages the FastMCP server process and handles all communication protocols.

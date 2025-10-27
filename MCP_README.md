# Fact Checker MCP Server

This MCP (Model Context Protocol) server exposes the functionality of the Fact Checker application as MCP tools, allowing AI assistants to interact with the fact-checking capabilities programmatically.

## Overview

The Fact Checker MCP Server provides access to various fact-checking and content processing capabilities including:

- **User Management**: Register, login, and logout users
- **Content Extraction**: Extract captions/transcripts from YouTube videos, audio files, podcasts, and web pages
- **Text Processing**: Generate summaries and extract factual statements from content
- **Fact Checking**: Verify claims using database lookups, external APIs, and NLP analysis
- **Text-to-Speech**: Convert text to audio files
- **OAuth Integration**: Google OAuth2 authentication (placeholder implementation)

## Installation

1. Install the required dependencies:
```bash
pip install -r mcp_requirements.txt
```

2. Ensure your Fact Checker application is properly configured with all necessary services and dependencies.

## Available Tools

### 1. `register_user`
Register a new user with username and password.

**Parameters:**
- `username` (string): Username for the new user
- `password` (string): Password for the new user

### 2. `login_user`
Login a user with username and password.

**Parameters:**
- `username` (string): Username for login
- `password` (string): Password for login

### 3. `logout_user`
Logout the current user and clear session.

**Parameters:** None

### 4. `get_captions`
Extract captions/transcripts from various media sources.

**Parameters:** (At least one required)
- `youtube_video_url` (string): YouTube video URL
- `video_url` (string): Direct video file URL
- `audio_url` (string): Direct audio file URL
- `podcast_url` (string): Podcast URL
- `web_url` (string): Web page URL for content extraction

### 5. `get_summarization`
Get summarized content from various sources with optional size selection.

**Parameters:** (At least one required)
- `youtube_video_url` (string): YouTube video URL
- `video_url` (string): Direct video file URL
- `audio_url` (string): Direct audio file URL
- `podcast_url` (string): Podcast URL
- `web_url` (string): Web page URL for content extraction
- `raw_text` (string): Raw text to summarize
- `selectedSize` (string, optional): Size of summary ("small", "medium", "large")

### 6. `get_statements`
Extract factual statements from various media sources.

**Parameters:** (At least one required)
- `youtube_video_url` (string): YouTube video URL
- `video_url` (string): Direct video file URL
- `audio_url` (string): Direct audio file URL
- `podcast_url` (string): Podcast URL
- `web_url` (string): Web page URL for content extraction
- `raw_text` (string): Raw text to extract statements from

### 7. `fact_check`
Check the veracity of a claim using database, external APIs, and NLP analysis.

**Parameters:**
- `claim` (string): The claim to fact-check

### 8. `text_to_speech`
Convert text to speech audio file.

**Parameters:**
- `text` (string): Text to convert to speech
- `action` (string, optional): Action type for TTS processing

### 9. `oauth2_authorize`
Get Google OAuth2 authorization URL (placeholder implementation).

**Parameters:** None

### 10. `oauth2_callback`
Handle OAuth2 callback from Google (placeholder implementation).

**Parameters:**
- `code` (string): Authorization code from Google
- `state` (string): State parameter for OAuth2

## Usage

### Running the MCP Server

```bash
python mcp_server.py
```

``` MCPinspector
npx @modelcontextprotocol/inspector uv run fastmcp_server.py
```

The server will start and listen for MCP protocol messages via stdio.

### Example Tool Calls

#### Register a User
```json
{
  "tool": "register_user",
  "arguments": {
    "username": "testuser",
    "password": "testpass123"
  }
}
```

#### Extract Captions from YouTube Video
```json
{
  "tool": "get_captions",
  "arguments": {
    "youtube_video_url": "https://www.youtube.com/watch?v=example"
  }
}
```

#### Summarize Content
```json
{
  "tool": "get_summarization",
  "arguments": {
    "raw_text": "This is a long text that needs to be summarized...",
    "selectedSize": "medium"
  }
}
```

#### Fact Check a Claim
```json
{
  "tool": "fact_check",
  "arguments": {
    "claim": "The Earth is flat"
  }
}
```

#### Convert Text to Speech
```json
{
  "tool": "text_to_speech",
  "arguments": {
    "text": "Hello, this is a test message"
  }
}
```

## Configuration

The MCP server uses the same configuration as your Fact Checker application. Ensure that:

1. All necessary configuration files are in place (`config.properties`)
2. Database is properly initialized
3. Required directories exist (audio files, session files, etc.)
4. Google OAuth credentials are configured (if using OAuth features)

## Error Handling

The MCP server includes comprehensive error handling:

- Input validation for all required parameters
- Graceful handling of service failures
- Detailed error messages for debugging
- Logging of all operations for troubleshooting

## Dependencies

Key dependencies include:
- `mcp`: Model Context Protocol implementation
- `Flask`: Web framework for the underlying application
- `transformers`: NLP models for fact checking
- `nltk`: Natural language processing
- `gTTS`: Google Text-to-Speech
- `requests`: HTTP requests for external APIs
- `beautifulsoup4`: Web scraping capabilities

## Limitations

1. **OAuth Integration**: The OAuth2 tools are placeholder implementations and would need to be adapted for MCP context
2. **Session Management**: User sessions are not maintained across MCP tool calls
3. **File Serving**: Audio file serving is not directly available through MCP tools
4. **Real-time Processing**: Some operations may take time depending on content size and complexity

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all Fact Checker dependencies are installed
2. **Database Errors**: Verify database configuration and connectivity
3. **Model Loading**: Ensure NLP models are properly downloaded and accessible
4. **File Permissions**: Check permissions for audio file directories

### Logging

The server logs all operations and errors. Check the application logs for detailed information about any issues.

## Contributing

When extending the MCP server:

1. Add new tools to the `handle_list_tools()` function
2. Implement tool logic in the `handle_call_tool()` function
3. Update this README with new tool documentation
4. Add appropriate error handling and validation
5. Test thoroughly with various input scenarios

## License

This MCP server is part of the Fact Checker application. Please refer to the main project license for usage terms.

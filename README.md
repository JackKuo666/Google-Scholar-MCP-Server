# Google Scholar MCP Server
[![smithery badge](https://smithery.ai/badge/@JackKuo666/google-scholar-mcp-server)](https://smithery.ai/server/@JackKuo666/google-scholar-mcp-server)

🔍 Enable AI assistants to search and access Google Scholar papers through a simple MCP interface.
<a href="https://smithery.ai/server/@JackKuo666/google-scholar-mcp-server"><img alt="Smithery Badge" src="https://smithery.ai/badge/@JackKuo666/google-scholar-mcp-server"></a>

The Google Scholar MCP Server provides a bridge between AI assistants and Google Scholar through the Model Context Protocol (MCP). It allows AI models to search for academic papers and access their content in a programmatic way.

## ✨ Core Features
- 🔎 Paper Search: Query Google Scholar papers with custom search strings or advanced search parameters ✅
- 🚀 Efficient Retrieval: Fast access to paper metadata ✅
- 👤 Author Information: Retrieve detailed information about authors ✅
- 📊 Research Support: Facilitate academic research and analysis ✅

## 🚀 Quick Start

### Installing via Smithery

To install google-scholar-mcp-server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@JackKuo666/google-scholar-mcp-server):

```bash
npx -y @smithery/cli install @JackKuo666/google-scholar-mcp-server --client claude
```

### Installing Manually
### Installing via Smithery

To install google-scholar Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@JackKuo666/google-scholar-mcp-server):

#### claude

```sh
npx -y @smithery/cli@latest install @JackKuo666/google-scholar-mcp-server --client claude --config "{}"
```

#### Cursor

Paste the following into Settings → Cursor Settings → MCP → Add new server: 
- Mac/Linux  
```s
npx -y @smithery/cli@latest run @JackKuo666/google-scholar-mcp-server --client cursor --config "{}" 
```
#### Windsurf
```sh
npx -y @smithery/cli@latest install @JackKuo666/google-scholar-mcp-server --client windsurf --config "{}"
```
### CLine
```sh
npx -y @smithery/cli@latest install @JackKuo666/google-scholar-mcp-server --client cline --config "{}"
```

1. Clone the repository:
   ```
   git clone https://github.com/JackKuo666/google-scholar-MCP-Server.git
   cd google-scholar-MCP-Server
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```


For development:

```bash
# Clone and set up development environment
git clone https://github.com/JackKuo666/Google-Scholar-MCP-Server.git
cd Google-Scholar-MCP-Server

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

## 📊 Usage

Start the MCP server:

```bash
python google_scholar_server.py
```

Once the server is running, you can use the provided MCP tools in your AI assistant or application. Here are some examples of how to use the tools:

### Example 1: Search for papers using keywords

```python
result = await mcp.use_tool("search_google_scholar_key_words", {
    "query": "artificial intelligence ethics",
    "num_results": 5
})
print(result)
```

### Example 2: Perform an advanced search

```python
result = await mcp.use_tool("search_google_scholar_advanced", {
    "query": "machine learning",
    "author": "Hinton",
    "year_range": [2020, 2023],
    "num_results": 3
})
print(result)
```

### Example 3: Get author information

```python
result = await mcp.use_tool("get_author_info", {
    "author_name": "Geoffrey Hinton"
})
print(result)
```

These examples demonstrate how to use the three main tools provided by the Google Scholar MCP Server. Adjust the parameters as needed for your specific use case.

## Usage with Claude Desktop

Add this configuration to your `claude_desktop_config.json`:

(Mac OS)

```json
{
  "mcpServers": {
    "google-scholar": {
      "command": "python",
      "args": ["-m", "google_scholar_mcp_server"]
      }
  }
}
```

(Windows version):

```json
{
  "mcpServers": {
    "google-scholar": {
      "command": "C:\\Users\\YOUR\\PATH\\miniconda3\\envs\\mcp_server\\python.exe",
      "args": [
        "D:\\code\\YOUR\\PATH\\Google-Scholar-MCP-Server\\google_scholar_server.py"
      ],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
  }
}
```
Using with Cline
```json
{
  "mcpServers": {
    "google-scholar": {
      "command": "bash",
      "args": [
        "-c",
        "source /home/YOUR/PATH/.venv/bin/activate && python /home/YOUR/PATH/google_scholar_mcp_server.py"
      ],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
  }
}
```


## 🛠 MCP Tools

The Google Scholar MCP Server provides the following tools:

### search_google_scholar_key_words

Search for articles on Google Scholar using key words.

**Parameters:**
- `query` (str): Search query string
- `num_results` (int, optional): Number of results to return (default: 5)

**Returns:** List of dictionaries containing article information

### search_google_scholar_advanced

Perform an advanced search for articles on Google Scholar.

**Parameters:**
- `query` (str): General search query
- `author` (str, optional): Author name
- `year_range` (tuple, optional): Tuple containing (start_year, end_year)
- `num_results` (int, optional): Number of results to return (default: 5)

**Returns:** List of dictionaries containing article information

### get_author_info

Get detailed information about an author from Google Scholar.

**Parameters:**
- `author_name` (str): Name of the author to search for

**Returns:** Dictionary containing author information

## 📁 Project Structure

- `google_scholar_server.py`: The main MCP server implementation using FastMCP
- `google_scholar_web_search.py`: Contains the web scraping logic for searching Google Scholar

## 🔧 Dependencies

- Python 3.10+
- mcp[cli]>=1.4.1
- scholarly>=1.7.0
- asyncio>=3.4.3

You can install the required dependencies using:

```bash
pip install -r requirements.txt
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## ⚠️ Disclaimer

This tool is for research purposes only. Please respect Google Scholar's terms of service and use this tool responsibly.

from typing import Any, List, Dict, Optional, Union
import asyncio
import logging
from mcp.server.fastmcp import FastMCP
from google_scholar_web_search import google_scholar_search, advanced_google_scholar_search
from scholarly import scholarly

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize FastMCP server for PubMed and Google Scholar
mcp = FastMCP("scholar_pubmed")

@mcp.tool()
async def search_google_scholar_key_words(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    logging.info(f"Searching Google Scholar for articles with query: {query}, num_results: {num_results}")
    """
    Search for articles on Google Scholar using key words.

    Args:
        query: Search query string
        num_results: Number of results to return (default: 5)

    Returns:
        List of dictionaries containing article information
    """
    try:
        results = await asyncio.to_thread(google_scholar_search, query, num_results)
        return results
    except Exception as e:
        return [{"error": f"An error occurred while searching Google Scholar: {str(e)}"}]

@mcp.tool()
async def search_google_scholar_advanced(query: str, author: Optional[str] = None, year_range: Optional[tuple] = None, num_results: int = 5) -> List[Dict[str, Any]]:
    logging.info(f"Performing advanced search with parameters: {locals()}")
    """
    Search for articles on Google Scholar using advanced filters.

    Args:
        query: General search query
        author: Author name
        year_range: tuple containing (start_year, end_year)
        num_results: Number of results to return (default: 5)

    Returns:
        List of dictionaries containing article information
    """
    try:
        results = await asyncio.to_thread(
            advanced_google_scholar_search,
            query, author, year_range, num_results
        )
        return results
    except Exception as e:
        return [{"error": f"An error occurred while performing advanced search on Google Scholar: {str(e)}"}]

@mcp.tool()
async def get_author_info(author_name: str) -> Dict[str, Any]:
    logging.info(f"Retrieving author information for: {author_name}")
    """
    Get detailed information about an author from Google Scholar.

    Args:
        author_name: Name of the author to search for

    Returns:
        Dictionary containing author information
    """
    try:
        search_query = scholarly.search_author(author_name)
        # StopIteration cannot propagate through an asyncio Future.
        # A login page can also appear as an empty iterator in scholarly.
        author = await asyncio.to_thread(next, search_query, None)
        if author is None:
            return {
                "error_code": "AUTHOR_RESULTS_UNAVAILABLE",
                "error": (
                    "Google Scholar returned no usable author results. "
                    "The author may not be found, or Google may require sign-in "
                    "or verification. Browser sign-in is not shared with this MCP."
                ),
            }
        filled_author = await asyncio.to_thread(scholarly.fill, author)
        
        # Extract relevant information
        author_info = {
            "name": filled_author.get("name", "N/A"),
            "affiliation": filled_author.get("affiliation", "N/A"),
            "interests": filled_author.get("interests", []),
            "citedby": filled_author.get("citedby", 0),
            "publications": [
                {
                    "title": pub.get("bib", {}).get("title", "N/A"),
                    "year": pub.get("bib", {}).get("pub_year", "N/A"),
                    "citations": pub.get("num_citations", 0)
                }
                for pub in filled_author.get("publications", [])[:5]  # Limit to top 5 publications
            ]
        }
        return author_info
    except Exception as e:
        return {"error": f"An error occurred while retrieving author information: {str(e)}"}

if __name__ == "__main__":
    mcp.run()

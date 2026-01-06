from fastmcp import FastMCP

# Create an MCP server named "EchoVault"
mcp = FastMCP("EchoVault")

@mcp.tool()
def search_history(query: str) -> str:
    """Search the music history for a specific song or artist.
    
    Args:
        query: The song title or artist name to search for.
    """
    # Placeholder: In a real app, this would query your dataset (e.g., tot.parquet)
    return f"Search results for '{query}': No matches found in demo mode."

if __name__ == "__main__":
    mcp.run(transport="stdio")

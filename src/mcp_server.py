import os

import duckdb
from fastmcp import FastMCP

# Create an MCP server named "EchoVault"
mcp = FastMCP("EchoVault")

# Path to the parquet file
PARQUET_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "tot.parquet")


@mcp.tool()
def query_data(sql: str) -> str:
    """Execute a SQL query against the database containing music history.

    Args:
        sql: SQL query to execute. Use 'tot' as the table name.
    """
    try:
        conn = duckdb.connect(":memory:")
        conn.execute(f"CREATE VIEW tot AS SELECT * FROM '{PARQUET_PATH}'")
        result = conn.execute(sql).df()
        return result.to_string()
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")

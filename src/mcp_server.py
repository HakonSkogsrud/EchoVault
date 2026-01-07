import os

import duckdb
from fastmcp import FastMCP

mcp = FastMCP("EchoVault")

PARQUET_PATH_MUSIC = os.path.join(os.path.dirname(__file__), "..", "data", "music_history.parquet")
PARQUET_PATH_YOUTUBE = os.path.join(
    os.path.dirname(__file__), "..", "data", "youtube_history.parquet"
)
PARQUET_PATH_SUBSCRIPTIONS = os.path.join(
    os.path.dirname(__file__), "..", "data", "subscriptions.parquet"
)


@mcp.tool()
def query_music_history(sql: str) -> str:
    """Execute a SQL query against the database containing music history.

    Args:
        sql: SQL query to execute. Use 'music_history' as the table name.
    """
    try:
        conn = duckdb.connect(":memory:")
        conn.execute(f"CREATE VIEW music_history AS SELECT * FROM '{PARQUET_PATH_MUSIC}'")
        result = conn.execute(sql).df()
        return result.to_string()
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def query_youtube_history(sql: str) -> str:
    """Execute a SQL query against the database containing musiyoutube watch history.
        Be aware that channel names changes over time, so use channel_id as channel aggregation column.
    Args:
        sql: SQL query to execute. Use 'youtube_history' as the table name.
    """
    try:
        conn = duckdb.connect(":memory:")
        conn.execute(f"CREATE VIEW youtube_history AS SELECT * FROM '{PARQUET_PATH_YOUTUBE}'")
        result = conn.execute(sql).df()
        return result.to_string()
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def query_youtube_subscriptions(sql: str) -> str:
    """Execute a SQL query against the database containing when a channel was subscribed to.
    Args:
        sql: SQL query to execute. Use 'youtube_history' as the table name.
    """
    try:
        conn = duckdb.connect(":memory:")
        conn.execute(f"CREATE VIEW subscriptions AS SELECT * FROM '{PARQUET_PATH_SUBSCRIPTIONS}'")
        result = conn.execute(sql).df()
        return result.to_string()
    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")

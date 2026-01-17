import os

import duckdb
from fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP("EchoVault")

# Dataset configuration
DATASETS = {
    "music_history": {
        "path": os.path.join(os.path.dirname(__file__), "..", "data", "music_history.parquet"),
        "view_name": "music_history",
        "table_name": "music_history",
    },
    "youtube_history": {
        "path": os.path.join(os.path.dirname(__file__), "..", "data", "youtube_history.parquet"),
        "view_name": "youtube_history",
        "table_name": "youtube_history",
    },
    "subscriptions": {
        "path": os.path.join(os.path.dirname(__file__), "..", "data", "subscriptions.parquet"),
        "view_name": "subscriptions",
        "table_name": "subscriptions",
    },
}


def _execute_query(dataset_key: str, sql: str) -> str:
    """Generic function to execute SQL queries against datasets."""
    try:
        dataset = DATASETS[dataset_key]
        conn = duckdb.connect(":memory:")
        conn.execute(f"CREATE VIEW {dataset['view_name']} AS SELECT * FROM '{dataset['path']}'")
        result = conn.execute(sql).df()
        return result.to_string()
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def get_todays_date() -> str:
    """ Gets todays date. """
    return str(datetime.now())

@mcp.tool()
def query_music_history(sql: str) -> str:
    """Execute a SQL query against the database containing music history.
        Columns: song, artist, time_local, year, month, day, hour
        One row per listening activity.
    Args:
        sql: SQL query to execute. Use 'music_history' as the table name.
    """
    return _execute_query("music_history", sql)


@mcp.tool()
def query_youtube_history(sql: str) -> str:
    """Execute a SQL query against the database containing youtube watch history.
        Be aware that channel names changes over time, so use channel_id as channel aggregation column.
        One row per viewing activity.
        Columns: title, channel_name, time_local, year, month, day, hour, channel_id
    Args:
        sql: SQL query to execute. Use 'youtube_history' as the table name.
    """
    return _execute_query("youtube_history", sql)


@mcp.tool()
def query_youtube_subscriptions(sql: str) -> str:
    """Execute a SQL query against the database containing when a channel was subscribed to.
        One row per time subscribed.
        Columns: channel, time_local, year, month, day, hour
    Args:
        sql: SQL query to execute. Use 'subscriptions' as the table name.
    """
    return _execute_query("subscriptions", sql)


if __name__ == "__main__":
    mcp.run(transport="stdio")

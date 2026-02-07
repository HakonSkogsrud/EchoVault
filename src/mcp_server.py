import os
from datetime import datetime

import duckdb
from fastmcp import FastMCP

mcp = FastMCP("EchoVault")

# Dataset configuration
# Use /data for containerized deployments, fall back to relative path for local development
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))


DUCKDB_INSTRUCTIONS = """
When writing DuckDB queries, strictly follow these rules:
- No Backticks: Use double quotes (") for column names with spaces or special characters (standard SQL syntax).
- No MySQLisms: Avoid MySQL-specific syntax; prioritize PostgreSQL/Standard SQL compatibility.
- Modern SQL: Use the IN operator instead of multiple OR statements for the same column when possible.
- Case-Insensitive Comparisons: Always convert both sides of string comparisons to lowercase using LOWER() to ensure case-insensitive matching (e.g., LOWER("Activity Type") = LOWER('running')).
"""


DATASETS = {
    "music_history": {
        "path": os.path.join(DATA_DIR, "music_history.parquet"),
        "view_name": "music_history",
        "table_name": "music_history",
    },
    "youtube_history": {
        "path": os.path.join(DATA_DIR, "youtube_history.parquet"),
        "view_name": "youtube_history",
        "table_name": "youtube_history",
    },
    "subscriptions": {
        "path": os.path.join(DATA_DIR, "subscriptions.parquet"),
        "view_name": "subscriptions",
        "table_name": "subscriptions",
    },
    "activities": {
        "path": os.path.join(DATA_DIR, "garmin-activities.csv"),
        "view_name": "activities",
        "table_name": "activities",
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
    """Gets todays date."""
    return str(datetime.now())


@mcp.tool()
def describe_table(table_name: str) -> str:
    """Get the schema/column information for a dataset table.

    If you encounter sql errors, use this tool to understand the exact column names,
    data types, and sample values.

    Args:
        table_name: Name of the table to describe. Options: 'activities', 'music_history', 'youtube_history', 'subscriptions'
    """
    if table_name not in DATASETS:
        return (
            f"Error: Unknown table '{table_name}'. Available tables: {', '.join(DATASETS.keys())}"
        )

    try:
        dataset = DATASETS[table_name]
        conn = duckdb.connect(":memory:")
        conn.execute(f"CREATE VIEW {dataset['view_name']} AS SELECT * FROM '{dataset['path']}'")

        # Get schema
        schema = conn.execute(f"DESCRIBE {dataset['view_name']}").df()
        schema_info = "\n".join(
            [f"  - {row['column_name']} ({row['column_type']})" for _, row in schema.iterrows()]
        )

        # Get sample data
        sample = conn.execute(f"SELECT * FROM {dataset['view_name']} LIMIT 3").df()

        return f"""Table: {table_name}

Columns:
{schema_info}

Sample rows:
{sample.to_string()}
"""
    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool()
def query_activities(sql: str) -> str:
    (
        """Execute a SQL query against a database containing Garmin sports activities.

    IMPORTANT: Column names have spaces and must be quoted with double quotes (").
    Use the describe_table('activities') tool to see exact column names.

    Key columns (use double quotes in queries):
    - "Activity Type": Type of activity (Running, Cycling, Swimming, etc.)
    - "Date": Date and time (format: MM/DD/YY HH:MM:SS)
    - "Title": Activity title
    - "Distance": Distance in km or miles
    - "Time": Duration (format: HH:MM:SS)
    - "Avg Speed": Average speed
    - "Max Speed": Maximum speed
    - "Total Ascent": Total elevation gain

    One row per activity.

    """
        + DUCKDB_INSTRUCTIONS
        + """

    Common "Activity Type" values:
        - Running
        - Trail Running
        - Cycling
        - Road Cycling
        - Mountain Biking
        - Gravel Cycling
        - Swimming
        - Pool Swim
        - Open Water Swimming
        - Hiking
        - Strength Training
        - And more...

    Example queries:
        SELECT COUNT(*) FROM activities WHERE LOWER("Activity Type") = LOWER('Running') AND strftime('%Y', "Date") = '2025'
        SELECT "Distance", "Date" FROM activities WHERE LOWER("Activity Type") = LOWER('Cycling') LIMIT 10
        SELECT "Activity Type", COUNT(*) as count FROM activities GROUP BY "Activity Type"

    Args:
        sql: SQL query to execute. Use 'activities' as table name.
    """
    )
    return _execute_query("activities", sql)


@mcp.tool()
def query_music_history(sql: str) -> str:
    (
        """Execute a SQL query against the database containing music history.
        Columns: song, artist, time_local, year, month, day, hour
        One row per listening activity.

    """
        + DUCKDB_INSTRUCTIONS
        + """

    Args:
        sql: SQL query to execute. Use 'music_history' as the table name.
    """
    )
    return _execute_query("music_history", sql)


@mcp.tool()
def query_youtube_history(sql: str) -> str:
    (
        """Execute a SQL query against the database containing youtube watch history.
        Be aware that channel names changes over time, so use channel_id as channel aggregation column.
        One row per viewing activity.
        Columns: title, channel_name, time_local, year, month, day, hour, channel_id

    """
        + DUCKDB_INSTRUCTIONS
        + """

    Args:
        sql: SQL query to execute. Use 'youtube_history' as the table name.
    """
    )
    return _execute_query("youtube_history", sql)


@mcp.tool()
def query_youtube_subscriptions(sql: str) -> str:
    (
        """Execute a SQL query against the database containing when a channel was subscribed to.
        One row per time subscribed.
        Columns: channel, time_local, year, month, day, hour

    """
        + DUCKDB_INSTRUCTIONS
        + """

    Args:
        sql: SQL query to execute. Use 'subscriptions' as the table name.
    """
    )
    return _execute_query("subscriptions", sql)


# @mcp.tool()
# def add(number1: int|float|str, number2: int|float|str) -> str:
#     """ Add two numbers together

#     Args:
#         number1: the first number
#         number2: the second number
#     """
#     return str(float(number1) + float(number2))

# @mcp.tool()
# def add_numbers_from_list(numbers: list[str]) -> str:
#     """ Adds all the numbers from a list together

#     Args:
#         numbers: A list of numbers as str
#     """
#     total = 0
#     for number in numbers:
#         total += float(number)
#     return total

if __name__ == "__main__":
    mcp.run(transport="stdio")

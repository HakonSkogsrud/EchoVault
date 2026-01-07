import io
from functools import lru_cache

import matplotlib

matplotlib.use("Agg")  # Backend for server-side rendering
import matplotlib.pyplot as plt
import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from config import ModelConfig


@lru_cache(maxsize=1)
def get_visualization_llm() -> ChatGoogleGenerativeAI:
    """Get LLM configured for visualization tasks."""
    return ChatGoogleGenerativeAI(
        model=ModelConfig.model,
        temperature=0,  # Use 0 for more deterministic plotting code
        thinking_level="low",  # Less thinking needed for plotting
    )


def create_visualization_agent(df: pd.DataFrame):
    """Create a Pandas DataFrame agent for visualization tasks.

    Args:
        df: The pandas DataFrame to analyze and visualize

    Returns:
        An agent that can write Python code to analyze and plot data
    """
    llm = get_visualization_llm()
    return create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        allow_dangerous_code=True,  # Required for matplotlib plotting
        agent_type="openai-functions",
        max_iterations=15,
        agent_executor_kwargs={"handle_parsing_errors": True},
    )


async def generate_plot(df: pd.DataFrame, user_request: str) -> tuple[str, bytes | None]:
    """Generate a plot based on user request.

    Args:
        df: The pandas DataFrame containing the data
        user_request: The user's request for visualization

    Returns:
        A tuple of (response_text, image_bytes or None)
    """
    # Create the pandas agent
    pandas_agent = create_visualization_agent(df)

    # Enhanced prompt to ensure proper plotting
    enhanced_prompt = f"""{user_request}

IMPORTANT PLOTTING INSTRUCTIONS:
- Create the visualization using matplotlib
- Use clear labels, title, and legend where appropriate
- For large datasets, consider showing only top items (e.g., top 10-20)
- Use appropriate chart types (bar, line, pie, scatter, etc.)
- Rotate x-axis labels if they're long to avoid overlap (plt.xticks(rotation=45, ha='right'))
- Set appropriate figure size for readability (e.g., plt.figure(figsize=(10, 6)))
- After creating the plot, the figure will be automatically captured
- Make sure to use readable colors and proper spacing
"""

    try:
        # Run the agent
        import chainlit as cl

        response = await cl.make_async(pandas_agent.run)(enhanced_prompt)

        # Capture any matplotlib figure that was created
        fig = plt.gcf()
        image_bytes = None

        if fig.get_axes():  # Check if a plot was actually created
            buf = io.BytesIO()
            plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
            buf.seek(0)
            image_bytes = buf.read()
            plt.close(fig)

        return response, image_bytes

    except Exception as e:
        plt.close("all")  # Clean up any figures on error
        return f"Error generating visualization: {str(e)}", None


def parse_dataframe_from_string(data_string: str) -> pd.DataFrame | None:
    """Attempt to parse a DataFrame from the string output of SQL tool.

    Args:
        data_string: String representation of data from SQL query (CSV format)

    Returns:
        A pandas DataFrame if parsing succeeds, None otherwise
    """
    try:
        from io import StringIO

        # Skip empty results
        if (
            not data_string
            or data_string.startswith("Error:")
            or "Empty DataFrame" in data_string
            or len(data_string.strip()) < 5
        ):
            return None

        # The data comes as CSV format from .to_csv()
        df = pd.read_csv(StringIO(data_string))

        return df if len(df) > 0 else None

    except Exception as e:
        # If parsing fails, return None
        print(f"Failed to parse DataFrame: {e}")
        return None

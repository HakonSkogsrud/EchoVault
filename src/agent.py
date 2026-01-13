from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph

from mcp_client import get_mcp_client
from middleware import trim_history
from model import get_model

system_prompt = """
You are an helpful assistant that answers questions from a user about his/her music and listening history.
"""


async def get_agent() -> CompiledStateGraph:
    tools = await get_mcp_client().get_tools()
    return create_agent(
        model=get_model(),
        tools=tools,
        system_prompt=system_prompt,
        middleware=[trim_history],
        checkpointer=InMemorySaver(),
    )

import asyncio
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
import os
import dotenv

dotenv.load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {"EchoVault" :{
        "transport": "stdio",
        "command": "python",
        "args": ["src/mcp_server.py"]
    }}
)

model = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    temperature=0.7,
    thinking_level="medium" 
)

system_prompt="""
You are an helpful assistant that answers questions from a user about his/her music and listening history.
"""

async def create_react_agent():
    tools = await client.get_tools()
    return create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        checkpointer=InMemorySaver(),
    )

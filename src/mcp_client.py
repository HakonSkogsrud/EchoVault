from functools import lru_cache

from langchain_mcp_adapters.client import MultiServerMCPClient


@lru_cache(maxsize=1)
def get_mcp_client() -> MultiServerMCPClient:
    return MultiServerMCPClient(
        {
            "EchoVault": {
                "transport": "stdio",
                "command": "python",
                "args": ["src/mcp_server.py"],
            }
        }
    )

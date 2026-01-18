import os
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
                "env": {
                    "DATA_DIR": os.environ.get(
                        "DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data")
                    )
                },
            }
        }
    )

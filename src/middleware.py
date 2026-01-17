from typing import Any

from langchain.agents import AgentState
from langchain.agents.middleware import before_agent
from langchain.messages import RemoveMessage

from config import MAX_MESSAGE_HISTORY


@before_agent
def trim_history(state: AgentState, runtime: Any) -> dict[str, Any] | None:
    messages = state["messages"]
    if len(messages) > MAX_MESSAGE_HISTORY:
        messages_to_remove = messages[:-MAX_MESSAGE_HISTORY]
        return {"messages": [RemoveMessage(id=m.id) for m in messages_to_remove]}
    return None

import json
import uuid
from dataclasses import dataclass

import chainlit as cl

from agent import get_agent


@cl.on_chat_start
async def start_chat() -> None:
    thread_id = str(uuid.uuid4())
    cl.user_session.set("thread_id", thread_id)

    agent = await get_agent()
    cl.user_session.set("agent", agent)


@dataclass
class Context:
    MODEL = "model"
    TOOL = "tools"


@cl.on_message
async def main(message: cl.Message) -> None:
    user_input = {"messages": [{"role": "user", "content": message.content}]}
    thread_id = cl.user_session.get("thread_id")
    agent = cl.user_session.get("agent")

    async for chunk in agent.astream(
        user_input, {"configurable": {"thread_id": thread_id}}, stream_mode="updates"
    ):
        if Context.MODEL in chunk:
            if is_tool_call(chunk):
                tool_name = extract_tool_name(chunk)
                query = extract_sql_query(chunk)
                if query:
                    async with cl.Step(name=tool_name, language="sql") as step:
                        step.output = extract_sql_query(chunk)

            else:
                answer = extract_output(chunk, Context.MODEL)
                final_answer = cl.Message(content=answer)
                await final_answer.send()

        if Context.TOOL in chunk:
            async with cl.Step(name="Tool output", type="retrieval") as step:
                step.output = extract_output(chunk, Context.TOOL)


def extract_output(chunk: dict, context: str) -> str:
    return chunk[context]["messages"][-1].content[-1]["text"]


def extract_tool_name(chunk: dict) -> str:
    return chunk["model"]["messages"][-1].additional_kwargs["function_call"]["name"]


def extract_sql_query(chunk: dict) -> str | None:
    query_dict_str = chunk["model"]["messages"][-1].additional_kwargs["function_call"]["arguments"]
    query_dict = json.loads(query_dict_str)
    if query_dict:
        return query_dict["sql"]
    return None


def is_tool_call(chunk: dict) -> bool:
    model = chunk["model"]
    return not model["messages"][-1].content

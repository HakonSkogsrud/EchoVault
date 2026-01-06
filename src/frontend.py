import uuid

import chainlit as cl

from agent import create_react_agent


@cl.on_chat_start
async def start_chat() -> None:
    thread_id = str(uuid.uuid4())
    cl.user_session.set("thread_id", thread_id)

    agent = await create_react_agent()
    cl.user_session.set("agent", agent)

    await cl.Message(content="Hva kan jeg hjelpe deg med?").send()


@cl.on_message
async def main(message: cl.Message) -> None:
    final_answer = cl.Message(content="")
    await final_answer.send()

    user_input = {"messages": [{"role": "user", "content": message.content}]}
    thread_id = cl.user_session.get("thread_id")
    agent = cl.user_session.get("agent")

    async for chunk in agent.astream(
        user_input, {"configurable": {"thread_id": thread_id}}, stream_mode="messages"
    ):
        msg, metadata = chunk
        if metadata.get("langgraph_node") == "model" and msg.content:
            if isinstance(msg.content, list):
                text = "".join(
                    block.get("text", "") for block in msg.content if block.get("type") == "text"
                )
                final_answer.content += text
            else:
                final_answer.content += msg.content
            await final_answer.update()

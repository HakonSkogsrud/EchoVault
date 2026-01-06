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
    final_answer = cl.Message(content="Tenker...")
    await final_answer.send()

    user_input = {"messages": [{"role": "user", "content": message.content}]}
    thread_id = cl.user_session.get("thread_id")
    agent = cl.user_session.get("agent")

    response = await agent.ainvoke(user_input, {"configurable": {"thread_id": thread_id}})

    last_message = response["messages"][-1]

    if hasattr(last_message, "content_blocks") and last_message.content_blocks:
        content = "".join(
            [b["text"] for b in last_message.content_blocks if b.get("type") == "text"]
        )
    else:
        content = last_message.content

    final_answer.content = content
    await final_answer.update()

import json
import uuid
from dataclasses import dataclass

import matplotlib

matplotlib.use("Agg")  # Must be set before importing pyplot

import chainlit as cl

from agent import get_agent
from visualization_agent import generate_plot, parse_dataframe_from_string


@cl.on_chat_start
async def start_chat() -> None:
    thread_id = str(uuid.uuid4())
    cl.user_session.set("thread_id", thread_id)
    cl.user_session.set("last_dataframe", None)  # Store last query result

    agent = await get_agent()
    cl.user_session.set("agent", agent)


@dataclass
class Context:
    MODEL = "model"
    TOOL = "tools"


def is_visualization_request(message: str) -> bool:
    """Detect if the user is asking for a visualization."""
    viz_keywords = [
        "plot",
        "chart",
        "graph",
        "visualize",
        "visualization",
        "show me",
        "bar chart",
        "pie chart",
        "line chart",
        "scatter",
        "histogram",
        "distribution",
        "trend",
    ]
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in viz_keywords)


@cl.on_message
async def main(message: cl.Message) -> None:
    user_input = {"messages": [{"role": "user", "content": message.content}]}
    thread_id = cl.user_session.get("thread_id")
    agent = cl.user_session.get("agent")

    # Check if this is a visualization request and we have data
    last_df = cl.user_session.get("last_dataframe")
    is_viz_request = is_visualization_request(message.content)

    # If it's a visualization request and we have data, use the Pandas agent directly
    if is_viz_request and last_df is not None and len(last_df) > 0:
        async with cl.Step(name="Generating Visualization", type="tool") as step:
            response_text, image_bytes = await generate_plot(last_df, message.content)
            step.output = (
                "Visualization generated successfully" if image_bytes else "No plot created"
            )

        if image_bytes:
            image = cl.Image(content=image_bytes, name="chart", display="inline")
            await cl.Message(content=response_text, elements=[image]).send()
        else:
            await cl.Message(content=response_text).send()
        return

    # Otherwise, process normally with the main agent
    async for chunk in agent.astream(
        user_input, {"configurable": {"thread_id": thread_id}}, stream_mode="updates"
    ):
        if Context.MODEL in chunk:
            if is_tool_call(chunk):
                tool_name = extract_tool_name(chunk)
                async with cl.Step(name=tool_name, language="sql") as step:
                    step.output = extract_sql_query(chunk)

            else:
                answer = extract_output(chunk, Context.MODEL)
                final_answer = cl.Message(content=answer)
                await final_answer.send()

        if Context.TOOL in chunk:
            tool_output = extract_output(chunk, Context.TOOL)

            async with cl.Step(name="Query Result", type="retrieval") as step:
                step.output = tool_output

            # Try to parse the tool output as a DataFrame for future visualization
            df = parse_dataframe_from_string(tool_output)
            
            if df is not None:
                print(f"Successfully parsed DataFrame with shape: {df.shape}")
                print(f"DataFrame columns: {df.columns.tolist()}")
                cl.user_session.set("last_dataframe", df)

                # If this was a visualization request, automatically generate the plot
                if is_viz_request:
                    print("Generating visualization...")
                    async with cl.Step(name="Generating Visualization", type="tool") as viz_step:
                        response_text, image_bytes = await generate_plot(df, message.content)
                        viz_step.output = "Visualization generated"

                    if image_bytes:
                        image = cl.Image(content=image_bytes, name="chart", display="inline")
                        # Send the visualization
                        await cl.Message(
                            content=f"{response_text}", elements=[image]
                        ).send()
            else:
                print(f"Failed to parse DataFrame from tool output. First 200 chars: {tool_output[:200]}")


def extract_output(chunk: dict, context: str) -> str:
    return chunk[context]["messages"][-1].content[-1]["text"]


def extract_tool_name(chunk: dict) -> str:
    return chunk["model"]["messages"][-1].additional_kwargs["function_call"]["name"]


def extract_sql_query(chunk: dict) -> str:
    query_dict_str = chunk["model"]["messages"][-1].additional_kwargs["function_call"]["arguments"]
    query_dict = json.loads(query_dict_str)
    return query_dict["sql"]


def is_tool_call(chunk: dict) -> bool:
    model = chunk["model"]
    if model["messages"][-1].content:
        return False
    return True

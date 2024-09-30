import chainlit as cl
from chainlit.input_widget import Select, Slider
from agents.stock_analysis_function_calling import create_agent
from utils import calculate_token_count_of_message
from llama_index.core.callbacks import CallbackManager
from termcolor import colored
import asyncio
import uuid
import json
import os

MAX_CONTEXT_LENGTH = 4000  # Adjust this based on your model's context window


async def save_chat_history(messages, filename, dir: str = "./history"):
    """Save the chat history"""
    os.makedirs(dir, exist_ok=True)
    with open(os.path.join(dir, filename), "w") as fp:
        json.dump(messages, fp)


# @cl.oauth_callback
# def oauth_callback(
#     provider_id: str,
#     token: str,
#     raw_user_data: Dict[str, str],
#     default_user: cl.User,
# ) -> Optional[cl.User]:
#     if provider_id == "google":
#         if raw_user_data["hd"] == "bridgeweave.com":
#             return default_user
#     return None


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Stock Analysis",
            message="How is Reliance performing? Create a detailed report.",
            icon="./public/starters/idea.svg",
        ),
        cl.Starter(
            label="Explain metrics",
            message="Explain P/E ratio like I'm five years old",
            icon="./public/starters/learn.svg",
        ),
        cl.Starter(
            label="Fetch specific metrics",
            message="What is the earnings per share ratio of Reliance",
            icon="./public/starters/write.svg",
        ),
    ]


@cl.on_chat_start
async def start():
    print(colored("[UI]: Starting Chat", color="light_cyan"))
    settings = await cl.ChatSettings(
        [
            Select(
                id="model_service",
                label="Model Service",
                values=["groq", "ollama"],
                initial_index=0,
            ),
            Select(
                id="model_name",
                label="Model",
                values=[
                    # Groq
                    "llama-3.1-70b-versatile",
                    "llama3-groq-8b-8192-tool-use-preview",
                    "llama-3.1-8b-instant",
                    "llama3-8b-8192",
                    # Ollama
                    "llama3.1:latest",
                    "qwen2.5:3b",
                ],
                initial_index=0,
            ),
            Select(
                id="system_prompt",
                label="PROMPT",
                values=[
                   "base",
                   "diy-investor"
                ],
                initial_index=0,
            ),
            Slider(
                id="temperature",
                label="Temperature",
                initial=0.1,
                min=0,
                max=1,
                step=0.01,
            ),
            Slider(
                id="top_k",
                label="Top K",
                initial=0.95,
                min=0.1,
                max=1,
                step=0.01,
                description="Controls diversity by limiting the next token prediciton to the top K probabilites.",
            ),
            Slider(
                id="top_p",
                label="Top K",
                initial=1,
                min=0,
                max=1,
                step=0.01,
                description="Controls diversity via nucleus sampling: 0.5 means half of all likelihood-weighted options are considered.",
            ),
            Slider(
                id="max_tokens",
                label="Max Tokens",
                initial=1024,
                min=256,
                max=2048,
                step=2,
                description="The maxium number of tokens to generate at each call.",
            ),
        ]
    ).send()
    # set the message history
    cl.user_session.set("message_history", [])

    await setup_agent(settings)
    # set the session id
    session_id = uuid.uuid1()
    cl.user_session.set("session_id", session_id)

    # await cl.Message(
    #     content="Welcome to the Stock Analysis Assistant! How can I help you today?"
    # ).send()
    print(colored(f"[UI]: Session id: {session_id}", color="light_cyan"))


@cl.on_settings_update
async def setup_agent(settings):
    """Set up the agent based on the settings update"""
    # get the callback manager
    callback_manager = CallbackManager(handlers=[cl.LlamaIndexCallbackHandler()])

    try:
        # create the agent
        agent = create_agent(
            model_name=settings["model_name"],
            callback_manager=callback_manager,
            model_service=settings["model_service"],
            generation_kwargs=settings,
        )

        # add agent to the user session
        cl.user_session.set("agent", agent)
    except Exception as e:
        await cl.Message(author="System", content=f"An Error occurred while initializing the agent: {e}")
        raise e


@cl.on_message
async def main(message: cl.Message):
    query = message.content
    message_history = cl.user_session.get("message_history")

    # Send a thinking message
    thinking_msg = cl.Message(
        content="Thinking... this may take a moment.",
        elements=[
            cl.Image(path="./public/buffering.png", display="side", size="small")
        ],
    )
    await thinking_msg.send()

    try:
        await asyncio.sleep(1)
        # Perform the stock analysis
        agent = cl.user_session.get("agent")

        result = await cl.make_async(agent.chat)("\n".join(message_history + [query]))

        print(colored(f"[AGENT RESPONSE]: {result.response}", color="magenta"))

        # Add the query and response to the message history
        message_history.append(f"Human: {query}")
        message_history.append(f"Assistant: {result.response}")

        # Limit the context length
        while (
            calculate_token_count_of_message("\n".join(message_history))
            > MAX_CONTEXT_LENGTH
        ):
            message_history.pop(0)

        # Update the user session with the new message history
        cl.user_session.set("message_history", message_history)

        out_message = cl.Message(author="Agent", content="")
        # a facade for streaming
        for char in result.response:
            await out_message.stream_token(char)

        # Remove the thinking message
        await thinking_msg.remove()

        # print("here")
        # Send a new message with the result instead of updating
        await out_message.send()
        # save chat history
        id = cl.user_session.get("session_id")
        await save_chat_history(
            messages=message_history, filename=f"chat_history_{id}.json"
        )

    except Exception as e:
        print(colored(f"[EXCEPTION]: {e}", color="red"))
        # If there's an error, send a new message with the error
        await cl.Message(content=f"An error occurred: {str(e)}").send()

        # remove the thinking message
        await thinking_msg.remove()


if __name__ == "__main__":
    cl.run()

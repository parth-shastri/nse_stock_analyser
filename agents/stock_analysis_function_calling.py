from typing import Optional, Any, Literal
from llama_index.llms.groq import Groq
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import FunctionCallingAgent, AgentRunner
from llama_index.core import Settings
from llama_index.core.prompts import ChatMessage
from tools.tools import stock_analyser, duckduckgo_search_tool
from typing import List
from dotenv import load_dotenv
from prompts.functioncalling_prompts import ANALYSIS_PROMPT
from termcolor import colored

# Load the env variables
load_dotenv("./secrets/local.env")


def create_agent(model_name: str = "llama-3.1-70b-versatile", callback_manager: Optional[Any] = None, model_service: Literal["groq", "ollama", "huggingface"] = "groq", generation_kwargs: dict[str, Any] = None) -> AgentRunner:
    """Create and return a new agent instance."""
    try:
        if model_service == "groq":
            llm = Groq(model=model_name, request_timeout=120.0)
        elif model_service == "ollama":
            llm = Ollama(model=model_name, request_timeout=120.0)
        else:
            raise NotImplementedError(f"The model_service {model_service} is not implemented.")
    except Exception as e:
        raise ValueError(f"Error loading model from {model_service} please check the model_name / model_service passed. Found={model_name}: {e}")

    # set the llm & the generation args
    Settings.llm = llm
    Settings.context_window = 4096  # default
    Settings.output_tokens = generation_kwargs.get("max_tokens", 1024)
    Settings.temperature = generation_kwargs.get("temperature", 0.1)

    system_prompt = ANALYSIS_PROMPT
    print(colored(f"[AGENT CREATION]: Using system_prompt as {generation_kwargs.get('system_prompt')}", color="light_magenta"))
    prefix_messages = [ChatMessage(role="system", content=system_prompt)]

    return FunctionCallingAgent.from_tools(
        llm=llm,
        tools=[stock_analyser, duckduckgo_search_tool],
        prefix_messages=prefix_messages,
        max_function_calls=3,
        callback_manager=callback_manager,
        verbose=True,
    )


def analyze_stock(query: str, chat_history: List[str]) -> str:
    """
    Analyze a stock based on the given query and chat history.

    Args:
        query (str): The user's query about a stock.
        chat_history (List[str]): List of previous messages in the chat.

    Returns:
        str: The analysis result.
    """
    agent = create_agent()

    # Combine chat history and current query
    context = "\n".join(chat_history + [query])

    # Use the combined context for the analysis
    response = agent.chat(context)
    return response.response

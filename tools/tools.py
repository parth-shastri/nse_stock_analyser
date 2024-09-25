from llama_index.core.tools import FunctionTool
# from llama_index.tools.brave_search import BraveSearchToolSpec
from tools.functions import analyse_company_yf, yf_fundamental_analysis, get_recent_news, duckduckgo_search

# init tools
stock_analyser = FunctionTool.from_defaults(fn=analyse_company_yf, name="analyse_company")
fundamental_analyser = FunctionTool.from_defaults(fn=yf_fundamental_analysis)
news_fetcher = FunctionTool.from_defaults(fn=get_recent_news)

duckduckgo_search_tool = FunctionTool.from_defaults(fn=duckduckgo_search)
# brave_search = BraveSearchToolSpec().to_tool_list()[0]

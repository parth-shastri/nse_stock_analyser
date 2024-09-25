from datetime import datetime
import json
import yfinance as yf
from pydantic import Field
import regex as re
from tools.utils import get_nse_tickers_scraping

# imports for util models
# from llama_index.llms.ollama import Ollama
from llama_index.llms.groq import Groq
from llama_index.tools.duckduckgo import DuckDuckGoSearchToolSpec

# from llama_index.core.program import FunctionCallingProgram
from llama_index.core.prompts import PromptTemplate
from agents.output_types import CompanyName, Ticker

# Make the search tool
search = DuckDuckGoSearchToolSpec().duckduckgo_full_search


def duckduckgo_search(
    query: str = Field(description="Search query to be executed"),
) -> str:
    """
    Get search results using DuckDuckGo.

    This function performs a search query using DuckDuckGo and returns the results
    as a formatted string.

    Args:
        query (str): The search query to be executed.

    Returns:
        str: A formatted string containing the search results, including titles,
             body snippets, and source URLs.

    Example:
        >>> result = duckduckgo_search("Python programming")
        >>> print(result)
        Search Results:
        Title: Python (programming language) - Wikipedia
        Body: Python is a high-level, general-purpose programming language...
        Sources: https://en.wikipedia.org/wiki/Python_(programming_language)
        ...
    """
    response = "\nSearch Results:\n"
    results = search(query, region="in")
    for result in results:
        response += f"Title: {result['title']}\n"
        response += f"Body: {result['body']}\n"
        response += f"Sources: {result['href']}\n"

    return response


def get_recent_news(
    ticker: str = Field(description="the ticker/trading symbol of the company"),
):
    """
    Get recent news for a given stock ticker using DuckDuckGo search.

    This function retrieves recent news articles related to the specified stock ticker
    using the DuckDuckGo search tool and formats the results as a string.

    Args:
        ticker (str): The stock ticker symbol to search for news.

    Returns:
        str: A formatted string containing recent news articles, including titles,
             article snippets, and source URLs.

    Example:
        >>> news = get_recent_news("AAPL")
        >>> print(news)
        ## Recent news for AAPL
        Title: Apple Reports Third Quarter Results
        Article: Apple today announced financial results for its fiscal 2023 third quarter...
        Sources: https://www.apple.com/newsroom/2023/08/apple-reports-third-quarter-results/
        ...
    """
    news_list = search(
        f"{ticker} recent news on {datetime.now().strftime('%d %B %Y')}", max_results=5
    )
    news = f"\n## Recent news for {ticker}\n"
    for doc in news_list:
        news += f"Title: {doc['title']}\n"
        news += f"Article: {doc['body']}\n"
        news += f"Sources: {doc['href']}\n"

    return news


# yahoo finance financials fetcher
def yf_get_financial_statements(
    ticker: str = Field(description="the ticker/trading symbol of the company"),
) -> str:
    """Fetches the financial statements data from yahoo finance.

    Args:
        ticker (str): The ticker symbol of the company to fetch information for.

    Returns:
        str: A string containing the financial statement data in a formatted way.
    """

    if "." in ticker:
        ticker = ticker.split(".")[0]

    ticker += ".NS"
    company = yf.Ticker(ticker)
    balance_sheet = company.balance_sheet
    if balance_sheet.shape[-1] > 3:
        balance_sheet = balance_sheet.iloc[:, :3]

    balance_sheet = balance_sheet.dropna(how="any")
    # Convert the sheet to Cr.
    balance_sheet = balance_sheet.multiply(1e-7)
    # rename the index
    balance_sheet.rename(
        index={name: f"{name} (in Crores.)" for name in balance_sheet.index},
        inplace=True,
    )
    # convert to string
    balance_sheet = "\n" + balance_sheet.to_string()

    return balance_sheet


# get stock info and recommendations summary
def yf_get_stockinfo(
    ticker: str = Field(description="the ticker/trading symbol of the company"),
) -> str:
    """Provides the detailed financial and general information about the stock ticker.
        Also provides a table for analyst recommendations for the ticker.

    Args:
        ticker (str): The ticker symbol of the company to fetch information for.

    Returns:
        str: A string containing the stock info and a summary of recommendations.
    """

    if "." in ticker:
        ticker = ticker.split(".")[0]

    ticker += ".NS"

    company = yf.Ticker(ticker)

    stock_info = company.info
    try:
        recommendations_summary = company.recommendations_summary
    except Exception as e:
        print(f"No recommendations {e}")
        recommendations_summary = ""

    # TODO: add units and convert to easily understandable units

    include_info = [
        "industry",
        "sector",
        "longBuisnessSummary",
        "previousClose",
        "dividendRate",
        "dividentYield",
        "beta",
        "forwardPE",
        "volume",
        "marketCap",
        "fiftyTwoWeekLow",
        "fiftyTwoWeekHigh",
        "currency",
        "bookValue",
        "priceToBook",
        "earningsQuarterlyGrowth",
        "trailingEps",
        "forwardEps",
        "52WeekChange",
        "totalCashPerShare",
        "ebidta",
        "totabDebt",
        "totalCashPerShare",
        "debtToEquity",
        "revenuePerShare",
        "earningsGrowth",
        "revenueGrowth",
        "grossMargins",
        "ebidtaMargins",
        "operatingMargins",
    ]
    response = "## Stock info:\n"

    for key, val in stock_info.items():
        if key in include_info:
            if re.search("(Growth|Margin|Change)", key):
                response += f"{key}: {round(float(val) * 100, 3)} %\n"
            elif "marketCap" in key:
                response += f"{key}: {round(int(val) * 1e-7, 2)} Cr.\n"
            else:
                response += f"{key}: {val}\n"

    response += "\n## Analyst Recommendations:\n"
    response += f"\n{recommendations_summary}"

    return response


def yf_fundamental_analysis(
    ticker: str = Field(description="the ticker/trading symbol of the company"),
):
    """
    Perform a comprehensive fundamental analysis on the given stock symbol.
    A great function from https://github.com/YBSener/financial_Agent/blob/main/tools/yf_fundamental_analysis_tool.py

    Args:
        stock_symbol (str): The stock symbol to analyze.

    Returns:
        dict: A dictionary with the detailed fundamental analysis results.
    """
    try:
        if "." in ticker:
            ticker = ticker.split(".")[0]

        stock = yf.Ticker(ticker)
        info = stock.info

        # Data processing
        financials = stock.financials.infer_objects(copy=False)
        balance_sheet = stock.balance_sheet.infer_objects(copy=False)
        cash_flow = stock.cashflow.infer_objects(copy=False)

        # Fill missing values
        financials = financials.ffill()
        balance_sheet = balance_sheet.ffill()
        cash_flow = cash_flow.ffill()

        # Key Ratios and Metrics
        ratios = {
            "P/E Ratio": info.get("trailingPE"),
            "Forward P/E": info.get("forwardPE"),
            "P/B Ratio": info.get("priceToBook"),
            "P/S Ratio": info.get("priceToSalesTrailing12Months"),
            "PEG Ratio": info.get("pegRatio"),
            "Debt to Equity": info.get("debtToEquity"),
            "Current Ratio": info.get("currentRatio"),
            "Quick Ratio": info.get("quickRatio"),
            "ROE": info.get("returnOnEquity"),
            "ROA": info.get("returnOnAssets"),
            "ROIC": info.get("returnOnCapital"),
            "Gross Margin": info.get("grossMargins"),
            "Operating Margin": info.get("operatingMargins"),
            "Net Profit Margin": info.get("profitMargins"),
            "Dividend Yield": info.get("dividendYield"),
            "Payout Ratio": info.get("payoutRatio"),
        }

        # Growth Rates
        revenue = financials.loc["Total Revenue"]
        net_income = financials.loc["Net Income"]
        revenue_growth = (
            revenue.pct_change(periods=-1).iloc[0] if len(revenue) > 1 else None
        )
        net_income_growth = (
            net_income.pct_change(periods=-1).iloc[0] if len(net_income) > 1 else None
        )

        growth_rates = {
            "Revenue Growth (YoY)": revenue_growth,
            "Net Income Growth (YoY)": net_income_growth,
        }

        # Valuation
        market_cap = info.get("marketCap")
        enterprise_value = info.get("enterpriseValue")

        valuation = {
            "Market Cap": market_cap,
            "Enterprise Value": enterprise_value,
            "EV/EBITDA": info.get("enterpriseToEbitda"),
            "EV/Revenue": info.get("enterpriseToRevenue"),
        }

        # Future Estimates
        estimates = {
            "Next Year EPS Estimate": info.get("forwardEps"),
            "Next Year Revenue Estimate": info.get("revenueEstimates", {}).get("avg"),
            "Long-term Growth Rate": info.get("longTermPotentialGrowthRate"),
        }

        # Simple DCF Valuation (very basic)
        free_cash_flow = (
            cash_flow.loc["Free Cash Flow"].iloc[0]
            if "Free Cash Flow" in cash_flow.index
            else None
        )
        wacc = 0.1  # Assumed Weighted Average Cost of Capital
        growth_rate = info.get("longTermPotentialGrowthRate", 0.03)

        def simple_dcf(fcf, growth_rate, wacc, years=5):
            if fcf is None or growth_rate is None:
                return None
            terminal_value = fcf * (1 + growth_rate) / (wacc - growth_rate)
            dcf_value = sum(
                [
                    fcf * (1 + growth_rate) ** i / (1 + wacc) ** i
                    for i in range(1, years + 1)
                ]
            )
            dcf_value += terminal_value / (1 + wacc) ** years
            return dcf_value

        dcf_value = simple_dcf(free_cash_flow, growth_rate, wacc)

        # Prepare the results
        analysis = {
            "Company Name": info.get("longName"),
            "Sector": info.get("sector"),
            "Industry": info.get("industry"),
            "Key Ratios": ratios,
            "Growth Rates": growth_rates,
            "Valuation Metrics": valuation,
            "Future Estimates": estimates,
            "Simple DCF Valuation": dcf_value,
            "Last Updated": datetime.fromtimestamp(
                info.get("lastFiscalYearEnd", 0)
            ).strftime("%Y-%m-%d"),
            "Data Retrieval Date": datetime.now().strftime("%Y-%m-%d"),
        }

        # Add interpretations
        interpretations = {
            "P/E Ratio": (
                "High P/E might indicate overvaluation or high growth expectations"
                if ratios.get("P/E Ratio", 0) > 16
                else "Low P/E might indicate undervaluation or low growth expectations"
            ),
            "Debt to Equity": (
                "High leverage"
                if ratios.get("Debt to Equity", 0) > 2
                else "Conservative capital structure"
            ),
            "ROE": (
                "Couldn't find ROE"
                if not ratios.get("ROE", 0.0)
                else (
                    "Strong returns"
                    if ratios.get("ROE", 0.0) > 0.15
                    else "Potential profitability issues"
                )
            ),
            "Revenue Growth": (
                "Strong growth"
                if growth_rates.get("Revenue Growth (YoY)", 0) > 0.1
                else "Slowing growth"
            ),
        }

        analysis["Interpretations"] = interpretations

        return analysis

    except Exception as e:
        return f"An error occurred during the analysis: {e}"


def analyse_company_yf(
    company_name: str = Field(
        description="The name of the company", pattern=r"""^\w[\w.\-#&\s]*$"""
    ),
) -> str:
    """Perform analysis on the company specified in the input query.

    This function takes a query about a company,
    finds its ticker symbol, retrieves financial statements and stock information,
    Args:
        company_name (str): The input query containing the company name to analyze.

    Returns:
        str: A string containing the financial statements and stock information
             of the specified company."""

    try:
        # model = Ollama(model="qwen2.5:3b", request_timeout=120.0)
        # Check if the company is on the NSE
        model = Groq(model="llama3-groq-8b-8192-tool-use-preview")

        company = CompanyName(company_name=company_name)
        # get the ticker
        search_result = search(
            f"What is the NSE ticker symbol for {company.company_name}",
            region="in",
            max_results=5,
        )
        # use a function calling program
        ticker_extraction_prompt = PromptTemplate(
            """
            Extract the ticker / company symbol from the input search result :
            {search_result}
            """
        )
        ticker = model.structured_predict(
            output_cls=Ticker,
            prompt=ticker_extraction_prompt,
            search_result=search_result,
        )
        print(ticker)

        # check if the ticker is present in the nse list
        nse_list = get_nse_tickers_scraping()
        if nse_list and ticker.company_symbol.split(".")[0] not in nse_list:
            return "The ticker is not a part of NSE India"

        # get fundamental analysis, financials & info
        fundamental_analysis = yf_fundamental_analysis(ticker.company_symbol)
        financials = yf_get_financial_statements(ticker.company_symbol)
        info = yf_get_stockinfo(ticker.company_symbol)

        # get recent news
        news = get_recent_news(ticker.company_symbol)

        return "\n".join([json.dumps(fundamental_analysis), info, financials, news])

    except Exception as e:
        return f"Error fetching data, Please try again: {e}"

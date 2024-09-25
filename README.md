**Stock Analysis Assistant**
==========================

**Description**
---------------

Stock Analysis Assistant is an AI-powered tool designed to help users analyze stocks and generate reports based on their financial statements, fundamentals & real-time web data.

**Features**
------------

### Stock Analysis

* Analyze stock performance based on its financial statements
* Generate detailed analysis, pros, cons, and additional notes
* Get the latest news and fundamental ratios of a given stock.

### DuckDuckGo Search Tool

* Fetch real-time information from DuckDuckGo using a search tool integrated into the assistant

### Function Calling Agent

* Execute specific functions from various tools and models using the function calling agent
* Enable more complex analysis by combining results from multiple sources

**Usage**
---------

1. **Starters**: Use pre-defined prompts for common stock-related questions
2. **Agent Chat**: Interact with the assistant by asking questions or providing prompts
3. **Function Calling Agent**: Execute specific functions from various tools and models using the function calling agent

**Models**
----------

### Model Selection

You can choose to use either of the following model services, which are interchangeable and provide similar functionality.

#### Default: Groq (Llama 3.1-70b-versatile)

* A Groq model (llama 3.1-70b-versatile) is used for generating reports and providing analysis by default

#### Alternative: Ollama (Llama 3.1)

* An Ollama model (Llama 3.1) can be used as an alternative to the Groq model, providing similar functionality
* To switch to the Ollama model, run `ollama list` for available models and select one

Note: For a complete list of available models and to check their availability, please refer to the Groq website or run `ollama list`.

**Tools**
---------

### Stock Analyser

* A stock analyser tool is used for analyzing stock performance based on financial statements & fundamental data fetched from the Yahoo Finance API.

### DuckDuckGo Search Tool

* A DuckDuckGo search tool is used to fetch real-time information

**Setup and Requirements**
---------------------------

### Prerequisites

* Python 3.8 or later
* Groq API key (llama-3.1-70b-versatile)
* Ollama installed, and the required model pulled.
* DuckDuckGo API key
* Stock analyser tool

**Installation**
---------------

To install the project, follow these steps:

### Using `pip` with a virtual environment (venv)

1. Create a new virtual environment using `python -m venv env`
2. Activate the environment by running `source env/bin/activate` on Linux/Mac or `env\Scripts\activate` on Windows
3. Install dependencies from `requirements.txt` using `pip install -r requirements.txt`

### Using `conda` with a requirements file

1. Create a conda environment directly using the requirements from `requirements.txt`: `conda create --name myenv python=<Version > 3.9>`
2. Activate the environment: `source activate myenv`
3. Run `pip install -r requirements.txt` to install dependencies

**Usage Instructions**
---------------------

1. Run `chainlit run chainlit_app.py` to start the app.
2. Use the starters or ask questions through the agent chat.

**Troubleshooting**
-------------------

If you encounter any issues, please check the project's logs for errors and consult the documentation for further assistance.

**Contributing**
---------------

Contributions are welcome! If you'd like to contribute to this project, please fork the repository and create a pull request with your changes.

**License**
----------

This project is licensed under the MIT License.
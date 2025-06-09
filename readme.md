# Google ADK Example Agents

This repository contains multiple example agents and tools built using the [Google ADK (Agent Development Kit)](https://developers.google.com/adk) in Python. The goal is to explore and experiment with various agent patterns, tools, and features as demonstrated in the official Google ADK documentation.

## Features

- Example agents for weather, time, search, and more
- Multi-tool agent setups
- Sub-agent delegation and orchestration
- State management and session handling
- Guardrails and callback usage
- Jupyter notebook and script-based workflows

## Usage

1. **Clone this repository.**
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Activate your virtual environment:**
   - **Windows:**
     ```sh
     .\venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```sh
     source venv/bin/activate
     ```
4. **(Recommended) Register your venv as a Jupyter kernel:**
   ```sh
   pip install ipykernel
   python -m ipykernel install --user --name=venv --display-name "Python (venv)"
   ```
   This allows you to select your virtual environment as the kernel in Jupyter notebooks.

5. **Check your current Python interpreter in a notebook:**
   ```python
   import sys
   print(sys.executable)
   ```

<!-- 6. **Explore the examples:**
   - Run and modify the notebook [`google-adk.ipynb`](google-adk.ipynb) for interactive experimentation.
   - Review and run agent scripts in [`multi_tool_agent/agent.py`](multi_tool_agent/agent.py) and [`app/google_search_agent/agent.py`](app/google_search_agent/agent.py).

## File Structure

- `google-adk.ipynb`: Main Jupyter notebook with step-by-step ADK examples
- `multi_tool_agent/agent.py`: Multi-tool agent and related tools
- `app/google_search_agent/agent.py`: Google Search agent example
- `requirements.txt`: Python dependencies
- `readme.md`: Project documentation -->

## Commands

- `adk run`: Run an agent using the ADK CLI.
- `adk web`: Launch the ADK web interface for interactive agent testing.
- `adk api_server`: Start the ADK API server for programmatic access.

## Notes

- This is a learning and experimentation project for Google ADK agent development.
- You can extend or modify any agent, tool, or workflow as you explore more ADK features.
- Ensure that you set up your API keys and environment variables as required by each example.

---

For more information, refer to the [Google ADK documentation](https://developers.google.com/adk).

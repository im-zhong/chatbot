# chatbot

A simple chatbot

## Start FastAPI Server

`uv run uvicorn --reload chatbot.api:app`

## Start Streamlit APP

- When passing your script some custom arguments, they must be passed after two dashes.
- Otherwise the arguments get interpreted as arguments to Streamlit itself.

`uv run streamlit run chatbot/app.py [-- script args]`

### 1. How to debug streamlit?

1. `python -m streamlit run your_script.py` cause streamlit could be start as a normal python module, so I think just configure it in the vscode debug conf, and start it as a normal python program, then you could debug it.

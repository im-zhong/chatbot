import streamlit as st
import random
import time
from llm import get_chat_model

# streamlit itself is sync, so requests is enough
import requests
import json


url = "http://localhost:8000/sse"


## Chat demo
@st.cache_resource
def get_cached_chat_model():
    return get_chat_model()


llm = get_chat_model()

st.write(
    "Streamlit loves LLMs! 🤖 [Build your own chat app](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps) in minutes, then make it powerful by adding images, dataframes, or even input widgets to the chat."
)

st.caption(
    "Note that this demo app isn't actually connected to any LLMs. Those are expensive ;)"
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Let's start chatting! 👇"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        # Inserts a container into your app that can be used to hold a single element.
        message_placeholder = st.empty()
        full_response = ""
        # assistant_response = random.choice(
        #     [
        #         "Hello there! How can I assist you today?",
        #         "Hi, human! Is there anything I can help you with?",
        #         "Do you need help?",
        #     ]
        # )
        # # Simulate stream of response with milliseconds delay
        # for chunk in assistant_response.split():
        #     full_response += chunk + " "
        #     time.sleep(0.05)
        #     # Add a blinking cursor to simulate typing
        #     message_placeholder.markdown(full_response + "▌")

        # call the llm in stream mode
        # for chunk in llm.stream(input=st.session_state.messages):
        #     full_response += chunk.content
        #     message_placeholder.markdown(full_response + "▌")

        # call the stream sse from fastapi
        # Handling JSON SSE (very common for LLMs)
        with requests.get(url=url, stream=True) as r:
            for line in r.iter_lines(decode_unicode=True):
                # TODO: 那我比较好奇不是data的时候会返回什么？
                # if not line or not line.startswith("data: "):
                #     continue

                # # skip "data: "
                # payload = json.loads(line[5:])
                # token = payload["token"]

                # full_response += token
                # message_placeholder.markdown(full_response + "▌")

                # 我要直接输出整个line 看看sse的协议内容
                full_response += line
                message_placeholder.markdown(full_response + "▌")

        # finally, when llm finish its response, update the message box with the ful response
        message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

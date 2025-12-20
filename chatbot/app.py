import streamlit as st
import random
import time
from llm import get_chat_model

# streamlit itself is sync, so requests is enough
import requests
import json


# url = "http://localhost:8000/chat"
url = "http://localhost:8000/agent-chat"

from chatbot.api import UserMessage, AgentMessage


st.title("Auth test")

import streamlit as st
import urllib.parse

# ====== Keycloak settings (match your realm) ======
ISSUER = "http://localhost:8080/realms/streamlit"  # must match token "iss"
APP_BASE_URL = "http://localhost:8501"  # where your Streamlit runs
POST_LOGOUT_REDIRECT = f"{APP_BASE_URL}/"  # after IdP logout, come back here

# Keycloak end-session (IdP logout) URL
keycloak_logout_url = (
    f"{ISSUER}/protocol/openid-connect/logout?"
    + urllib.parse.urlencode({"post_logout_redirect_uri": POST_LOGOUT_REDIRECT})
)

st.title("Login / Logout (Streamlit + Keycloak OIDC)")

import streamlit as st
import urllib.parse

ISSUER = "http://localhost:8080/realms/streamlit"
CLIENT_ID = "streamlit"
APP_BASE_URL = "http://localhost:8501"
POST_LOGOUT_REDIRECT = f"{APP_BASE_URL}/"

# Keycloak front-channel logout:
# Use client_id (works without id_token_hint)
keycloak_logout_url = (
    f"{ISSUER}/protocol/openid-connect/logout?"
    + urllib.parse.urlencode(
        {
            "client_id": CLIENT_ID,
            "post_logout_redirect_uri": POST_LOGOUT_REDIRECT,
        }
    )
)

st.title("Streamlit + Keycloak OIDC Login/Logout")

# --- Logged in ---
if st.user.is_logged_in:
    c1, c2 = st.columns(2)

    with c1:
        if st.button("Logout (Streamlit only)", use_container_width=True):
            st.logout()
            st.stop()  # avoid falling through to login

    with c2:
        # Logs out of Keycloak SSO too -> next login can use different account
        st.link_button(
            "Logout from Keycloak (switch account)",
            keycloak_logout_url,
            use_container_width=True,
        )

    st.success("You are logged in!")
    st.json(st.user)

# --- Not logged in ---
else:
    st.info("You are not logged in.")
    if st.button("Login", use_container_width=True):
        st.login()
        st.stop()

st.divider()
st.write("Debug:")
st.json(st.user)


user_id = st.user["sub"]
st.write(f"user: {user_id}")


# 我还需要一个thread id: thread_id


## Chat demo
@st.cache_resource
def get_cached_chat_model():
    return get_chat_model()


llm = get_chat_model()

st.write(
    "Streamlit loves LLMs! 🤖 [Build your own chat app](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps) in minutes, then make it powerful by adding images, dataframes, or even input widgets to the chat."
)

# st.caption(
#     "Note that this demo app isn't actually connected to any LLMs. Those are expensive ;)"
# )

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
        # user_message = UserMessage(messages=st.session_state.messages)
        agent_message = AgentMessage(message=prompt)

        # with requests.post(url=url, json=user_message.model_dump(), stream=True) as r:
        with requests.post(url=url, json=agent_message.model_dump(), stream=True) as r:
            for line in r.iter_lines(decode_unicode=True):
                # TODO: 那我比较好奇不是data的时候会返回什么？
                if not line or not line.startswith("data: "):
                    continue

                # skip "data: "
                payload = json.loads(line[5:])
                token = payload["token"]

                full_response += token
                message_placeholder.markdown(full_response + "▌")

                # 我要直接输出整个line 看看sse的协议内容
                # full_response += line
                # message_placeholder.markdown(full_response + "▌")

        # finally, when llm finish its response, update the message box with the ful response
        message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})


# TODO:
# 我现在需要实现一个sidebar，展示所有的历史消息记录，就通过

# import json
# import urllib.parse

# import requests
# import streamlit as st

# from chatbot.api import AgentMessage
# from chatbot.llm import get_chat_model

# # url = "http://localhost:8000/chat"
# AGENT_CHAT_URL = "http://localhost:8000/agent-chat"
# GET_ALL_THREADS_URL = "http://localhost:8000/all-chat-threads"
# NEW_CHAT_URL = "http://localhost:8000/new-chat"
# THREAD_MESSAGES_URL = "http://localhost:8000/thread-chat-messages"

# st.title("Auth test")

# # ====== Keycloak settings (match your realm) ======
# ISSUER = "http://localhost:8080/realms/streamlit"  # must match token "iss"
# APP_BASE_URL = "http://localhost:8501"  # where your Streamlit runs
# POST_LOGOUT_REDIRECT = f"{APP_BASE_URL}/"  # after IdP logout, come back here

# # Keycloak end-session (IdP logout) URL
# keycloak_logout_url = (
#     f"{ISSUER}/protocol/openid-connect/logout?"
#     + urllib.parse.urlencode({"post_logout_redirect_uri": POST_LOGOUT_REDIRECT})
# )

# st.title("Login / Logout (Streamlit + Keycloak OIDC)")

# CLIENT_ID = "streamlit"
# APP_BASE_URL = "http://localhost:8501"
# POST_LOGOUT_REDIRECT = f"{APP_BASE_URL}/"

# # Keycloak front-channel logout:
# # Use client_id (works without id_token_hint)
# keycloak_logout_url = (
#     f"{ISSUER}/protocol/openid-connect/logout?"
#     + urllib.parse.urlencode(
#         {
#             "client_id": CLIENT_ID,
#             "post_logout_redirect_uri": POST_LOGOUT_REDIRECT,
#         }
#     )
# )

# st.title("Streamlit + Keycloak OIDC Login/Logout")

# # --- Logged in ---
# if st.user.is_logged_in:
#     c1, c2 = st.columns(2)

#     with c1:
#         if st.button("Logout (Streamlit only)", use_container_width=True):
#             st.logout()
#             st.stop()  # avoid falling through to login

#     with c2:
#         # Logs out of Keycloak SSO too -> next login can use different account
#         st.link_button(
#             "Logout from Keycloak (switch account)",
#             keycloak_logout_url,
#             use_container_width=True,
#         )

#     st.success("You are logged in!")
#     # st.json(st.user)

# # --- Not logged in ---
# else:
#     st.info("You are not logged in.")
#     if st.button("Login", use_container_width=True):
#         st.login()
#         st.stop()

# # st.divider()
# # st.write("Debug:")
# # st.json(st.user)


# user_id = st.user["sub"]
# st.write(f"user: {user_id}")


# # should store thread_id in the session state
# # https://docs.streamlit.io/get-started/fundamentals/advanced-concepts#session-state
# # thread_id: str | None = None
# if "current_thread_id" not in st.session_state:
#     st.session_state.current_thread_id = None

# # 我还需要一个thread id: thread_id


# def fetch_threads(user_id: str) -> list[str]:
#     resp = requests.get(GET_ALL_THREADS_URL, params={"user_id": user_id}, timeout=10)
#     resp.raise_for_status()
#     data: list[str] = resp.json()
#     # Expect list[str]
#     return data


# # st.session_state.messages = [
# #     {"role": "assistant", "content": "Let's start chatting! 👇"}
# # ]
# def fetch_thread_chat_messages(user_id: str, thread_id: str) -> list[dict]:
#     # pass
#     # 1. 首先实现一个新的API，根据userid和threadid返回消息历史
#     resp = requests.get(
#         THREAD_MESSAGES_URL,
#         params={"user_id": user_id, "thread_id": thread_id},
#         timeout=10,
#     )
#     resp.raise_for_status()
#     return resp.json()


# def new_chat() -> str:
#     resp = requests.post(NEW_CHAT_URL, json={"user_id": user_id}, timeout=10)
#     resp.raise_for_status()
#     data = resp.json()
#     return data["thread_id"]


# ## Chat demo
# @st.cache_resource
# def get_cached_chat_model():
#     return get_chat_model()


# llm = get_chat_model()


# ## Sidebar: history threads
# st.sidebar.header("History")

# try:
#     thread_ids = fetch_threads(user_id)
# except requests.RequestException as e:
#     st.sidebar.error(f"Failed to load threads: {e}")
#     thread_ids = []

# # 我想把new chat的按钮放在最上面
# if st.sidebar.button("➕ New chat", use_container_width=True):
#     st.session_state.current_thread_id = new_chat()
#     # st.session_state.messages = [
#     #     {"role": "assistant", "content": "Let's start chatting! 👇"}
#     # ]
#     st.rerun()

# if not thread_ids:
#     st.sidebar.caption("No chats yet.")
#     st.session_state.current_thread_id = None
#     # 那么，这里可以自动的创建一个新的new chat 作为初始化
#     st.session_state.current_thread_id = new_chat()
# else:
#     # Default to first thread if none selected yet (assumes API already sorts new->old)
#     # 这个不管thread id是一个随机的值，还是None，都可以更新成最新的值 好！
#     if st.session_state.current_thread_id not in thread_ids:
#         st.session_state.current_thread_id = thread_ids[0]

#     # 这里用了一个列表
#     selected = st.sidebar.radio(
#         "Chats",
#         options=thread_ids,
#         index=thread_ids.index(st.session_state.current_thread_id),
#         label_visibility="collapsed",
#     )
#     st.session_state.current_thread_id = selected
#     # 一旦选择了，我们就要读取当前thread id所对应的所有的历史消息，并更新session_state.messages
#     st.session_state.messages = fetch_thread_chat_messages(
#         user_id=user_id, thread_id=st.session_state.current_thread_id
#     )


# st.write(
#     "Streamlit loves LLMs! 🤖 [Build your own chat app](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps) in minutes, then make it powerful by adding images, dataframes, or even input widgets to the chat."
# )

# # st.caption(
# #     "Note that this demo app isn't actually connected to any LLMs. Those are expensive ;)"
# # )

# # display all threads of current user
# # with requests.get(url=get_all_threads_url, params={"user_id": user_id}) as r:
# #     # threads: list[str] = r.json()
# #     st.write("user chats: ")
# #     st.write(r.json())

# #     threads: list[str] = r.json()
# #     # 默认情况下，thread_id会被赋值成第一个
# #     if threads and thread_id is None:
# #         thread_id = threads[0]


# # Initialize chat history
# # 因为加入了new chat的逻辑，所以如果发现current_thread_id is None, 那么就要更新 session state里面的message
# if st.session_state.current_thread_id is None or "messages" not in st.session_state:
#     st.session_state.messages = [
#         {"role": "assistant", "content": "Let's start chatting! 👇"}
#     ]

# # Display chat messages from history on app rerun
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])


# if "pending_interrupt" in st.session_state:
#     interrupt = st.session_state.pending_interrupt

#     with st.chat_message("assistant"):
#         st.markdown(f"⚠️ **Approval needed**  \n{interrupt['question']}")

#         choice = st.radio(
#             "",
#             ["Approve", "Reject"],
#             horizontal=True,
#             key="approval_choice",
#         )

#         col1, col2 = st.columns([1, 1])
#         with col1:
#             approve_clicked = st.button("✓ Confirm", key="approve_btn")
#         with col2:
#             cancel_clicked = st.button("✗ Cancel", key="cancel_btn")


# # st.session_state.pending_interrupt   # 是否有 interrupt 等待处理
# # st.session_state.interrupt_decision  # True / False
# # st.session_state.should_resume       # 是否该 resume graph
# if "pending_interrupt" in st.session_state:
#     if st.session_state.get("approve_btn"):
#         st.session_state.interrupt_decision = (
#             st.session_state.approval_choice == "Approve"
#         )
#         st.session_state.should_resume = True
#         st.rerun()

#     if st.session_state.get("cancel_btn"):
#         st.session_state.interrupt_decision = False
#         st.session_state.should_resume = True
#         st.rerun()


# def run_agent_sse(agent_message: AgentMessage, resume: bool = False):
#     message_placeholder = st.empty()
#     full_response = ""

#     with requests.post(
#         url=AGENT_CHAT_URL,
#         json={
#             **agent_message.model_dump(),
#             "resume": resume,
#         },
#         stream=True,
#         timeout=30,
#     ) as r:
#         for line in r.iter_lines(decode_unicode=True):
#             if not line or not line.startswith("data: "):
#                 continue

#             payload = json.loads(line[5:])

#             if payload["type"] == "token":
#                 token = payload["token"]
#                 full_response += token
#                 message_placeholder.markdown(full_response + "▌")

#             elif payload["type"] == "interrupt":
#                 # 保存 interrupt
#                 st.session_state.pending_interrupt = {
#                     "id": payload["id"],
#                     "question": payload["question"],
#                 }
#                 st.session_state.should_resume = False

#                 # 停止本轮
#                 st.session_state.partial_response = full_response
#                 st.rerun()

#     message_placeholder.markdown(full_response)
#     return full_response


# # Accept user input
# # if prompt := st.chat_input("What is up?"):
# #     # Add user message to chat history
# #     st.session_state.messages.append({"role": "user", "content": prompt})
# #     # Display user message in chat message container
# #     with st.chat_message("user"):
# #         st.markdown(prompt)


# #     # Display assistant response in chat message container
# #     with st.chat_message("assistant"):
# #         # Inserts a container into your app that can be used to hold a single element.
# #         message_placeholder = st.empty()
# #         full_response = ""
# #         # assistant_response = random.choice(
# #         #     [
# #         #         "Hello there! How can I assist you today?",
# #         #         "Hi, human! Is there anything I can help you with?",
# #         #         "Do you need help?",
# #         #     ]
# #         # )
# #         # # Simulate stream of response with milliseconds delay
# #         # for chunk in assistant_response.split():
# #         #     full_response += chunk + " "
# #         #     time.sleep(0.05)
# #         #     # Add a blinking cursor to simulate typing
# #         #     message_placeholder.markdown(full_response + "▌")

# #         # call the llm in stream mode
# #         # for chunk in llm.stream(input=st.session_state.messages):
# #         #     full_response += chunk.content
# #         #     message_placeholder.markdown(full_response + "▌")

# #         # call the stream sse from fastapi
# #         # Handling JSON SSE (very common for LLMs)
# #         # user_message = UserMessage(messages=st.session_state.messages)

# #         # 到了这一步了，不得不聊天了，如果thread_id是空的话，就说明要创建一个新的对话
# #         # if st.session_state.current_thread_id is None:
# #         #     st.session_state.current_thread_id = new_chat()
# #         #     st.rerun()
# #         # st.session_state.messages = [
# #         #     {"role": "assistant", "content": "Let's start chatting! 👇"}
# #         # ]
# #         assert user_id is not None
# #         agent_message = AgentMessage(
# #             message=prompt,
# #             user_id=user_id,
# #             thread_id=st.session_state.current_thread_id,
# #         )
# #         # TODO: 但是要怎么在sidebar上体现出来呢？

# #         with requests.post(
# #             url=AGENT_CHAT_URL, json=agent_message.model_dump(), stream=True, timeout=30
# #         ) as r:
# #             for line in r.iter_lines(decode_unicode=True):
# #                 # TODO: 那我比较好奇不是data的时候会返回什么？
# #                 if not line or not line.startswith("data: "):
# #                     continue

# #                 # skip "data: "
# #                 payload = json.loads(line[5:])
# #                 # 现在我们又两种数据格式了
# #                 # data: {"type": "token", "token": "Di"}
# #                 # data: {"type": "interrupt", "id": "9e69c2ac43ac610e4fd610bdb9dcb132", "question": "Do you approve this action?"}

# #                 # 所以首先要对type进行测试
# #                 if payload["type"] == "token":
# #                     token = payload["token"]
# #                     full_response += token
# #                     message_placeholder.markdown(full_response + "▌")
# #                 elif payload["type"] == "interrupt":
# #                     # 保存 interrupt 状态
# #                     st.session_state.pending_interrupt = {
# #                         "id": payload["id"],
# #                         "question": payload["question"],
# #                     }
# #                     st.session_state.should_resume = False

# #                     full_response += payload["question"]
# #                     message_placeholder.markdown(full_response + "▌")
# #                     st.rerun()

# #                 # 我要直接输出整个line 看看sse的协议内容
# #                 # full_response += line
# #                 # message_placeholder.markdown(full_response + "▌")

# #         # finally, when llm finish its response, update the message box with the ful response
# #         message_placeholder.markdown(full_response)
# #     # Add assistant response to chat history
# #     st.session_state.messages.append({"role": "assistant", "content": full_response})

# if st.session_state.get("should_resume"):
#     st.session_state.should_resume = False

#     with st.chat_message("assistant"):
#         agent_message = AgentMessage(
#             message="",  # resume 不需要原始 prompt
#             user_id=user_id,
#             thread_id=st.session_state.current_thread_id,
#             approved=st.session_state.resume_approved,
#         )

#         full_response = run_agent_sse(agent_message, resume=True)

#     # resume 完成后，才真正写入 assistant message
#     st.session_state.messages.append({"role": "assistant", "content": full_response})

#     del st.session_state.resume_approved


# if prompt := st.chat_input("What is up?"):
#     # 1. 记录 user 消息
#     st.session_state.messages.append({"role": "user", "content": prompt})

#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # 2. assistant 容器
#     with st.chat_message("assistant"):
#         assert user_id is not None

#         agent_message = AgentMessage(
#             message=prompt,
#             user_id=user_id,
#             thread_id=st.session_state.current_thread_id,
#         )

#         full_response = run_agent_sse(agent_message, resume=False)

#     # 3. 只有“真正结束”才写入 history
#     if "pending_interrupt" not in st.session_state:
#         st.session_state.messages.append(
#             {"role": "assistant", "content": full_response}
#         )

# # TODO:
# # 我现在需要实现一个sidebar，展示所有的历史消息记录，就通过
# # 我需要先实现一个API，返回某个用户所有的消息历史


## new impl from chatgpt
import json
import requests
import streamlit as st

from chatbot.api import AgentMessage

AGENT_CHAT_URL = "http://localhost:8000/agent-chat"

st.set_page_config(page_title="LangGraph Interrupt Demo", layout="centered")
st.title("LangGraph Human-in-the-loop Demo")

# ======================================================
# 1. Session State Initialization (CRITICAL)
# ======================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Let's start chatting! 👇"}
    ]

if "pending_interrupt" not in st.session_state:
    st.session_state.pending_interrupt = None

if "resume_approved" not in st.session_state:
    st.session_state.resume_approved = None

if "should_resume" not in st.session_state:
    st.session_state.should_resume = False

if "current_thread_id" not in st.session_state:
    st.session_state.current_thread_id = "demo-thread"

# Demo user id (replace with Keycloak / auth later)
user_id = "demo-user"


# ======================================================
# 2. SSE Runner (NO UI LOGIC HERE)
# ======================================================
def run_agent_sse(agent_message: AgentMessage, resume: bool = False) -> str:
    """
    Run agent via SSE.
    If interrupt occurs, it stores interrupt state and reruns Streamlit.
    """
    message_placeholder = st.empty()
    full_response = ""

    with requests.post(
        AGENT_CHAT_URL,
        json={**agent_message.model_dump(), "resume": resume},
        stream=True,
        timeout=60,
    ) as r:
        for line in r.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue

            payload = json.loads(line[5:])

            if payload["type"] == "token":
                token = payload["token"]
                full_response += token
                message_placeholder.markdown(full_response + "▌")

            elif payload["type"] == "interrupt":
                # ⛔ Save interrupt state and stop this run
                st.session_state.pending_interrupt = {
                    "id": payload["id"],
                    "question": payload["question"],
                }
                st.session_state.should_resume = False
                st.rerun()

    message_placeholder.markdown(full_response)
    return full_response


# ======================================================
# 3. Render Chat History
# ======================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ======================================================
# 4. Interrupt UI (UI ONLY)
# ======================================================
if st.session_state.pending_interrupt is not None:
    interrupt = st.session_state.pending_interrupt

    with st.chat_message("assistant"):
        st.markdown(f"⚠️ **Approval needed**  \n{interrupt['question']}")

        st.radio(
            "",
            ["Approve", "Reject"],
            horizontal=True,
            key="approval_choice",
        )

        col1, col2 = st.columns(2)
        with col1:
            st.button("✓ Confirm", key="approve_btn")
        with col2:
            st.button("✗ Cancel", key="cancel_btn")


# ======================================================
# 5. Handle Approval Clicks (STATE ONLY)
# ======================================================
if st.session_state.pending_interrupt is not None:
    if st.session_state.get("approve_btn"):
        st.session_state.resume_approved = st.session_state.approval_choice == "Approve"
        st.session_state.should_resume = True
        st.rerun()

    if st.session_state.get("cancel_btn"):
        st.session_state.resume_approved = False
        st.session_state.should_resume = True
        st.rerun()


# ======================================================
# 6. Resume Graph Execution (ONLY PLACE resume=True)
# ======================================================
if st.session_state.should_resume:
    st.session_state.should_resume = False

    with st.chat_message("assistant"):
        agent_message = AgentMessage(
            message="",  # resume does NOT resend messages
            user_id=user_id,
            thread_id=st.session_state.current_thread_id,
            approved=st.session_state.resume_approved,
        )

        full_response = run_agent_sse(agent_message, resume=True)

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Cleanup
    st.session_state.pending_interrupt = None
    st.session_state.resume_approved = None


# ======================================================
# 7. Normal User Input (First Run)
# ======================================================
if prompt := st.chat_input("What is up?"):
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant message
    with st.chat_message("assistant"):
        agent_message = AgentMessage(
            message=prompt,
            user_id=user_id,
            thread_id=st.session_state.current_thread_id,
        )

        full_response = run_agent_sse(agent_message, resume=False)

    # Only save if no interrupt happened
    if st.session_state.pending_interrupt is None:
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

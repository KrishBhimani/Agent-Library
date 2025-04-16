import streamlit as st
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
groq_api_key=os.getenv('GROQ_API_KEY')

# ---------- CONFIG ----------
st.set_page_config(page_title="🧠 Prompt Designer", layout="wide")
st.title("🧠 Prompt Designer Assistant")

# ---------- MODEL ----------
model=ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct",groq_api_key=groq_api_key)

# ---------- SESSION STORAGE ----------
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

prompt = ChatPromptTemplate.from_messages([
    ("system", """I want you to become my Expert Prompt Creator. Your goal is to help me craft the best possible prompt for my needs. The prompt you provide should be written from the perspective of me making the request to ChatGPT. Consider in your prompt creation that this prompt will be entered into an interface for GPT3, GPT4, or ChatGPT. The prompt will include instructions to write the output using my communication style.

The process is as follows:

1. You will generate the following sections:

" **Prompt:\\ >
{{provide the best possible prompt according to my request}}

> > >
{{summarize my prior messages to you and provide them as examples of my communication style}}

**Critique:\\
{{provide a concise paragraph on how to improve the prompt. Be very critical in your response. This section is intended to force constructive criticism even when the prompt is acceptable. Any assumptions and or issues should be included}}

**Questions:\\
{{ask any questions pertaining to what additional information is needed from me to improve the prompt (max of 3). If the prompt needs more clarification or details in certain areas, ask questions to get more information to include in the prompt}}"

2. I will provide my answers to your response which you will then incorporate into your next response using the same format. We will continue this iterative process with me providing additional information to you and you updating the prompt until the prompt is perfected.

Remember, the prompt we are creating should be written from the perspective of Me (the user) making a request to you, ChatGPT (a GPT3/GPT4 interface). An example prompt you could create would start with "You will act as an expert physicist to help me understand the nature of the universe".

Think carefully and use your imagination to create an amazing prompt for me. Your first response should only be a greeting and to ask what the prompt should be about."""),
    ("user", "{input}")
])

chain= prompt | model

chain_with_history = RunnableWithMessageHistory(chain, get_session_history)

session_id = st.session_state.get("session_id", "default_session")
st.session_state["session_id"] = session_id

if session_id in store:
    for msg in store[session_id].messages:
        if msg.type == "human":
            st.chat_message("user").write(msg.content)
        else:
            st.chat_message("assistant").write(msg.content)

user_input = st.chat_input("Ask me to refine or design a prompt...")

if user_input:
    st.chat_message("user").write(user_input)

    response = chain_with_history.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": session_id}}
    )

    st.chat_message("assistant").write(response.content)

if st.button("🔄 Clear Chat"):
    store[session_id] = ChatMessageHistory()
    st.rerun()

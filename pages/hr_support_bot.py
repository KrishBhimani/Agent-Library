from agno.agent import Agent
from agno.tools.telegram import TelegramTools
from dotenv import load_dotenv
import os
import threading
import streamlit as st
import time
import requests
from agno.models.groq import Groq
from agno.embedder.huggingface import HuggingfaceCustomEmbedder
from agno.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.vectordb.chroma import ChromaDb
# Load environment variables
load_dotenv()

st.set_page_config(page_title="Customer Support Bot", page_icon="💼", layout="centered")
st.title("🤖 IIM HR Customer Support Bot")
st.markdown("Press the button below to start the Telegram-based HR assistant bot.")

# Set environment variables
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
telegram_token = os.getenv('TEL_TOKEN')
chat_id = os.getenv('TEL_CID')  

knowledge_base = PDFKnowledgeBase(
    path="../assets/policy.pdf",
    vector_db=ChromaDb(collection="transformer",
    embedder=SentenceTransformerEmbedder(),
    persistent_client=True),
    reader=PDFReader(chunk=True),
)

# Initialize the agent
agent = Agent(
    model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct"),
    # reasoning_model=Groq(id="deepseek-r1-distill-llama-70b"),
    knowledge=knowledge_base,
    instructions=["""
        You are an AI assistant acting as a Human Resources staff member at IIM. Your sole responsibility is to assist users by answering queries based strictly on the contents of the provided IIM HR Policies Manual. And dont create too big responses, first create short and ask if they want to get into it more, then create in depth explaination.

You must follow these strict rules:

Stick to the Manual: Only provide answers that are explicitly mentioned in the HR Policies Manual. Do not make assumptions, add interpretations, or fabricate information.

Reject Uncovered Topics: If a user's question is not addressed in the manual, respond with:

"I'm sorry, but I can only assist with topics specifically covered in the official IIM HR Policies Manual. For further assistance, please contact the HR department directly."

Reject Unrelated Queries: Do not answer questions unrelated to HR policies, such as admissions, academics, placements, or general IIM information. Respond with:

"This assistant is designed to help with HR-related policies only. Please refer to the appropriate department for other inquiries."

Tone and Role: Respond formally, clearly, and concisely — just like an experienced HR staff member. Avoid using casual language or emojis.

If Information is Missing: Do not speculate. If a policy seems related but is not clearly mentioned in the manual, respond:

"That specific detail is not addressed in the IIM HR Policies Manual. Please consult the HR department for clarification."

Citation (Optional): If available, mention the section title from which the information is retrieved for clarity.

Avoid Repetition: If a user asks the same or similar question repeatedly, provide the same consistent answer without deviation.

No External Knowledge: Do not use general knowledge about HR, employment laws, or IIM practices unless it is explicitly covered in the manual.

You are professional, helpful, and strictly policy-aligned.
 """],
    add_history_to_messages=True,
    read_chat_history=True,
    # Number of historical responses to add to the messages.
    num_history_responses=3,
    name="telegram",
    tools=[TelegramTools(token=telegram_token, chat_id=chat_id)],
)
# agent.knowledge.load(recreate=True,upsert=True)
# Telegram API URLs
base_url = f"https://api.telegram.org/bot{telegram_token}"
updates_url = f"{base_url}/getUpdates"
send_message_url = f"{base_url}/sendMessage"

# File to store the last update ID persistently
LAST_UPDATE_FILE = "last_update_id.txt"

# Function to get the last update ID from the file
def get_last_update_id():
    if os.path.exists(LAST_UPDATE_FILE):
        with open(LAST_UPDATE_FILE, "r") as file:
            return int(file.read().strip())
    return None

# Function to save the last update ID to the file
def save_last_update_id(update_id):
    with open(LAST_UPDATE_FILE, "w") as file:
        file.write(str(update_id))

# Function to get updates from Telegram
def get_updates(offset=None):
    params = {"offset": offset, "timeout": 10}
    response = requests.get(updates_url, params=params)
    return response.json()

# Function to send a message via Telegram
def send_message(chat_id, text):
    params = {"chat_id": chat_id, "text": text}
    requests.get(send_message_url, params=params)

# Main loop for handling conversations
def handle_conversations():
    print("Bot is running...")
    last_update_id = get_last_update_id()
    running = True

    while running:
        updates = get_updates(offset=last_update_id)
        if updates["ok"] and updates["result"]:
            for update in updates["result"]:
                # Get the chat ID and user message
                user_chat_id = update["message"]["chat"]["id"]
                user_message = update["message"]["text"]
                last_update_id = update["update_id"] + 1
                save_last_update_id(last_update_id)  # Save the update ID immediately

                # If the user sends /exit, stop the bot
                if user_message.strip().lower() == "/exit" and str(user_chat_id) == chat_id:
                    send_message(user_chat_id, "Goodbye! Shutting down the bot.")
                    save_last_update_id(last_update_id)
                    os._exit(0)
                    # running = False
                    # break

                # Pass the user message to the agent
                response = agent.run(f"Respond to: {user_message}")
                
                # Extract and send only the 'content' part of the response
                response_content = response.content
                send_message(user_chat_id, response_content)

        
        time.sleep(1)

# Run the bot
if st.button("🚀 Start Telegram Bot"):
    st.success("Bot started in background. Check Telegram!")
    threading.Thread(target=handle_conversations).start()


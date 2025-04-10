import streamlit as st

st.set_page_config(page_title="Agent Library", page_icon="🤖", layout="wide")

st.markdown(
    """
    <style>
    .stButton>button {
        width: 100%;
        height: 140px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
        background-color: white;
        color: #2C3E50;
        border: none;
        transition: 0.3s;
        padding: 8px;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        white-space: normal;
        word-wrap: break-word;
    }
    .stButton>button:hover {
        background-color: white;
        transform: scale(1.05);
        color: black;
    }
    .title {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .description {
        text-align: center;
        font-size: 18px;
        color: #555;
        margin-bottom: 30px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<h1 class="title">Agent Library</h1>', unsafe_allow_html=True)
st.markdown('<p class="description">Explore a variety of intelligent agents designed for different tasks.</p>', unsafe_allow_html=True)

agent_info = [
    ("Github Readme Automation", "Analyze the repository and create a README file automatically"),
    ("Email Automation", "Analyzes the email body and categorizes it and sends the email from respective team."),
    ("Trip Planner", "Provides complete itenary for your trip"),
    ("HR Support Bot", "Conversational AI for HR support on Telegram."),
    ("Sentiment Analyzer", "Determines sentiment in text data."),
    ("Code Reviewer", "Automates code quality checks."),
    ("Fraud Detector", "Identifies suspicious financial transactions."),
    ("Document Summarizer", "Generates concise summaries of text documents."),
    ("Speech Recognizer", "Converts spoken language into text."),
    ("Translator", "Translates text between multiple languages."),
    ("Ad Recommender", "Suggests personalized advertisements."),
    ("Traffic Predictor", "Analyzes traffic data for congestion forecasting."),
    ("Task Automator", "Automates repetitive business processes."),
    ("Face Recognizer", "Identifies individuals from images or videos."),
    ("Cybersecurity Monitor", "Detects potential security threats in real time."),
    ("Health Diagnostic", "Provides AI-based medical diagnosis assistance."),
    ("Weather Forecaster", "Predicts weather conditions based on historical data."),
    ("Image Captioning", "Generates captions for images using deep learning."),
    ("Voice Cloning", "Creates AI-generated voices from samples."),
    ("Legal Document Analyzer", "Extracts insights from legal documents."),
    ("News Aggregator", "Gathers and summarizes news from various sources."),
    ("Financial Advisor", "Provides AI-driven financial recommendations."),
    ("Email Classifier", "Sorts emails into predefined categories."),
    ("Object Detector", "Identifies objects in images and videos."),
    ("Smart Scheduler", "Optimizes scheduling for meetings and tasks."),
    ("Anomaly Detector", "Finds irregular patterns in datasets."),
    ("E-commerce Recommender", "Suggests products based on user behavior."),
    ("Resume Generator", "Creates professional resumes based on input data."),
    ("AI Tutor", "Provides educational assistance using AI."),
    ("Game AI", "Enhances game characters with intelligent behaviors."),
]

for i in range(0, len(agent_info), 3):
    cols = st.columns(3)
    for j in range(3):
        if i + j < len(agent_info):
            with cols[j]:
                
                if st.button(f"**{agent_info[i+j][0]}**\n\n{agent_info[i+j][1]}", key=f"agent_{i+j}"):
                    st.switch_page(f"pages/{agent_info[i+j][0].replace(' ', '_').lower()}.py")

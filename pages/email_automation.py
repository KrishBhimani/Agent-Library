import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing_extensions import Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage
from agno.agent import Agent
from agno.tools.email import EmailTools
from agno.models.groq import Groq
import streamlit as st

# Load environment variables
load_dotenv()
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')

# Initialize LLM
llm = ChatGroq(model="qwen-2.5-32b")

# Define routing structure
class Route(BaseModel):
    step: Literal["support team", "technical team", "marketing team"] = Field(
        None, description="The next step of the routing process"
    )

class State(TypedDict):
    input: str
    decision: str
    output: str

router = llm.with_structured_output(Route)

# Define team functions
def support(state: State):
    """Handles routing to the Support Team."""
    return {"output": "It's sent to Support Team"}

def tech(state: State):
    """Handles routing to the Technical Team."""
    return {"output": "It's sent to Technical Team"}

def marketing(state: State):
    """Handles routing to the Marketing Team."""
    return {"output": "It's sent to Marketing Team"}

def llm_call_router(state: State):
    """Determines the routing decision using the LLM."""
    decision = router.invoke([SystemMessage(content=(
        "You are an AI assistant responsible for routing emails to the correct team. Analyze the email content and determine "
        "whether it should be sent to the Support Team, Technical Team, or Marketing Team. Use the following criteria:\n\n"
        "- **Support Team**: Handles customer service inquiries, order issues, and general support requests.\n"
        "- **Technical Team**: Resolves technical problems such as system errors, login issues, and software bugs.\n"
        "- **Marketing Team**: Manages promotional campaigns, collaborations, and brand partnerships."
    )),
    HumanMessage(content=state['input'])
    ])
    return {'decision': decision.step}

def router_decision(state: State):
    """Determines the next step based on the LLM decision."""
    if state['decision'] == "support team":
        return "support"
    elif state['decision'] == "technical team":
        return "tech"
    elif state['decision'] == "marketing team":
        return "marketing"

# Build the workflow graph
builder = StateGraph(State)

builder.add_node("Support_Team", support)
builder.add_node("Tech_Team", tech)
builder.add_node("Marketing_Team", marketing)
builder.add_node("llm_call_router", llm_call_router)

builder.add_edge(START, "llm_call_router")
builder.add_conditional_edges(
    "llm_call_router",
    router_decision,
    {
        "tech": "Tech_Team",
        "support": "Support_Team",
        "marketing": "Marketing_Team"
    }
)
builder.add_edge("Support_Team", END)
builder.add_edge("Tech_Team", END)
builder.add_edge("Marketing_Team", END)

router_workflow = builder.compile()

# Streamlit UI for email composition
st.title("Professional Email Generator")
st.write("""
This tool helps you craft a professional email response based on the content you provide. The system analyzes your message,
routes it to the appropriate team (Support, Technical, or Marketing), and generates a professional response.
""")

# Email input fields
email_body = st.text_area("Email Body", height=200, placeholder="Enter the content of your email...")

receiver_email = st.text_input("Receiver's Email", placeholder="e.g., receiver@example.com")

sender_name = st.text_input("Your Name", value="Krish", placeholder="e.g., John Doe")

# Generate the response when the button is clicked
if st.button("Generate and Send Email"):
    if email_body and receiver_email:
        # Prepare state for routing
        state = {
            "input": email_body,
            "decision": "",
            "output": ""
        }

        # Get the routing decision
        response = router_workflow.invoke(state)

        # Automatically generate the subject using the LLM
        # Automatically generate the subject using the LLM
        subject_response = llm.invoke([SystemMessage(content="You are an AI assistant. Generate a professional subject for the email based on the following content:"),
                               HumanMessage(content=email_body)])

# Extract the subject text from the AI response
        subject = subject_response.content  # Use the correct attribute to access the text



        # Define the email content and generate a professional response
        response_content = f"""
        Subject: {subject}

        Dear {sender_name},

        Thank you for reaching out to us. We have received your query and based on the content of your email, it will be handled by the {response['output']}.

        We will get back to you shortly with a resolution.

        Best regards,
        {sender_name}
        """

        # Define Agno Agent for sending the email
        sender_email = os.getenv('sender_email')
        sender_passkey = os.getenv('sender_passkey')

        agent = Agent(
            model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct"),
            instructions=[
                "You are tasked with crafting and sending a professional email response based on the following:",
                f"1. The email content received from the sender: {response['input']}",
                f"2. The team responsible for responding: {response['output']}",
                "Compose a professional email addressing the sender's concerns and include the team responsible for the response in the signature."
            ],
            tools=[EmailTools(
                receiver_email=receiver_email,
                sender_email=sender_email,
                sender_name=sender_name,
                sender_passkey=sender_passkey,
            )],
        )

        # Send email
        agent.print_response(f"send an email to {receiver_email}")

        st.success("Email sent successfully!")
    else:
        st.warning("Please fill in all the required fields.")


# I am reaching out to explore potential collaboration opportunities between our brands. We believe a partnership could be mutually beneficial, especially given our shared audience.
# Could we schedule a meeting to discuss how we can work together? Looking forward to your thoughts.

# I am facing an issue with logging into my account on our company portal. Every time I enter my credentials, I receive an "Invalid Credentials" error, even though I am sure my details are correct. I also tried resetting my password, but the reset link isn’t working.
# Could you please look into this issue and help me regain access?

# I recently placed an order (#12345) on your website, but I haven't received any updates regarding the shipping status. The estimated delivery date has passed, and the tracking link isn't showing any details.
# Could you please check the status and provide an update?
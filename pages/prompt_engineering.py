from crewai import Agent
from fpdf import FPDF
import re
import streamlit as st
import datetime
import sys
from crewai import Task
from textwrap import dedent
from datetime import date
from langchain_core.language_models.chat_models import BaseChatModel
from crewai import Crew, LLM


import os
from dotenv import load_dotenv
load_dotenv()
os.environ['GEMINI_API_KEY']=os.getenv('GEMINI_API_KEY')
import streamlit as st
from crewai import Agent, Task, Crew, Process
# from langchain_anthropic import ChatAnthropic

# Set up the page configuration
import streamlit as st
import os
import traceback
from crewai import Agent, Task, Crew, Process
# import google.generativeai as genai
# from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st
import os
import traceback
from crewai import Agent, Task, Crew, Process
# import google.generativeai as genai
# from langchain_google_genai import ChatGoogleGenerativeAI

# Set up the page configuration
st.set_page_config(
    page_title="Prompt Engineering Agent",
    page_icon="🤖",
    layout="wide"
)

# Display debugging info in the sidebar
st.sidebar.title("Debug Info")

# Configure Google Gemini API
def setup_gemini_api():
    try:
        # Try to get API key from environment variables or Streamlit secrets
        api_key = os.getenv('GEMINI_API_KEY')
        # If not available, request it from the user
        if not api_key:
            api_key = st.sidebar.text_input("Enter your Google API Key:", type="password")
            if api_key:
                os.environ["GOOGLE_API_KEY"] = api_key
                st.sidebar.success("API Key set!")
            else:
                st.sidebar.warning("Please enter your Google API Key to continue")
                return False
        
        # Configure the API
        # genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.sidebar.error(f"API Setup Error: {str(e)}")
        return False

# Get LLM instance for CrewAI
@st.cache_resource
def get_llm():
    try:
        llm = LLM(model="gemini/gemini-2.0-flash")
        st.sidebar.success("LLM initialized successfully!")
        return llm
    except Exception as e:
        st.sidebar.error(f"LLM Error: {str(e)}")
        st.sidebar.error(traceback.format_exc())
        return None

# Initialize session state variables
if 'prompt_history' not in st.session_state:
    st.session_state.prompt_history = []
if 'current_iteration' not in st.session_state:
    st.session_state.current_iteration = 0
if 'feedback_questions' not in st.session_state:
    st.session_state.feedback_questions = []
if 'final_prompt' not in st.session_state:
    st.session_state.final_prompt = ""
if 'debug_messages' not in st.session_state:
    st.session_state.debug_messages = []

# Add debug message function
def add_debug(message):
    st.session_state.debug_messages.append(message)
    # Show only the latest 10 debug messages
    st.sidebar.write(f"DEBUG: {message}")

# Display all debug messages in the sidebar
with st.sidebar.expander("View Debug History", expanded=False):
    for i, msg in enumerate(st.session_state.debug_messages[-10:]):
        st.write(f"{i+1}. {msg}")

# Title and description
st.title("🤖 Prompt Engineering Assistant")
st.markdown("""
This tool helps you craft the perfect prompt for your AI interactions.
Simply describe what you need, and our CrewAI-powered system will generate
an optimized prompt along with questions to refine it further.
""")

# Define the CrewAI agents and tasks
def create_prompt_engineering_crew(user_input, feedback=None):
    try:
        add_debug(f"Creating crew with input: {user_input[:50]}...")
        
        llm = get_llm()
        if not llm:
            add_debug("LLM initialization failed")
            return "Error: Failed to initialize LLM"
        
        # Define the prompt engineer agent
        add_debug("Creating Prompt Engineer agent...")
        prompt_engineer = Agent(
            role="Prompt Engineering Expert",
            goal="You're an Expert Prompt Engineer. Your role is to help users craft the most effective and well-structured prompts tailored for GPT-3, GPT-4, or ChatGPT. You should write prompts from the users perspective, using their communication style. Your responses must follow a fixed format with three sections: Prompt, Critique, and Questions. Be constructive, imaginative, and highly detail-oriented in refining prompts. Be critical in your feedback to ensure the best quality. Do not generate a final prompt until you have enough context. Always begin by greeting the user and asking what the prompt should be about.",
            backstory="""You are an expert in creating prompts that get the best results from AI systems.
            You understand the nuances of language that lead to optimal AI responses.""",
            llm=llm,
            verbose=True
        )
        
        # Define the prompt critic agent
        add_debug("Creating Prompt Critic agent...")
        prompt_critic = Agent(
            role="Prompt Evaluation Specialist",
            goal="Critically evaluate prompts and suggest improvements",
            backstory="""You meticulously analyze prompts for ambiguities, missing context, 
            and potential improvements. You know how to turn good prompts into great ones.""",
            llm=llm,
            verbose=True
        )
        
        # Define the prompt synthesizer agent
        add_debug("Creating Prompt Synthesizer agent...")
        prompt_synthesizer = Agent(
            role="Prompt Refinement Expert",
            goal="Synthesize feedback and create improved versions of prompts",
            backstory="""You specialize in incorporating feedback to refine prompts.
            You can balance multiple considerations and produce optimized results.""",
            llm=llm,
            verbose=True
        )
        
        # Define the initial prompt creation task
        add_debug("Creating prompt creation task...")
        prompt_creation_task = Task(
            description=f"""
            Create an effective prompt based on the user's needs.
            
            User Input: {user_input}
            
            Help the user craft a high-quality prompt written from their point of view to be used in GPT-3, GPT-4, or ChatGPT. Include three sections in your response:
            1. **Prompt:** Generate a clear and well-written prompt based on the user's input and mimic their communication style using examples from prior messages.
            2. **Critique:** Provide a concise yet critical analysis of the prompt and suggest ways to improve it. Even if the prompt is good, find something that could be optimized.
            3. **Questions:** Ask up to 3 specific questions to get more clarity, details, or examples needed to further enhance the prompt.

            This is an iterative process. After receiving user answers, you must refine the prompt and repeat the same structure until it's perfected.
            this is the user feedback for the 3 questions, if its None then ignore it else use it to create the prompt again:
            {feedback}
            """,
            agent=prompt_engineer,
            expected_output="""A well-crafted prompt based on user needs and the 3 questions"""
        )
        
        # Define the prompt evaluation task
        add_debug("Creating prompt evaluation task...")
        prompt_evaluation_task = Task(
            description="""
            Evaluate the prompt created by the Prompt Engineer. Consider:
            1. Clarity and specificity
            2. Potential ambiguities or misinterpretations
            3. Missing context or information
            
            Structure your output as:
            
            ## Evaluation
            [Your evaluation here]
            
            ## Critical Questions
            [List exactly 3 questions that would help refine this prompt further]
            """,
            agent=prompt_critic,
            context=[prompt_creation_task],
            expected_output="""An evaluation of the prompt with 3 critical questions for refinement."""
        )
        
        # If feedback is provided, add a refinement task
        tasks = [prompt_creation_task, prompt_evaluation_task]
        
        if feedback:
            add_debug("Creating refinement task with feedback...")
            refinement_task = Task(
                description=f"""
                Refine the prompt based on the user's feedback.
                
                Original Prompt: {st.session_state.prompt_history[-1]['prompt']}
                
                User Feedback:
                {feedback}
                
                Create an improved version of the prompt that addresses the feedback.
                Structure your output as:
                
                ## Refined Prompt
                [Your refined prompt here]
                
                ## Improvements Made
                [Brief explanation of changes and how they address the feedback]
                
                ## Follow-up Questions
                [List exactly 3 questions that would help refine this prompt even further]
                """,
                agent=prompt_synthesizer,
                context=[prompt_creation_task, prompt_evaluation_task],
                expected_output="""A refined prompt incorporating user feedback, with explanation of improvements and 3 follow-up questions."""
            )
            tasks.append(refinement_task)
        
        # Create and run the crew
        add_debug("Creating crew with configured agents and tasks...")
        crew = Crew(
            agents=[prompt_engineer, prompt_critic, prompt_synthesizer],
            tasks=tasks,
            verbose=True,
            process=Process.sequential
        )
        
        add_debug("Kicking off the crew...")
        result = crew.kickoff()
        
        # Extract the text content from the CrewOutput object
        # In newer versions of CrewAI, result might be a CrewOutput object with different attributes
        if hasattr(result, 'raw'):
            output_text = result.raw
        elif hasattr(result, 'content'):
            output_text = result.content
        elif hasattr(result, 'output'):
            output_text = result.output
        elif hasattr(result, 'result'):
            output_text = result.result
        elif hasattr(result, 'data'):
            output_text = result.data
        elif hasattr(result, 'text'):
            output_text = result.text
        elif hasattr(result, 'value'):
            output_text = result.value
        elif hasattr(result, '__str__'):
            # Fallback to string representation
            output_text = str(result)
        else:
            # Last resort - convert to string directly
            output_text = f"{result}"
        
        add_debug(f"Crew result received. Type: {type(result)}, Output text length: {len(output_text)} characters")
        
        # Display result attributes for debugging
        add_debug(f"Result attributes: {dir(result)}")
        
        return output_text
    except Exception as e:
        error_msg = f"Error in crew execution: {str(e)}"
        add_debug(error_msg)
        add_debug(traceback.format_exc())
        return f"Error occurred: {error_msg}\n\nTraceback: {traceback.format_exc()}"

# Function to parse crew output
def parse_output(crew_output, is_refinement=False):
    try:
        add_debug(f"Parsing output: {crew_output[:100] if isinstance(crew_output, str) else 'Non-string output'}...")
        
        # Ensure we're working with a string
        if not isinstance(crew_output, str):
            crew_output = str(crew_output)
            
        output_sections = {}
        
        # Extract different sections from crew output
        if "## Generated Prompt" in crew_output:
            add_debug("Found '## Generated Prompt' section")
            parts = crew_output.split("## Generated Prompt")
            prompt_and_rest = parts[1].split("##", 1)
            output_sections["prompt"] = prompt_and_rest[0].strip()
            
            if "## Evaluation" in crew_output:
                add_debug("Found '## Evaluation' section")
                eval_parts = crew_output.split("## Evaluation")
                eval_and_rest = eval_parts[1].split("##", 1)
                output_sections["evaluation"] = eval_and_rest[0].strip()
                
            if "## Critical Questions" in crew_output:
                add_debug("Found '## Critical Questions' section")
                question_parts = crew_output.split("## Critical Questions")
                output_sections["questions"] = question_parts[1].strip()
        
        # Handle refinement output format
        elif is_refinement or "## Refined Prompt" in crew_output:
            add_debug("Processing refinement output")
            parts = crew_output.split("## Refined Prompt")
            if len(parts) > 1:
                prompt_and_rest = parts[1].split("##", 1)
                output_sections["prompt"] = prompt_and_rest[0].strip()
                
                if "## Improvements Made" in crew_output:
                    improvements_parts = crew_output.split("## Improvements Made")
                    improvements_and_rest = improvements_parts[1].split("##", 1)
                    output_sections["improvements"] = improvements_and_rest[0].strip()
                    
                if "## Follow-up Questions" in crew_output:
                    question_parts = crew_output.split("## Follow-up Questions")
                    output_sections["questions"] = question_parts[1].strip()
        
        # If no structured format is found, try to extract something useful
        if not output_sections and len(crew_output) > 50:
            add_debug("No structured format found, attempting to extract content")
            # Look for anything that might be a prompt
            if "prompt:" in crew_output.lower():
                prompt_parts = crew_output.lower().split("prompt:")
                if len(prompt_parts) > 1:
                    # Take the text after "prompt:" until the next section marker or end
                    potential_prompt = prompt_parts[1].split("\n\n", 1)[0] if "\n\n" in prompt_parts[1] else prompt_parts[1]
                    output_sections["prompt"] = potential_prompt.strip()
            else:
                # Just use the whole output as the prompt if we can't find a specific section
                output_sections["prompt"] = crew_output.strip()
        
        # Extract the questions as a list
        questions = []
        if "questions" in output_sections:
            for line in output_sections["questions"].split("\n"):
                line = line.strip()
                if line and (line.startswith("- ") or line.startswith("* ") or 
                            line.startswith("1. ") or line.startswith("2. ") or line.startswith("3. ")):
                    questions.append(line.lstrip("- *123. "))
                elif line and len(line) > 10:  # Simple heuristic to catch non-formatted questions
                    questions.append(line)
        
        # If no questions found but we have some output, generate default questions
        if not questions and output_sections:
            questions = [
                "How can we make this prompt more specific to your needs?",
                "Is there any context or information missing from this prompt?",
                "What aspects of the prompt would you like to improve or refine?"
            ]
        
        # Limit to 3 questions
        questions = questions[:3]
        
        add_debug(f"Parsing complete. Found {len(output_sections)} sections and {len(questions)} questions")
        return output_sections, questions
    except Exception as e:
        error_msg = f"Error parsing output: {str(e)}"
        add_debug(error_msg)
        add_debug(traceback.format_exc())
        return {"error": error_msg}, ["What went wrong?", "How can we fix it?", "Should we try again?"]

# Check if API is configured
api_configured = setup_gemini_api()

# Only show the main interface if API is configured
if api_configured:
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Initial prompt input area
        if st.session_state.current_iteration == 0:
            user_input = st.text_area("Describe what you need a prompt for:", 
                                    height=150,
                                    placeholder="Example: I need a prompt that will help generate creative marketing ideas for a new eco-friendly household product.")
            
            submit_button = st.button("Generate Prompt")
            
            if submit_button:
                if not user_input:
                    st.error("Please enter a description of what you need a prompt for.")
                else:
                    st.info("Button clicked. Processing request...")
                    with st.spinner("Creating your prompt..."):
                        try:
                            add_debug("Starting crew execution...")
                            result = create_prompt_engineering_crew(user_input)
                            
                            # Display raw output in debug
                            with st.sidebar.expander("Raw Output", expanded=False):
                                st.text(result)
                            
                            output_sections, questions = parse_output(result)
                            
                            if "error" in output_sections:
                                st.error(output_sections["error"])
                            elif "prompt" in output_sections:
                                add_debug("Successfully extracted prompt and questions")
                                st.session_state.prompt_history.append({
                                    "prompt": output_sections["prompt"],
                                    "evaluation": output_sections.get("evaluation", ""),
                                    "user_input": user_input
                                })
                                st.session_state.feedback_questions = questions
                                st.session_state.current_iteration += 1
                                st.rerun()
                            else:
                                st.error("Failed to parse prompt from output")
                                st.write("Output sections:", output_sections)
                        except Exception as e:
                            st.error(f"Error occurred: {str(e)}")
                            st.code(traceback.format_exc())
                            add_debug(f"Error: {str(e)}")
        
        # Display current prompt and feedback area
        elif st.session_state.current_iteration > 0:
            st.subheader("Generated Prompt:")
            st.markdown(f"""```
{st.session_state.prompt_history[-1]['prompt']}
```""")
            
            if st.session_state.prompt_history[-1].get("evaluation"):
                with st.expander("View Evaluation"):
                    st.markdown(st.session_state.prompt_history[-1]["evaluation"])
            
            st.subheader("Refinement Questions:")
            for i, question in enumerate(st.session_state.feedback_questions):
                st.markdown(f"**{i+1}.** {question}")
            
            feedback = st.text_area("Answer the questions above to refine your prompt (or type 'None' to finalize):", 
                                height=150,
                                placeholder="Provide your answers to help refine the prompt further...")
            
            col1a, col1b = st.columns([1, 1])
            with col1a:
                refine_button = st.button("Refine Prompt")
            with col1b:
                finalize_button = st.button("Finalize Prompt")
            
            if refine_button:
                if not feedback:
                    st.error("Please provide feedback to refine the prompt.")
                elif feedback.strip().lower() == "none":
                    st.session_state.final_prompt = st.session_state.prompt_history[-1]["prompt"]
                    st.success("Prompt finalized!")
                else:
                    st.info("Refining prompt with your feedback...")
                    with st.spinner("Refining your prompt..."):
                        try:
                            add_debug("Starting refinement with feedback...")
                            result = create_prompt_engineering_crew(st.session_state.prompt_history[0]["user_input"], feedback)
                            
                            # Display raw output in debug
                            with st.sidebar.expander("Refinement Raw Output", expanded=False):
                                st.text(result)
                            
                            output_sections, questions = parse_output(result, is_refinement=True)
                            
                            if "error" in output_sections:
                                st.error(output_sections["error"])
                            elif "prompt" in output_sections:
                                add_debug("Successfully extracted refined prompt and questions")
                                st.session_state.prompt_history.append({
                                    "prompt": output_sections["prompt"],
                                    "improvements": output_sections.get("improvements", ""),
                                    "feedback": feedback
                                })
                                st.session_state.feedback_questions = questions
                                st.session_state.current_iteration += 1
                                st.experimental_rerun()
                            else:
                                st.error("Failed to parse refined prompt from output")
                                st.write("Output sections:", output_sections)
                        except Exception as e:
                            st.error(f"Error occurred during refinement: {str(e)}")
                            st.code(traceback.format_exc())
                            add_debug(f"Refinement Error: {str(e)}")
            
            if finalize_button:
                st.session_state.final_prompt = st.session_state.prompt_history[-1]["prompt"]
                st.success("Prompt finalized!")

    # Sidebar with history and settings
    with col2:
        st.subheader("Prompt History")
        
        if not st.session_state.prompt_history:
            st.info("No prompts generated yet.")
        else:
            for i, entry in enumerate(st.session_state.prompt_history):
                with st.expander(f"Iteration {i+1}"):
                    st.markdown("**Prompt:**")
                    st.markdown(f"""```
{entry['prompt']}
```""")
                    
                    if "evaluation" in entry and entry["evaluation"]:
                        st.markdown("**Evaluation:**")
                        st.markdown(entry["evaluation"])
                    
                    if "improvements" in entry and entry["improvements"]:
                        st.markdown("**Improvements:**")
                        st.markdown(entry["improvements"])
                    
                    if "feedback" in entry and entry["feedback"]:
                        st.markdown("**Your Feedback:**")
                        st.markdown(entry["feedback"])
        
        # Final prompt display
        if st.session_state.final_prompt:
            st.subheader("🎯 Final Prompt")
            st.code(st.session_state.final_prompt, language="markdown")
            
            # Add copy button
            if st.button("Copy to Clipboard"):
                st.code(st.session_state.final_prompt)
                st.success("Copied to clipboard!")
                
            # Add download button
            st.download_button(
                label="Download Prompt",
                data=st.session_state.final_prompt,
                file_name="optimized_prompt.txt",
                mime="text/plain"
            )

    # Add a section to restart the process
    if st.session_state.current_iteration > 0:
        if st.button("Start Over with New Prompt"):
            add_debug("Restarting the process...")
            st.session_state.prompt_history = []
            st.session_state.current_iteration = 0
            st.session_state.feedback_questions = []
            st.session_state.final_prompt = ""
            st.rerun()

else:
    st.warning("Please configure the Google API in the sidebar to continue.")

# Add a simple CrewAI version check
try:
    import crewai
    st.sidebar.markdown(f"CrewAI version: {crewai.__version__}")
except:
    st.sidebar.markdown("CrewAI version: Unknown")

# Display version info
st.sidebar.markdown("---")
st.sidebar.caption("Prompt Engineering Agent v1.1")
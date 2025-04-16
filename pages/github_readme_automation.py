import base64
import requests
import streamlit as st
from agno.agent import Agent
from agno.tools.github import GithubTools
from agno.models.groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["GITHUB_ACCESS_TOKEN"] = os.getenv("GITHUB_ACCESS_TOKEN")
GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
GITHUB_USERNAME = "KrishBhimani"

# Streamlit app title and description
st.title("GitHub README Generator")
st.write("Automatically generate a structured README file for your GitHub repository.")

# Explanation about the agent
st.subheader("About the Agent")
st.write("""
This agent analyzes the given GitHub repository and automatically generates a structured README file based on your preferences.
The README will include key details like features, installation steps, usage instructions, technologies used, challenges & solutions, and contribution guidelines.
You can customize the type of README (detailed, minimal, or technical) and decide whether to include the installation guide and technologies used.
""")

# Input for repository name
repo_name = st.text_input("Enter the repository name:", placeholder="e.g., version-control-practice")

# Dropdown for README type
readme_type = st.selectbox(
    "Select the type of README you want to generate:",
    ["detailed", "minimal", "technical"]
)

# Radio button to include installation guide and technologies
include_installation = st.radio(
    "Do you want to include the installation guide and technologies in the README?",
    ("Yes", "No")
)

if st.button("Generate README"):
    if repo_name:
        repo = GITHUB_USERNAME + '/' + repo_name

        # Customize instructions based on user input
        instructions = f"""
            Analyze the repository {repo} and generate a structured README file.Dont create anything apart from the readme file. Extract key details like features, installation steps, usage instructions, technologies used, challenges & solutions, and contribution guidelines. The content should only contain the README content and nothing else. Make sure the technologies used must match with those in the repository, you can refer to the code in the individual files. Format it as follows:

            # [Project Name]<the name should be meaningful and bold and capitalize>

            A brief one-line description of the project.<use llm to add more information as well>

            ## 🚀 Features

            - Summarize the key functionalities concisely.
            - Highlight any AI models, automation, or key differentiators.
        """
        
        if include_installation == "Yes":
            instructions += """
            ## 🕠️ Installation

            ### 1 Clone the Repository

            ```sh
            git clone [repo_link]
            ```

            ### 2 Create a Virtual Environment

            #### For Windows:
            ```sh
            conda create -p venv python==3.11 -y
            conda activate venv/
            ```

            #### For macOS/Linux:
            ```sh
            python3 -m venv venv
            source venv/bin/activate
            ```

            ### 3 Install Dependencies

            ```sh
            pip install -r requirements.txt
            ```

            ### 4 Run the Application

            ```sh
            [Run Command]
            ```

            """
        
        if readme_type == "detailed":
            instructions += """
            ## 📌 Usage

            1. Explain how users can interact with the project step-by-step.
            2. Provide key use cases or examples.

            ## 🔧 Technologies Used

            **List all major technologies, frameworks, and APIs used in development.**

            ## 🚀 Challenges & Solutions

            - **Describe major challenges encountered.**
            - **Explain how they were solved.**

            ## 🤝 Contributing

            Contributions are welcome! Feel free to submit **issues** or **pull requests** to improve this project.

            ---
            """

        elif readme_type == "minimal":
            instructions += """
            ## 📌 Usage

            - Brief explanation of usage or key features.
            
            ## 🤝 Contributing

            Contributions are welcome!

            ---
            """

        elif readme_type == "technical":
            instructions += """
            ## 🔧 Technologies Used

            **Provide a list of all technologies used, frameworks, and APIs used in development.**

            ## 🚀 Challenges & Solutions

            - **Describe technical challenges encountered.**
            - **Explain the technical solutions implemented.**

            ---
            """

        # Create an agent with the customized instructions
        agent = Agent(
            model=Groq(id="meta-llama/llama-4-scout-17b-16e-instruct"),
            instructions=[instructions],
            tools=[GithubTools()],
            show_tool_calls=True,
        )

        try:
            response = agent.run("create a readme template for a repository", markdown=True)

            # Content of the README file
            README_CONTENT = response.content
            
            # Encode content in Base64
            encoded_content = base64.b64encode(README_CONTENT.encode("utf-8")).decode("utf-8")

            # API URL for the README file
            API_URL = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/contents/README.md"

            # Get the current file SHA (required for updates)
            get_response = requests.get(
                API_URL,
                headers={"Authorization": f"Bearer {GITHUB_ACCESS_TOKEN}"}
            )
            if get_response.status_code == 200:
                sha = get_response.json().get("sha")
            else:
                sha = None

            # Data for the API request
            data = {
                "message": "Add/Update README.md",
                "content": encoded_content,
            }
            if sha:
                data["sha"] = sha

            # Make the API request to create or update the README file
            put_response = requests.put(
                API_URL,
                json=data,
                headers={"Authorization": f"Bearer {GITHUB_ACCESS_TOKEN}"}
            )

            if put_response.status_code in [200, 201]:
                st.success("README.md successfully added/updated!")
            else:
                st.error(f"Failed to add/update README.md: {put_response.json()}")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a repository name.")

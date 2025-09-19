FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directories that might be needed
RUN mkdir -p pages/tmp

# Note about environment variables
# The application requires various API keys to be set as environment variables
# These can be provided when running the container:
# docker run -p 8501:8501 -e OPENAI_API_KEY=your_key -e GITHUB_ACCESS_TOKEN=your_token ... agent-library

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "app.py"]

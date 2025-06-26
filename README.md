# CreationAgent

A Streamlit-based app for creating, roleplaying, and chatting with AI-powered characters and worlds. Design unique characters, generate interactive stories, and chat with your creations using Google Gemini AI.

## Features
- **Character Creation:** Design characters with custom names, roles, personalities, and more.
- **Roleplay World Creation:** Build interactive worlds and story templates.
- **AI Chat:** Chat with your characters, with memories and relationship tracking.
- **Gemini AI Integration:** Uses Google Gemini for natural language generation and memory extraction.

## Installation
1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd CreationAgent
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## API Key Setup (Google Gemini)
This app requires a Gemini API key. You must add your key to a Streamlit secrets file:

1. Create a folder named `.streamlit` in the project root (if it doesn't exist):
   ```bash
   mkdir -p .streamlit
   ```
2. Create a file named `secrets.toml` inside `.streamlit`:
   ```toml
   [secrets]
   GEMINI_API_KEY = "your-gemini-api-key-here"
   ```
   Replace `your-gemini-api-key-here` with your actual Gemini API key.

## Usage
1. **Run the app:**
   ```bash
   streamlit run sekai_creation_agent_app.py
   ```
2. Open your browser and go to the URL shown in the terminal (usually http://localhost:8501).
3. Choose a mode (Character Creation or Roleplay Creation) and follow the on-screen steps.

## Troubleshooting
- If you see errors about missing API keys, make sure your `.streamlit/secrets.toml` file is present and correctly formatted.
- For best results, use Python 3.8 or higher.
- If you have issues with dependencies, try upgrading pip: `pip install --upgrade pip`.

## License
MIT

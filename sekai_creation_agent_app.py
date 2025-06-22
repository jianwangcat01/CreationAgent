# sekai_creation_agent_app.py

import streamlit as st
import google.generativeai as genai
import json

# --- Config ---
st.set_page_config(page_title="Sekai Creation Agent", layout="wide")
st.title("Sekai AI Creation Agent")

# --- Gemini API Setup ---
with st.sidebar:
    st.header("🔐 API Settings")
    api_key = st.text_input("Enter your Gemini API Key", type="password")
    model_type = st.selectbox("Model", ["gemini-2.5-flash"])

if not api_key:
    st.warning("Please enter your Gemini API key to start.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_type)

# --- Step 1: Define World ---
st.subheader("1. Define Your Sekai World")
world_title = st.text_input("Sekai Title", "Midnight Library")
world_setting = st.text_area("World Setting", "A magical library that only appears at midnight, where books come alive.")
world_genre = st.multiselect("Genre(s)", ["Fantasy", "Romance", "Mystery", "Sci-fi", "Horror"], default=["Fantasy"])

# --- Step 2: Define Characters ---
st.subheader("2. Create Main Characters")
num_characters = st.slider("Number of Characters", 1, 5, 2)
characters = []
for i in range(num_characters):
    with st.expander(f"Character {i+1}"):
        name = st.text_input(f"Name {i+1}", key=f"name_{i}")
        role = st.text_input(f"Role {i+1}", key=f"role_{i}")
        trait = st.text_input(f"Key Traits {i+1}", key=f"trait_{i}")
        characters.append({"name": name, "role": role, "traits": trait})

# --- Step 3: Generate Sekai JSON ---
st.subheader("3. Generate Sekai Story Template")
if st.button("✨ Generate with Gemini"):
    with st.spinner("Talking to Gemini AI..."):
        prompt = f"""
You are an AI agent for building interactive fanfiction worlds.
Create a JSON-based story template using the following input:

Title: {world_title}
Setting: {world_setting}
Genre: {', '.join(world_genre)}
Characters:
"""
        for c in characters:
            prompt += f"- {c['name']} ({c['role']}): {c['traits']}\n"

        prompt += "\nRespond ONLY with raw JSON. Do not wrap the output in code blocks or explanations."

        response = model.generate_content(prompt)
        output = response.text.strip()

        # --- Clean up triple backticks if present ---
        if output.startswith("```json"):
            output = output.replace("```json", "").strip()
        if output.endswith("```"):
            output = output[:-3].strip()

        try:
            sekai_json = json.loads(output)
            st.success("Sekai story template generated!")
            st.json(sekai_json)
            st.download_button("Download JSON", json.dumps(sekai_json, indent=2), file_name="sekai_story.json")
        except json.JSONDecodeError:
            st.error("Failed to parse JSON. Please try again or check your prompt.")
            st.code(output)

st.caption("Built by Claire Wang for the Sekai PM Take-Home Project ✨")

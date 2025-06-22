# sekai_creation_agent_app.py (upgraded for generative input + game start)

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

# --- Helper: Generate Suggestions ---
def generate_field(prompt):
    response = model.generate_content(prompt)
    return response.text.strip()

# --- Step 1: Define World ---
st.subheader("1. Define Your Sekai World")
col1, col2 = st.columns([3, 1])
with col1:
    world_idea = st.text_input("Describe your world idea (or leave blank to write manually)", "Midnight Library")
    if st.button("🧠 AI: Suggest World"):
        suggestion = generate_field(f"Suggest a detailed setting, title and genre based on the idea: '{world_idea}'")
        st.session_state["world_suggestion"] = suggestion
    world_title = st.text_input("Sekai Title", st.session_state.get("world_suggestion", "Midnight Library"))
    world_setting = st.text_area("World Setting", "A magical library that only appears at midnight, where books come alive.")
    world_genre = st.multiselect("Genre(s)", ["Fantasy", "Romance", "Mystery", "Sci-fi", "Horror"], default=["Fantasy"])

# --- Step 2: Define Characters ---
st.subheader("2. Create Main Characters")
num_characters = st.slider("Number of Characters", 1, 5, 2)
characters = []

for i in range(num_characters):
    with st.expander(f"Character {i+1}"):
        idea = st.text_input(f"Character Idea {i+1}", key=f"idea_{i}")
        if st.button(f"🧠 AI: Generate Character {i+1}", key=f"gen_{i}"):
            prompt = f"Write a name, role, and personality traits for a character based on: {idea}"
            result = generate_field(prompt)
            st.session_state[f"char_{i}"] = result
        default_text = st.session_state.get(f"char_{i}", "Name: , Role: , Traits: ")
        name = st.text_input(f"Name {i+1}", key=f"name_{i}", value=default_text.split('Name: ')[-1].split(',')[0].strip())
        role = st.text_input(f"Role {i+1}", key=f"role_{i}", value=default_text.split('Role: ')[-1].split(',')[0].strip())
        trait = st.text_input(f"Key Traits {i+1}", key=f"trait_{i}", value=default_text.split('Traits: ')[-1].strip())
        characters.append({"name": name, "role": role, "traits": trait})

# --- Step 3: Generate Sekai JSON ---
st.subheader("3. Generate Sekai Story Template")
if st.button("✨ Generate Template"):
    with st.spinner("Talking to Gemini AI..."):
        prompt = f"""
You are an AI for building JSON-based interactive stories.
Generate a story JSON with: title, setting, genre, characters (array of name, role, description), and openingScene.

Title: {world_title}
Setting: {world_setting}
Genre: {', '.join(world_genre)}
Characters:
"""
        for c in characters:
            prompt += f"- {c['name']} ({c['role']}): {c['traits']}\n"
        prompt += "\nRespond with raw JSON only."

        response = model.generate_content(prompt)
        output = response.text.strip()

        if output.startswith("```json"):
            output = output.replace("```json", "").strip()
        if output.endswith("```"):
            output = output[:-3].strip()

        try:
            sekai_json = json.loads(output)
            st.session_state["sekai_json"] = sekai_json
            st.success("Sekai story template generated!")
            st.json(sekai_json)
        except json.JSONDecodeError:
            st.error("Failed to parse JSON. Please try again.")
            st.code(output)

# --- Step 4: Start the Game ---
if "sekai_json" in st.session_state:
    st.subheader("4. Start Your Sekai Interactive Game")
    if st.button("🎮 Start Game"):
        story_prompt = f"""You are the game narrator. Begin the interactive story using the setting below.
Let each character speak in turn. Occasionally, ask the user for a response and wait for their input.

JSON:
{json.dumps(st.session_state['sekai_json'], indent=2)}
"""
        st.session_state["game_state"] = [model.generate_content(story_prompt).text.strip()]

# --- Step 5: Game UI ---
if "game_state" in st.session_state:
    st.markdown("---")
    st.subheader("🚀 Game In Progress")

    for block in st.session_state["game_state"]:
        st.markdown(block)

    if "user_reply" not in st.session_state:
    st.session_state["user_reply"] = ""
if "send_triggered" not in st.session_state:
    st.session_state["send_triggered"] = False

user_input = st.text_input("Your reply", value=st.session_state["user_reply"], key="reply_input")

if st.button("🔄 Send"):
    st.session_state["send_triggered"] = True
    st.session_state["user_reply"] = user_input

if st.session_state.get("send_triggered", False):
    st.session_state["send_triggered"] = False  # reset trigger
    if st.session_state["user_reply"]:
        last_turn = st.session_state["game_state"][-1]
        reply_prompt = f"Continue the interactive story. The user replied: '{st.session_state['user_reply']}'. Respond with the next part."
        new_turn = model.generate_content(last_turn + "\n\n" + reply_prompt).text.strip()
        st.session_state["game_state"].append(new_turn)
        st.session_state["user_reply"] = ""  # safe now


# ... footer unchanged ...
st.caption("Built by Claire Wang for the Sekai PM Take-Home Project ✨")

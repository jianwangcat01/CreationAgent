import streamlit as st
import google.generativeai as genai
import json
import random

# --- Page Config ---
st.set_page_config(page_title="Sekai Creation Agent", layout="wide")
st.title("Sekai AI Creation Agent")

# --- Gemini API Setup (from secrets) ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model_type = "gemini-2.5-flash"
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
    if st.button("\U0001F9E0 AI: Suggest World"):
        suggestion = generate_field(f"Suggest a detailed setting, title and genre based on the idea: '{world_idea}'")
        st.session_state["world_suggestion"] = suggestion
    world_title = st.text_input("Sekai Title", st.session_state.get("world_suggestion", "Midnight Library"))
    world_setting = st.text_area("World Setting", "A magical library that only appears at midnight, where books come alive.", height=120)
    world_genre = st.multiselect("Genre(s)", ["Fantasy", "Romance", "Mystery", "Sci-fi", "Horror"], default=["Fantasy"])
    user_name = st.text_input("Your Character Name (You will be part of the story)", "Alex")
    user_traits = st.text_area("Your Character Traits", "Curious, brave, and a quick thinker", height=100)

# --- Step 2: Define Characters ---
st.subheader("2. Create Main Characters")
num_characters = st.slider("Number of Characters", 1, 5, 2)
characters = []

if st.button("✨ Generate All Characters"):
    for i in range(num_characters):
        idea = st.session_state.get(f"idea_{i}", "")
        prompt = (
            f"Based on the following idea, create a character with the following format:\n\n"
            f"Name: <Character Name>\n"
            f"Role: <Character Role>\n"
            f"Traits: <Personality traits and special abilities>\n\n"
            f"Idea: {idea if idea else f'A new character that fits this setting: {world_setting}'}"
        )
        result = generate_field(prompt)
        st.session_state[f"char_{i}"] = result

for i in range(num_characters):
    with st.expander(f"Character {i+1}"):
        idea = st.text_input(f"Character Idea {i+1}", key=f"idea_{i}")
        if st.button(f"\U0001F9E0 AI: Generate Character {i+1}", key=f"gen_{i}"):
            prompt = (
                f"Based on the following idea, create a character with the following format:\n\n"
                f"Name: <Character Name>\n"
                f"Role: <Character Role>\n"
                f"Traits: <Personality traits and special abilities>\n\n"
                f"Idea: {idea}"
            )
            result = generate_field(prompt)
            st.session_state[f"char_{i}"] = result

        default_text = st.session_state.get(f"char_{i}", "")
        parsed_name, parsed_role, parsed_traits = "", "", ""
        if "Name:" in default_text and "Role:" in default_text and "Traits:" in default_text:
            try:
                parsed_name = default_text.split("Name:")[1].split("Role:")[0].strip()
                parsed_role = default_text.split("Role:")[1].split("Traits:")[0].strip()
                parsed_traits = default_text.split("Traits:")[1].strip()
            except Exception:
                parsed_name, parsed_role, parsed_traits = "", "", ""

        name = st.text_input(f"Name {i+1}", key=f"name_{i}", value=parsed_name)
        role = st.text_input(f"Role {i+1}", key=f"role_{i}", value=parsed_role)
        trait = st.text_area(f"Key Traits {i+1}", key=f"trait_{i}", value=parsed_traits, height=100)
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
- {user_name} (Player): {user_traits}
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
    st.markdown("""
📜 In this game, please:
- Type your character's dialogue normally: e.g., `What are you doing here?`
- Type your character's **actions** with asterisks: e.g., `*run away from the library*`
    """)
    if st.button("\U0001F3AE Start Game"):
        story_prompt = f"""You are the game narrator. Begin the interactive story using a visual novel script format.
Limit narration to short sentences. Prioritize character dialogue and inner thoughts.
Include the player character: {user_name}.

JSON:
{json.dumps(st.session_state['sekai_json'], indent=2)}
"""
        st.session_state["game_state"] = [model.generate_content(story_prompt).text.strip()]
        st.session_state["story_colors"] = [random.choice(["#fce4ec", "#e3f2fd", "#e8f5e9", "#fff8e1", "#ede7f6"])]

# --- Step 5: Game UI ---
if "game_state" in st.session_state:
    st.markdown("---")
    st.subheader("🚀 Game In Progress")

    for i, block in enumerate(st.session_state["game_state"]):
        color = st.session_state.get("story_colors", ["#e3f2fd"])[i % len(st.session_state["story_colors"])]
        st.markdown(f'<div style="background-color:{color}; padding:10px; border-radius:8px">{block}</div>', unsafe_allow_html=True)

    user_input = st.text_input("Your reply", key="reply_input")

    if st.button("🔄 Send"):
        if user_input.strip():
            last_turn = st.session_state["game_state"][-1]
            reply_prompt = (
                f"Continue the visual novel format story. The player said or did: '{user_input}'."
                f" Focus on character dialogue and thoughts. Keep narration brief."
            )
            new_turn = model.generate_content(last_turn + "\n\n" + reply_prompt).text.strip()
            st.session_state["game_state"].append(new_turn)
            # Assign a new color different from the last
            existing_colors = st.session_state.get("story_colors", [])
            available_colors = [c for c in ["#fce4ec", "#e3f2fd", "#e8f5e9", "#fff8e1", "#ede7f6"] if c != existing_colors[-1]]
            new_color = random.choice(available_colors)
            st.session_state["story_colors"].append(new_color)
            st.rerun()

# Footer
st.caption("Built by Claire Wang for the Sekai PM Take-Home Project ✨")

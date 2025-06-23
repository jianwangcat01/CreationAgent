import streamlit as st
import google.generativeai as genai
import json
import random

# --- Page Config ---
st.set_page_config(page_title="Sekai Creation Agent", layout="wide")
st.title("Sekai AI Creation Agent")

# --- Gemini API Setup (from secrets) ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model_type = "gemini-2.5-flash-lite-preview-06-17"
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
    existing = []
    for i in range(num_characters):
        idea = st.session_state.get(f"idea_{i}", "")
        prompt = (
            f"Create a completely unique and different character for the world: {world_setting}.\n"
            f"Avoid using any of the following names: {', '.join([c['name'] for c in existing])}.\n"
            f"Ensure the name, personality, and abilities are distinct from existing characters.\n"
            "\nRespond in this format:\n"
            "Name: <Character Name>\n"
            "Role: <Character Role>\n"
            "Traits: <Personality traits and special abilities>"
        )

        result = generate_field(prompt)
        st.session_state[f"char_{i}"] = result

for i in range(num_characters):
    with st.expander(f"Character {i+1}"):
        idea = st.text_input(f"Character Idea {i+1}", key=f"idea_{i}")
        if st.button(f"\U0001F9E0 AI: Generate Character {i+1}", key=f"gen_{i}"):
            other_chars = [st.session_state.get(f"char_{j}", "") for j in range(num_characters) if j != i]
            prompt = (
                f"Create a new character for the following world: {world_setting}. "
                f"Ensure this character is clearly different from any existing characters:\n"
                + "\n".join(other_chars) +
                "\n\nRespond in this format:\n"
                "Name: <Character Name>\n"
                "Role: <Character Role>\n"
                "Traits: <Personality traits and special abilities>"
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

# --- Step 3: Generate Sekai Story Template ---
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
    story_prompt = f"""
You are an interactive fiction narrator for a visual novel.
Begin the story using the following JSON world structure.
Write the story in the following script format:

narrator "<scene description>"
character tone "<dialogue or thoughts>"

Rules:
- Use narrator and character lines as shown.
- Focus on character dialogue and internal thoughts.
- Avoid long narration.
- Do NOT offer multiple choice options or suggestions.
- End with: **\"What do you do?\"**

JSON:
{json.dumps(st.session_state['sekai_json'], indent=2)}

Write the opening scene below:
"""
    first_turn = model.generate_content(story_prompt).text.strip()

    if first_turn.startswith("{") or first_turn.startswith('"title"'):
        st.error("Model returned raw JSON instead of story text. Please retry.")
    else:
        st.session_state["game_state"] = [first_turn]
        st.session_state["story_colors"] = [random.choice(["#fce4ec", "#e3f2fd", "#e8f5e9", "#fff8e1", "#ede7f6"])]
        st.session_state["user_inputs"] = [""]

# --- Step 5: Game UI ---
if "game_state" in st.session_state:
    st.markdown("---")
    st.subheader("🚀 Game In Progress")

    for i, (block, user_input) in enumerate(zip(st.session_state["game_state"], st.session_state["user_inputs"])):
        color = st.session_state.get("story_colors", ["#e3f2fd"])[i % len(st.session_state["story_colors"])]
        user_reply_html = f'<p style="margin-bottom:4px;"><b>Your input:</b> {user_input}</p>' if user_input.strip() else ""
        st.markdown(f'<div style="background-color:{color}; padding:10px; border-radius:8px">{user_reply_html}{block}</div>', unsafe_allow_html=True)

    user_input = st.text_input("Enter your next action or dialogue", key="reply_input")
    if st.button("🔄 Send"):
        if user_input.strip():
            last_turn = st.session_state["game_state"][-1]
            reply_prompt = (
                f"Continue the story in script format. The player said or did: '{user_input}'. "
                f"Focus on character dialogue and thoughts. Keep narration brief. Do not give choices."
            )
            new_turn = model.generate_content(last_turn + "\n\n" + reply_prompt).text.strip()
            st.session_state["game_state"].append(new_turn)
            st.session_state["user_inputs"].append(user_input.strip())
            existing_colors = st.session_state.get("story_colors", [])
            available_colors = [c for c in ["#fce4ec", "#e3f2fd", "#e8f5e9", "#fff8e1", "#ede7f6"] if c != existing_colors[-1]]
            new_color = random.choice(available_colors)
            st.session_state["story_colors"].append(new_color)
            st.rerun()

# Footer
st.caption("Built by Claire Wang for the Sekai PM Take-Home Project ✨")

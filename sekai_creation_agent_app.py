import streamlit as st
import google.generativeai as genai
import json
import random
import re

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

def extract_genres(genre_match):
    if genre_match and genre_match.group(1):
        return [g.strip() for g in genre_match.group(1).split("/") if g.strip()]
    return []

# --- Step 1: Define World ---
st.subheader("1. Define Your Sekai World")
AVAILABLE_GENRES = ["Fantasy", "Romance", "Mystery", "Sci-fi", "Horror"]

col1, col2 = st.columns([3, 1])
with col1:
    world_idea = st.text_input("Describe your world idea (or leave blank to write manually)", "Midnight Library")

    # Initialize genre in session state if it doesn't exist
    if "world_genre" not in st.session_state:
        st.session_state["world_genre"] = ["Fantasy"]

    if st.button("🤖 AI: Suggest World & Character", key="suggest_world_btn"):
        with st.spinner("Generating suggestions..."):
            suggestion = generate_field(
                f"Let's craft a compelling concept around the '{world_idea}' idea.\n\n"
                "Please generate a structured Sekai concept with:\n\n"
                "**Title:** (a short and poetic title)\n"
                "**Genre:** (1-2 genres only, like Fantasy / Romance)\n"
                "**World Setting:** (2-3 sentence description)\n"
                "**Player Character Name:** (a human name)\n"
                "**Character Traits:** (1-2 short traits only)\n\n"
                "Respond in markdown format using ** for bolded labels."
            )
            title = re.search(r'\*\*Title:\*\*\s*(.*?)\n', suggestion)
            genre = re.search(r'\*\*Genre:\*\*\s*(.*?)\n', suggestion)
            setting = re.search(r'\*\*World Setting:\*\*\s*(.*?)\n', suggestion)
            name = re.search(r'\*\*Player Character Name:\*\*\s*(.*?)\n', suggestion)
            traits = re.search(r'\*\*Character Traits:\*\*\s*(.*?)$', suggestion, re.DOTALL)

            if title:
                st.session_state["world_title"] = title.group(1).strip()
            if setting:
                st.session_state["world_setting"] = setting.group(1).strip()
            if name:
                st.session_state["user_name"] = name.group(1).strip()
            if traits:
                st.session_state["user_traits"] = traits.group(1).strip()
            
            new_genres = extract_genres(genre)
            if new_genres:
                valid_genres = [g for g in new_genres if g in AVAILABLE_GENRES]
                if valid_genres:
                    st.session_state["world_genre"] = valid_genres
            
            st.rerun()

    selected_genres = st.multiselect("Genre(s)", AVAILABLE_GENRES, key="world_genre")

    world_title = st.text_input("Sekai Title", value=st.session_state.get("world_title", "Midnight Library"), key="world_title")
    world_setting = st.text_area("World Setting", value=st.session_state.get("world_setting", "A magical library that only appears at midnight, where books come alive."), height=120, key="world_setting")
    user_name = st.text_input("Your Character Name (You will be part of the story)", value=st.session_state.get("user_name", "Alex"), key="user_name")
    user_traits = st.text_area("Your Character Traits", value=st.session_state.get("user_traits", "Curious, brave, and a quick thinker"), height=100, key="user_traits")

# --- Step 2: Define Characters ---
st.subheader("2. Create Main Characters")
num_characters = st.slider("Number of Characters", 1, 5, 2)
characters = []

if st.button("✨ Generate All Characters"):
    with st.spinner(f"Generating {num_characters} characters..."):
        player_name = st.session_state.get("user_name", "")
        prompt = (
            f"Generate {num_characters} completely unique and different characters for the world: {world_setting}.\n"
            f"The player's character is named '{player_name}'. Do not use this name for any of the generated characters.\n"
            f"Ensure the names, personalities, and abilities are distinct from each other and from the player.\n"
            f"Please provide {num_characters} character descriptions separated by '---'.\n\n"
            "Each character description must follow this format:\n"
            "Name: <A standard first name and optional last name only, no titles or descriptions>\n"
            "Role: <Character Role>\n"
            "Traits: <Personality traits and special abilities>"
        )
        response_text = generate_field(prompt)
        generated_characters = response_text.strip().split("\n---\n")

        for i in range(num_characters):
            if i < len(generated_characters):
                st.session_state[f"char_{i}"] = generated_characters[i].strip()
            else:
                st.session_state[f"char_{i}"] = ""

for i in range(num_characters):
    with st.expander(f"Character {i+1}"):
        idea = st.text_input(f"Character Idea {i+1}", key=f"idea_{i}")
        if st.button(f"🧠 AI: Generate Character {i+1}", key=f"gen_{i}"):
            player_name = st.session_state.get("user_name", "")
            other_chars = [st.session_state.get(f"char_{j}", "") for j in range(num_characters) if j != i]
            prompt = (
                f"Create a new character for the following world: {world_setting}. "
                f"The player's character is named '{player_name}'. Do not use this name.\n"
                f"Ensure this character is clearly different from the player and any existing characters:\n"
                + "\n".join(other_chars) +
                "\n\nRespond in this format:\n"
                "Name: <A standard first name and optional last name only, no titles or descriptions>\n"
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
Genre: {', '.join(selected_genres)}
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
if st.button("🎮 Start Game"):
    story_prompt = f"""
You are an interactive fiction narrator for a visual novel.
Begin the story using the following JSON world structure.
Write the story in the following script format:

narrator "<scene description>"
character (expression) "<dialogue or thoughts>"

Rules:
- Use narrator and character lines as shown.
- Focus on character dialogue and internal thoughts.
- Avoid long narration.
- You must introduce all main characters from the JSON within the first 3 story turns.
- Do NOT offer multiple choice options or suggestions.
- End with: **\"What do you do?\"**

JSON:
{json.dumps(st.session_state['sekai_json'], indent=2)}

Write the opening scene below, making sure to introduce one or more characters:
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

        # Format each line on a new line with spacing
        formatted_block = ""
        for line in block.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Use regex to find speaker and dialogue
            match = re.match(r'^(.*?)\s*(".*")', line, re.DOTALL)
            if match:
                speaker = match.group(1).strip()
                dialogue = match.group(2)  # Keep original with quotes for characters

                if speaker.lower() == "narrator":
                    # For narrator, remove quotes and italicize the content
                    dialogue_content = dialogue.strip()
                    if dialogue_content.startswith('"') and dialogue_content.endswith(
                        '"'
                    ):
                        dialogue_content = dialogue_content[1:-1]
                    formatted_line = f"<i>{dialogue_content}</i>"
                else:
                    # For characters, bold the speaker and show the dialogue
                    formatted_line = f"<b>{speaker}</b> {dialogue}"

                formatted_block += f"<p style='margin:4px 0;'>{formatted_line}</p>"
            else:
                # Handle lines without a speaker, like "**What do you do?**"
                formatted_block += f"<p style='margin:4px 0;'>{line}</p>"

        st.markdown(
            f'<div style="background-color:{color}; padding:10px; border-radius:8px">{user_reply_html}{formatted_block}</div>',
            unsafe_allow_html=True,
        )

def handle_send():
    user_input = st.session_state.get("reply_input", "")
    if user_input.strip():
        last_turn = st.session_state["game_state"][-1]

        introduction_instruction = ""
        # Ensure all characters are introduced within the first 3 turns
        if len(st.session_state["game_state"]) < 3:
            full_story_text = "".join(st.session_state["game_state"])
            all_characters_in_json = st.session_state["sekai_json"].get(
                "characters", []
            )
            character_names = [
                c.get("name") for c in all_characters_in_json if c.get("name")
            ]
            unintroduced_characters = [
                name
                for name in character_names
                if name.lower() not in full_story_text.lower()
            ]
            if unintroduced_characters:
                char_list = ", ".join(unintroduced_characters)
                introduction_instruction = f"IMPORTANT: In this turn, you must introduce the following character(s): {char_list}. "

        player_name = st.session_state.get("user_name", "the player")
        reply_prompt = (
            f"You are an interactive fiction narrator. The player character is {player_name}.\n"
            f"The player's input (action or dialogue) is: '{user_input}'.\n"
            f"Your role is to describe what happens next. Narrate the scene and have other non-player characters react.\n"
            f"IMPORTANT: Do NOT write dialogue or thoughts for the player character, {player_name}. Their input is already given.\n"
            f"{introduction_instruction}"
            f"Continue the story in script format. Keep narration brief. Do not give choices."
        )
        new_turn = model.generate_content(
            last_turn + "\n\n" + reply_prompt
        ).text.strip()
        st.session_state["game_state"].append(new_turn)
        st.session_state["user_inputs"].append(user_input.strip())

        # Clear the input box for the next turn
        st.session_state.reply_input = ""

        existing_colors = st.session_state.get("story_colors", [])
        available_colors = [
            c
            for c in ["#fce4ec", "#e3f2fd", "#e8f5e9", "#fff8e1", "#ede7f6"]
            if c != existing_colors[-1]
        ]
        new_color = random.choice(available_colors)
        st.session_state["story_colors"].append(new_color)
        # st.rerun is implicit with on_click callback

st.text_input("Enter your next action or dialogue", key="reply_input")
st.button("🔄 Send", on_click=handle_send)

# Footer
st.caption("Built by Claire Wang for the Sekai PM Take-Home Project ✨")

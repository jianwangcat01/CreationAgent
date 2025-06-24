import streamlit as st
import google.generativeai as genai
import json
import random
import re

# --- Mode Selection ---
if "app_mode" not in st.session_state:
    st.session_state["app_mode"] = None

# --- Menu Page ---
if st.session_state["app_mode"] is None:
    st.set_page_config(page_title="Sekai Creation Agent", layout="wide")
    st.title("Sekai AI Creation Agent")
    st.subheader("Choose a mode to get started:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            '''
            <a href="https://postimg.cc/YGrdLrpn" target="_blank">
                <img src="https://i.postimg.cc/j5Nm92Bb/1.png" alt="1" width="250" height="240"/>
            </a>
            ''',
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            '''
            <a href="https://postimages.org/" target="_blank">
                <img src="https://i.postimg.cc/nrJgtZtQ/2.png" alt="2" width="380" height="240"/>
            </a>
            ''',
            unsafe_allow_html=True
        )
    
    # Create another row for buttons to ensure they're aligned
    col1_btn, col2_btn = st.columns(2)
    
    with col1_btn:
        if st.button("Character Creation", key="char_mode_btn", use_container_width=True):
            st.session_state["app_mode"] = "character"
            st.rerun()
    
    with col2_btn:
        if st.button("Roleplay Creation", key="roleplay_mode_btn", use_container_width=True):
            st.session_state["app_mode"] = "roleplay"
            st.rerun()
    
    st.stop()

# --- Character Creation Mode ---
if st.session_state["app_mode"] == "character":
    st.set_page_config(page_title="Create Your Character", layout="wide")
    st.title("🎭 Create Your Character")
    st.markdown("""
Design a unique character, then chat with them as if they were real!
The AI will take on the personality you describe and respond accordingly.
""")

    if st.button("⬅️ Go Back to Menu", key="back_to_menu_char"):
        st.session_state["app_mode"] = None
        st.rerun()

    # Initialize session state for character creation
    if "char_creation_step" not in st.session_state:
        st.session_state["char_creation_step"] = 1
    if "char_feedback" not in st.session_state:
        st.session_state["char_feedback"] = {}

    # Progress indicator
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        step1_active = "🟢" if st.session_state["char_creation_step"] >= 1 else "⚪"
        if st.button(f"{step1_active} **Step 1: Core Details**", key="char_step1_btn", use_container_width=True):
            st.session_state["char_creation_step"] = 1
            st.rerun()
    with col2:
        step2_active = "🟢" if st.session_state["char_creation_step"] >= 2 else "⚪"
        if st.button(f"{step2_active} **Step 2: Personality**", key="char_step2_btn", use_container_width=True):
            st.session_state["char_creation_step"] = 2
            st.rerun()
    with col3:
        step3_active = "🟢" if st.session_state["char_creation_step"] >= 3 else "⚪"
        if st.button(f"{step3_active} **Step 3: Final Touches**", key="char_step3_btn", use_container_width=True):
            st.session_state["char_creation_step"] = 3
            st.rerun()
    st.markdown("---")

    # Clear button
    if st.button("🗑️ Clear All & Start Over", type="secondary", use_container_width=True):
        # Clear all character creation related session state
        keys_to_clear = [
            "char_creation_step", "char_feedback", "char_name_input", "char_role_input",
            "char_traits_input", "voice_style_input", "emotional_style_input", "lore_snippets_input",
            "opening_line_input", "char_image_upload", "chat_started", "chat_history",
            "character_prompt", "random_name_clicked", "random_role_clicked", "random_traits_clicked",
            "random_voice_clicked", "random_emotional_clicked", "random_lore_clicked", "random_opening_clicked"
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    # Helper function for random examples
    def get_random_example(field_type):
        examples = {
            "name": ["Eliora", "Jack the Brave", "Neko-chan", "Luna", "Kai", "Aria"],
            "role": ["Your loyal knight", "The mischievous demon you summoned", "Your online girlfriend who only lives in a phone", "Time-traveling librarian", "Guardian spirit", "Space pirate captain"],
            "traits": [
                "She's soft-spoken but bold when protecting loved ones. She speaks like an ancient priestess.",
                "He's sarcastic, flirty, and never serious — until someone mentions his tragic past.",
                "They adore shiny things and always try to trade useless junk with people.",
                "Calm, mysterious, and always speaks in riddles. Has knowledge of the past and future.",
                "Energetic and optimistic, but secretly carries deep emotional scars from their past.",
                "Wise and patient mentor figure who loves sharing stories and giving advice."
            ],
            "opening": [
                "Hey, it's you again! I've been waiting forever, dummy!",
                "Ah... another traveler. Come to disturb my peace?",
                "Greetings, brave soul! What brings you to my humble abode?",
                "Oh! You're finally here! I was starting to think you'd forgotten about me!",
                "Welcome, wanderer. I sense great potential within you..."
            ],
            "voice_style": [
                "Always says 'nya~' like a cat girl",
                "Ends every sentence with 'my dear'",
                "Speaks in old English ('Thou art brave indeed!')",
                "Uses lots of exclamation marks and is very energetic",
                "Speaks very formally and uses big words",
                "Has a habit of repeating the last word of sentences"
            ],
            "emotional_style": [
                "Protective big brother energy",
                "Tsundere (hot and cold flirty)",
                "Obsessive yandere",
                "Gentle supportive best friend",
                "Mysterious and aloof but secretly caring",
                "Playful and teasing but deeply loyal"
            ],
            "lore_snippets": [
                "They once lost someone they loved, and still carry the necklace.",
                "You and the character used to play in the forest as kids.",
                "They have a mysterious scar that glows in the moonlight.",
                "The character saved your life once, but you don't remember it.",
                "They're actually from another dimension and miss their home.",
                "You both share a secret that no one else knows about."
            ]
        }
        return random.choice(examples.get(field_type, ["Example"]))

    # Step 1: Core Details
    if st.session_state["char_creation_step"] == 1:
        st.subheader("🌟 Step 1: Core Details")
        st.info("Let's start with the basics! Tell us about your character's identity.")

        # Character Name
        st.markdown("### 👤 Character Name")
        col1, col2 = st.columns([3, 1])
        with col1:
            # Get random name if button was clicked
            if "random_name_clicked" not in st.session_state:
                st.session_state["random_name_clicked"] = False
            
            # Set default value based on random click or existing session state
            default_name = st.session_state.get("char_name_input", "")
            if st.session_state["random_name_clicked"]:
                default_name = get_random_example("name")
                st.session_state["char_name_input"] = default_name
                st.session_state["random_name_clicked"] = False
            
            char_name = st.text_input(
                "What's their name?",
                value=default_name,
                placeholder="Eliora / Jack the Brave / Neko-chan",
                key="char_name_input"
            )
        with col2:
            if st.button("🎲 Random", key="random_name"):
                st.session_state["random_name_clicked"] = True
                st.rerun()
        
        if char_name.strip():
            st.success(f"✨ That name is full of charm! Can't wait to meet {char_name}!")

        # Role/Occupation
        st.markdown("### 🎭 Role / Occupation")
        col1, col2 = st.columns([3, 1])
        with col1:
            # Get random role if button was clicked
            if "random_role_clicked" not in st.session_state:
                st.session_state["random_role_clicked"] = False
            
            # Set default value based on random click or existing session state
            default_role = st.session_state.get("char_role_input", "")
            if st.session_state["random_role_clicked"]:
                default_role = get_random_example("role")
                st.session_state["char_role_input"] = default_role
                st.session_state["random_role_clicked"] = False
            
            char_role = st.text_input(
                "What do they do? What's their role?",
                value=default_role,
                placeholder="Your loyal knight / Time-traveling librarian / Guardian spirit",
                key="char_role_input"
            )
        with col2:
            if st.button("🎲 Random", key="random_role"):
                st.session_state["random_role_clicked"] = True
                st.rerun()
        
        if char_role.strip():
            st.success("🎉 Ooooh! That's an exciting role — this is gonna be fun!")

        # Navigation
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Back to Menu"):
                st.session_state["app_mode"] = None
                st.rerun()
        with col2:
            if char_name.strip() and char_role.strip():
                if st.button("➡️ Next: Personality", type="primary"):
                    st.session_state["char_creation_step"] = 2
                    st.rerun()
            else:
                st.button("➡️ Next: Personality", disabled=True)

    # Step 2: Personality
    elif st.session_state["char_creation_step"] == 2:
        st.subheader("🧠 Step 2: Personality & Background")
        st.info("This is where the magic happens! Tell us how they behave, think, speak, and feel.")

        # Get values from previous step
        char_name = st.session_state.get("char_name_input", "Luna")
        char_role = st.session_state.get("char_role_input", "Time-traveling librarian")

        # Personality Traits
        st.markdown("### 💫 Personality Traits & Background")
        col1, col2 = st.columns([3, 1])
        with col1:
            # Get random traits if button was clicked
            if "random_traits_clicked" not in st.session_state:
                st.session_state["random_traits_clicked"] = False
            
            # Set default value based on random click or existing session state
            default_traits = st.session_state.get("char_traits_input", "")
            if st.session_state["random_traits_clicked"]:
                default_traits = get_random_example("traits")
                st.session_state["char_traits_input"] = default_traits
                st.session_state["random_traits_clicked"] = False
            
            char_traits = st.text_area(
                "Tell us about their personality, background, and how they behave:",
                value=default_traits,
                placeholder="She's soft-spoken but bold when protecting loved ones. She speaks like an ancient priestess.",
                height=120,
                key="char_traits_input"
            )
        with col2:
            if st.button("🎲 Random", key="random_traits"):
                st.session_state["random_traits_clicked"] = True
                st.rerun()

        if char_traits.strip():
            st.success("🎨 Wow, that's such a vivid personality. You're a worldbuilder already!")

        # Advanced Options (Collapsible)
        with st.expander("🌟 Advanced Options (Optional)", expanded=False):
            st.markdown("#### 🗣️ Voice Style / Speech Quirks")
            col1, col2 = st.columns([3, 1])
            with col1:
                # Get random voice style if button was clicked
                if "random_voice_clicked" not in st.session_state:
                    st.session_state["random_voice_clicked"] = False
                
                # Set default value based on random click or existing session state
                default_voice = st.session_state.get("voice_style_input", "")
                if st.session_state["random_voice_clicked"]:
                    default_voice = get_random_example("voice_style")
                    st.session_state["voice_style_input"] = default_voice
                    st.session_state["random_voice_clicked"] = False
                
                voice_style = st.text_input(
                    "How do they speak? Any unique speech patterns?",
                    value=default_voice,
                    placeholder="Always says 'nya~' like a cat girl / Ends every sentence with 'my dear'",
                    key="voice_style_input"
                )
            with col2:
                if st.button("🎲 Random", key="random_voice"):
                    st.session_state["random_voice_clicked"] = True
                    st.rerun()
            
            st.markdown("#### 💕 Emotional Style / Relationship Style")
            col1, col2 = st.columns([3, 1])
            with col1:
                # Get random emotional style if button was clicked
                if "random_emotional_clicked" not in st.session_state:
                    st.session_state["random_emotional_clicked"] = False
                
                # Set default value based on random click or existing session state
                default_emotional = st.session_state.get("emotional_style_input", "")
                if st.session_state["random_emotional_clicked"]:
                    default_emotional = get_random_example("emotional_style")
                    st.session_state["emotional_style_input"] = default_emotional
                    st.session_state["random_emotional_clicked"] = False
                
                emotional_style = st.text_input(
                    "How do they treat the user emotionally?",
                    value=default_emotional,
                    placeholder="Protective big brother energy / Tsundere (hot and cold flirty) / Gentle supportive best friend",
                    key="emotional_style_input"
                )
            with col2:
                if st.button("🎲 Random", key="random_emotional"):
                    st.session_state["random_emotional_clicked"] = True
                    st.rerun()
            
            st.markdown("#### 📖 Memory or Lore Snippets")
            col1, col2 = st.columns([3, 1])
            with col1:
                # Get random lore if button was clicked
                if "random_lore_clicked" not in st.session_state:
                    st.session_state["random_lore_clicked"] = False
                
                # Set default value based on random click or existing session state
                default_lore = st.session_state.get("lore_snippets_input", "")
                if st.session_state["random_lore_clicked"]:
                    default_lore = get_random_example("lore_snippets")
                    st.session_state["lore_snippets_input"] = default_lore
                    st.session_state["random_lore_clicked"] = False
                
                lore_snippets = st.text_area(
                    "Any personal backstory or shared memories?",
                    value=default_lore,
                    placeholder="They once lost someone they loved, and still carry the necklace. / You and the character used to play in the forest as kids.",
                    height=80,
                    key="lore_snippets_input"
                )
            with col2:
                if st.button("🎲 Random", key="random_lore"):
                    st.session_state["random_lore_clicked"] = True
                    st.rerun()

        # Navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Back"):
                st.session_state["char_creation_step"] = 1
                st.rerun()
        with col3:
            if char_traits.strip():
                if st.button("➡️ Next: Final Touches", type="primary"):
                    st.session_state["char_creation_step"] = 3
                    st.rerun()
            else:
                st.button("➡️ Next: Final Touches", disabled=True)

    # Step 3: Final Touches
    elif st.session_state["char_creation_step"] == 3:
        st.subheader("✨ Step 3: Final Touches")
        st.info("Almost done! Let's add those finishing touches to make your character perfect.")

        # Get values from previous steps
        char_name = st.session_state.get("char_name_input", "Luna")
        char_role = st.session_state.get("char_role_input", "Time-traveling librarian")
        char_traits = st.session_state.get("char_traits_input", "Luna is calm, mysterious, and always speaks in riddles.")

        # Opening Lines
        st.markdown("### 💬 Opening Lines (Optional)")
        st.markdown("**💡 Tip:** If you don't write anything here, I'll come up with something fun for you!")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            # Get random opening if button was clicked
            if "random_opening_clicked" not in st.session_state:
                st.session_state["random_opening_clicked"] = False
            
            # Set default value based on random click or existing session state
            default_opening = st.session_state.get("opening_line_input", "")
            if st.session_state["random_opening_clicked"]:
                default_opening = get_random_example("opening")
                st.session_state["opening_line_input"] = default_opening
                st.session_state["random_opening_clicked"] = False
            
            opening_line = st.text_area(
                "What should they say to start the conversation?",
                value=default_opening,
                placeholder="Hey, it's you again! I've been waiting forever, dummy!",
                height=80,
                key="opening_line_input"
            )
        with col2:
            if st.button("🎲 Random", key="random_opening"):
                st.session_state["random_opening_clicked"] = True
                st.rerun()

        if opening_line.strip():
            st.success("🎭 Got it! That's a perfect way to start the conversation!")

        # Character Image
        st.markdown("### 🖼️ Character Image (Optional)")
        st.markdown("**💡 Tip:** Try using AI image generators from Hugging Face like `cagliostrolab/animagine-xl` or `hakurei/waifu-diffusion`!")
        
        char_image = st.file_uploader(
            "Upload a profile image",
            type=["png", "jpg", "jpeg"],
            key="char_image_upload"
        )

        if char_image:
            st.success("🖼️ Beautiful image! It'll make the chat feel more immersive!")

        # Character Preview
        st.markdown("### 👀 Character Preview")
        preview_col1, preview_col2 = st.columns([1, 2])
        
        with preview_col1:
            if char_image:
                st.image(char_image, use_container_width=True, caption=f"{char_name}'s Avatar")
            else:
                # Default avatar placeholder
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 10px; color: white;">
                    <h3>🎭 {char_name}</h3>
                    <p>✨ Character Avatar</p>
                </div>
                """, unsafe_allow_html=True)

        with preview_col2:
            st.markdown(f"""
            **Name:** {char_name}
            **Role:** {char_role}
            **Personality:** {char_traits[:100]}{'...' if len(char_traits) > 100 else ''}
            """)

        # Navigation and Start Chat
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Back"):
                st.session_state["char_creation_step"] = 2
                st.rerun()
        with col3:
            if st.button("🔮 Start Chat with Character", type="primary"):
                # Start the chat
                st.session_state["chat_started"] = True
                st.session_state["chat_history"] = []
                
                # Build character prompt with advanced options
                voice_style = st.session_state.get("voice_style_input", "")
                emotional_style = st.session_state.get("emotional_style_input", "")
                lore_snippets = st.session_state.get("lore_snippets_input", "")
                
                character_prompt = f"You are roleplaying as a fictional character named {char_name}. "
                character_prompt += f"Your role is: {char_role}. Your personality and background: {char_traits}.\n\n"
                
                if voice_style:
                    character_prompt += f"Speech style: {voice_style}\n"
                if emotional_style:
                    character_prompt += f"Emotional style: {emotional_style}\n"
                if lore_snippets:
                    character_prompt += f"Background lore: {lore_snippets}\n"
                
                character_prompt += "\nSpeak naturally as this character would. Stay in character and never say you're an AI.\n"
                character_prompt += "Keep your replies concise (under 100 words) unless the user asks for a long story or detailed answer.\n"
                character_prompt += "Start the conversation by introducing yourself."
                
                st.session_state["character_prompt"] = character_prompt
                
                # Generate opening line if user didn't provide one
                if not opening_line.strip():
                    # Configure Gemini API for generating opening line
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")
                    
                    opening_prompt = f"""
Generate an engaging opening line for a character in a chat conversation.

Character Name: {char_name}
Role/Occupation: {char_role}
Personality/Background: {char_traits}
Voice Style: {voice_style}
Emotional Style: {emotional_style}
Lore: {lore_snippets}

The opening line should:
- Be in character and reflect their personality
- Be welcoming and engaging
- Be 1-2 sentences maximum
- Feel natural and conversational
- Not mention being an AI or fictional character
- Incorporate their voice style if specified

Generate only the opening line, nothing else.
"""
                    try:
                        response = model.generate_content(opening_prompt)
                        generated_opening = response.text.strip()
                        # Clean up any extra formatting
                        if generated_opening.startswith('"') and generated_opening.endswith('"'):
                            generated_opening = generated_opening[1:-1]
                        opening_line = generated_opening
                    except Exception as e:
                        # Fallback to a simple greeting if generation fails
                        opening_line = f"Hello! I'm {char_name}."
                
                # Add the opening line as the first message from the character
                st.session_state["chat_history"].append({
                    "user": "",
                    "bot": opening_line.strip()
                })
                
                st.rerun()

    # --- Chat UI (after Start) ---
    if st.session_state.get("chat_started"):
        st.markdown("---")
        st.subheader(f"🗨️ Chat with {st.session_state.get('char_name_input', 'Your Character')}")
        
        # Character info display
        char_name = st.session_state.get("char_name_input", "Luna")
        char_image = st.session_state.get("char_image_upload")
        
        if char_image:
            st.image(char_image, use_container_width=False, width=200, caption=f"{char_name}'s Avatar")
        
        # Chat history
        for i, entry in enumerate(st.session_state["chat_history"]):
            if entry['user']:
                st.markdown(f"**You:** {entry['user']}")
            # Remove double character name if present
            bot_reply = entry['bot']
            prefix = f"{char_name}:"
            if bot_reply.strip().lower().startswith(prefix.lower()):
                bot_reply = bot_reply.strip()[len(prefix):].lstrip()
            st.markdown(f"**{char_name}:** {bot_reply}")
        
        # Chat input
        user_input = st.text_input("Your Message", key="char_chat_input")
        if st.button("📩 Send"):
            model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")
            full_prompt = st.session_state["character_prompt"] + "\n\n"
            for entry in st.session_state["chat_history"]:
                if entry['user']:
                    full_prompt += f"You: {entry['user']}\n{char_name}: {entry['bot']}\n"
                else:
                    full_prompt += f"{char_name}: {entry['bot']}\n"
            full_prompt += f"You: {user_input}\n{char_name}:"
            response = model.generate_content(full_prompt)
            reply = response.text.strip()
            # Remove double character name if present in reply before saving
            prefix = f"{char_name}:"
            if reply.lower().startswith(prefix.lower()):
                reply = reply[len(prefix):].lstrip()
            st.session_state["chat_history"].append({
                "user": user_input,
                "bot": reply
            })
            st.rerun()
        
        # Back to character creation
        if st.button("🔄 Create New Character"):
            st.session_state["chat_started"] = False
            st.session_state["char_creation_step"] = 1
            st.rerun()
    
    st.stop()

# --- Roleplay Creation Mode ---
if st.session_state["app_mode"] == "roleplay":
    st.set_page_config(page_title="Create Your Sekai World", layout="wide")
    st.title("🌍 Create Your Sekai World")
    st.markdown("""
Welcome to the magical world of Sekai creation! Let's build something amazing together, step by step. ✨
""")

    if st.button("⬅️ Go Back to Menu", key="back_to_menu_roleplay"):
        st.session_state["app_mode"] = None
        st.rerun()

    # Clear button at the top
    if st.button("🗑️ Clear All & Start Over", type="secondary", use_container_width=True):
        # Clear all roleplay creation related session state
        keys_to_clear = [
            "roleplay_step", "roleplay_feedback", "world_idea_input", "world_title", "world_setting",
            "world_title_input", "world_setting_input", "world_keywords_input", "world_genre",
            "user_name", "user_traits", "user_name_input", "user_traits_input", "num_characters_slider",
            "sekai_json", "game_state", "story_colors", "user_inputs", "story_tone", "pacing", "pov", "narration_style"
        ]
        # Clear character-specific keys (up to 5 characters)
        for i in range(5):
            keys_to_clear.extend([
                f"char_{i}", f"idea_{i}", f"name_{i}", f"role_{i}", f"trait_{i}",
                f"voice_style_{i}", f"opening_line_{i}", f"gen_{i}"
            ])
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

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

    def handle_choice_click(choice_text):
        st.session_state.reply_input = choice_text
        handle_send()

    def generate_choices():
        """Generate 3 choice options for the player"""
        if "game_state" in st.session_state and st.session_state["game_state"]:
            last_turn = st.session_state["game_state"][-1]
            player_name = st.session_state.get("user_name", "the player")
            
            choice_prompt = f"""
Based on the current story situation, generate 3 different action choices for {player_name}.

Current story context:
{last_turn}

Generate 3 distinct choices that would make sense for the player character in this situation. 
Each choice should be:
- 1-2 sentences maximum
- Specific and actionable
- Different from each other
- Appropriate for the story context

Format as:
1. [First choice]
2. [Second choice] 
3. [Third choice]

Generate only the 3 choices, nothing else.
"""
            
            try:
                response = model.generate_content(choice_prompt)
                choices_text = response.text.strip()
                
                # Parse the choices
                choices = []
                lines = choices_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                        choice = line.split('.', 1)[1].strip()
                        if choice:
                            choices.append(choice)
                
                # Ensure we have exactly 3 choices
                while len(choices) < 3:
                    choices.append(f"Continue exploring the area")
                if len(choices) > 3:
                    choices = choices[:3]
                
                return choices
            except Exception as e:
                # Fallback choices
                return [
                    "Continue exploring the area",
                    "Talk to someone nearby", 
                    "Investigate something interesting"
                ]
        return [
            "Continue exploring the area",
            "Talk to someone nearby", 
            "Investigate something interesting"
        ]

    # --- Quick Navigation Links ---
    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("🌍 Step 1: World", key="nav_step1", use_container_width=True):
            st.markdown("""
            <script>
            document.querySelector('[data-testid="stMarkdown"]').scrollIntoView();
            </script>
            """, unsafe_allow_html=True)
    with col2:
        if st.button("👤 Step 2: You", key="nav_step2", use_container_width=True):
            st.markdown("""
            <script>
            document.querySelector('[data-testid="stMarkdown"]').scrollIntoView();
            </script>
            """, unsafe_allow_html=True)
    with col3:
        if st.button("👥 Step 3: Characters", key="nav_step3", use_container_width=True):
            st.markdown("""
            <script>
            document.querySelector('[data-testid="stMarkdown"]').scrollIntoView();
            </script>
            """, unsafe_allow_html=True)
    with col4:
        if st.button("📜 Step 4: Template", key="nav_step4", use_container_width=True):
            st.markdown("""
            <script>
            document.querySelector('[data-testid="stMarkdown"]').scrollIntoView();
            </script>
            """, unsafe_allow_html=True)
    with col5:
        if st.button("🎮 Step 5: Play", key="nav_step5", use_container_width=True):
            st.markdown("""
            <script>
            document.querySelector('[data-testid="stMarkdown"]').scrollIntoView();
            </script>
            """, unsafe_allow_html=True)
    st.markdown("---")

    # ===== STEP 1: CREATE YOUR SEKAI WORLD =====
    st.markdown("## 🌍 Step 1: Create Your Sekai World")
    st.markdown('<div id="step-1"></div>', unsafe_allow_html=True)
    st.info("Let's start with your spark of inspiration! Don't overthink it — just share a mood, a moment, or a single word! We'll turn it into magic together 💫")

    # --- World Spark (Seed Idea) ---
    if 'world_idea_input' not in st.session_state:
        st.session_state['world_idea_input'] = ''
    if 'world_idea_input_temp' not in st.session_state:
        st.session_state['world_idea_input_temp'] = ''
    def update_world_idea():
        st.session_state['world_idea_input'] = st.session_state['world_idea_input_temp']
    world_idea = st.text_input(
        "Your world spark",
        value=st.session_state['world_idea_input_temp'],
        placeholder="A city where dreams are currency / Cyberpunk witches at high school / Haunted aquarium / Post-apocalyptic tea shop",
        key="world_idea_input_temp",
        on_change=update_world_idea
    )
    if world_idea.strip():
        st.success("✨ Ooooh, that sounds fascinating. Let's shape it into something special!")

    # --- Genre Picker ---
    genre_options = ["Fantasy 🧝‍♀️", "Sci-Fi 🚀", "Romance 💘", "Slice of Life 🍰", "Mystery 🔍", "Horror 👻", "Comedy 😂", "Action ⚔️", "Historical 🏯"]
    if 'world_genre' not in st.session_state:
        st.session_state['world_genre'] = []
    if 'world_genre_temp' not in st.session_state:
        st.session_state['world_genre_temp'] = []
    def update_genres():
        st.session_state['world_genre'] = st.session_state['world_genre_temp']
    selected_genres = st.multiselect(
        "Your Sekai's Genre(s)",
        genre_options,
        default=st.session_state['world_genre_temp'],
        key="world_genre_temp",
        on_change=update_genres
    )
    
    if selected_genres:
        st.success(f"🌟 Awesome! Your world will have a {', '.join(selected_genres)} vibe!")

    # --- AI World Generation Button ---
    def strip_stars(s):
        return s.strip().strip('*').strip()
    if st.button("✨ AI: Turn My Idea into a World", type="primary"):
        st.toast("Working magic... Generating your Sekai world ✨")
        # Compose the prompt based on available fields
        idea = st.session_state['world_idea_input_temp'].strip()
        genres = st.session_state['world_genre_temp']
        genre_str = ', '.join([g.split(' ', 1)[0] for g in genres]) if genres else ''
        if idea and genre_str:
            prompt = f"Generate a creative Sekai world concept based on the following idea and genres.\n\nIdea: {idea}\nGenres: {genre_str}\n\nRespond with:\n- Sekai Title\n- World Setting (2-3 vivid sentences)\n- Keywords (comma separated, 3-6 words)"
        elif idea:
            prompt = f"Generate a creative Sekai world concept based on the following idea.\n\nIdea: {idea}\n\nRespond with:\n- Sekai Title\n- World Setting (2-3 vivid sentences)\n- Keywords (comma separated, 3-6 words)"
        elif genre_str:
            prompt = f"Generate a creative Sekai world concept based on the following genres.\n\nGenres: {genre_str}\n\nRespond with:\n- Sekai Title\n- World Setting (2-3 vivid sentences)\n- Keywords (comma separated, 3-6 words)"
        else:
            prompt = "Generate a random creative Sekai world concept.\n\nRespond with:\n- Sekai Title\n- World Setting (2-3 vivid sentences)\n- Keywords (comma separated, 3-6 words)"
        suggestion = generate_field(prompt)
        # Parse the response
        title = re.search(r'[Tt]itle\s*[:：\-]\s*(.*)', suggestion)
        setting = re.search(r'[Ww]orld [Ss]etting\s*[:：\-]\s*(.*)', suggestion)
        keywords = re.search(r'[Kk]eywords?\s*[:：\-]\s*(.*)', suggestion)
        # Fallback: try to split lines if not matched
        if not title or not setting or not keywords:
            lines = [l.strip() for l in suggestion.split('\n') if l.strip()]
            if len(lines) >= 3:
                if not title:
                    title = re.match(r'^(.*)$', lines[0])
                if not setting:
                    setting = re.match(r'^(.*)$', lines[1])
                if not keywords:
                    keywords = re.match(r'^(.*)$', lines[2])
        # Fill session state, stripping stars
        if title:
            clean_title = strip_stars(title.group(1))
            st.session_state["world_title"] = clean_title
            st.session_state["world_title_temp"] = clean_title
        if setting:
            clean_setting = strip_stars(setting.group(1))
            st.session_state["world_setting"] = clean_setting
            st.session_state["world_setting_temp"] = clean_setting
        if keywords:
            clean_keywords = strip_stars(keywords.group(1))
            st.session_state["world_keywords_input"] = clean_keywords
            st.session_state["world_keywords_input_temp"] = clean_keywords
        st.rerun()

    # --- Title + Setting Description ---
    if 'world_title' not in st.session_state:
        st.session_state['world_title'] = ''
    if 'world_title_temp' not in st.session_state:
        st.session_state['world_title_temp'] = ''
    def update_world_title():
        st.session_state['world_title'] = st.session_state['world_title']
    world_title = st.text_input(
        "Sekai Title",
        value=st.session_state['world_title'],
        key="world_title",
        on_change=update_world_title
    )
    if 'world_setting' not in st.session_state:
        st.session_state['world_setting'] = ''
    if 'world_setting_temp' not in st.session_state:
        st.session_state['world_setting_temp'] = ''
    def update_world_setting():
        st.session_state['world_setting'] = st.session_state['world_setting']
    world_setting = st.text_area(
        "Describe the World Setting",
        value=st.session_state['world_setting'],
        key="world_setting",
        on_change=update_world_setting
    )
    if world_setting.strip():
        st.success("📝 This already feels so vivid! We're almost ready to meet your characters…")

    # --- World Keywords/Tags (optional) ---
    if 'world_keywords_input' not in st.session_state:
        st.session_state['world_keywords_input'] = ''
    if 'world_keywords_input_temp' not in st.session_state:
        st.session_state['world_keywords_input_temp'] = ''
    def update_keywords():
        st.session_state['world_keywords_input'] = st.session_state['world_keywords_input']
    world_keywords = st.text_input(
        "Keywords",
        value=st.session_state['world_keywords_input'],
        key="world_keywords_input",
        on_change=update_keywords
    )

    st.markdown("---")

    # ===== STEP 2: CREATE YOUR CHARACTER (YOU IN THE WORLD) =====
    st.markdown("## 👤 Step 2: Create Your Character")
    st.markdown('<div id="step-2"></div>', unsafe_allow_html=True)
    st.info("Now let's meet you! You'll be the heart of this world, so tell us about yourself.")

    # --- AI Character Generation Button ---
    if st.button("✨ AI: Generate My Character", key="ai_generate_player_char", type="primary"):
        # Get complete world information from Step 1
        world_title = st.session_state.get('world_title_temp') or st.session_state.get('world_title', '')
        world_setting = st.session_state.get('world_setting_temp') or st.session_state.get('world_setting', '')
        world_keywords = st.session_state.get('world_keywords_input_temp') or st.session_state.get('world_keywords_input', '')
        world_genres = st.session_state.get('world_genre_temp') or st.session_state.get('world_genre', [])
        
        if not (world_title and world_setting):
            st.warning("Please complete Step 1 (Sekai World) before generating your character.")
        else:
            # Build a comprehensive prompt with all available world information
            genre_str = ', '.join([g.split(' ', 1)[0] for g in world_genres]) if world_genres else 'Fantasy'
            world_context = f"Title: {world_title}\nSetting: {world_setting}"
            if world_keywords:
                world_context += f"\nKeywords: {world_keywords}"
            world_context += f"\nGenre: {genre_str}"
            
            prompt = f"""Generate a player character for the following Sekai world.

{world_context}

Create a character that would fit naturally into this world and could be the protagonist of an interactive story. The character should have a compelling personality and abilities that make sense for this setting.

Respond with:
- Name (a human name)
- Traits (1-2 sentences about personality, quirks, or magical powers)"""
            
            suggestion = generate_field(prompt)
            # Parse the response
            name = re.search(r'[Nn]ame\s*[:：\-]\s*(.*)', suggestion)
            traits = re.search(r'[Tt]raits?\s*[:：\-]\s*(.*)', suggestion)
            # Fallback: try to split lines if not matched
            if not name or not traits:
                lines = [l.strip() for l in suggestion.split('\n') if l.strip()]
                if len(lines) >= 2:
                    if not name:
                        name = re.match(r'^(.*)$', lines[0])
                    if not traits:
                        traits = re.match(r'^(.*)$', lines[1])
            def strip_stars(s):
                return s.strip().strip('*').strip()
            valid = False
            if name and traits:
                clean_name = strip_stars(name.group(1))
                clean_traits = strip_stars(traits.group(1))
                if clean_name and clean_traits and not clean_name.lower().startswith("let's craft"):
                    st.session_state['user_name_input_temp'] = clean_name
                    st.session_state['user_traits_input_temp'] = clean_traits
                    valid = True
            if not valid:
                st.error("AI could not generate a valid character. Please check your world info in Step 1 and try again.")
            else:
                st.rerun()

    # --- Character Name ---
    if 'user_name_input' not in st.session_state:
        st.session_state['user_name_input'] = ''
    if 'user_name_input_temp' not in st.session_state:
        st.session_state['user_name_input_temp'] = ''
    def update_user_name():
        st.session_state['user_name_input'] = st.session_state['user_name_input_temp']
    user_name = st.text_input(
        "Your Character's Name",
        value=st.session_state['user_name_input_temp'],
        key="user_name_input_temp",
        on_change=update_user_name
    )

    # --- Character Traits ---
    if 'user_traits_input' not in st.session_state:
        st.session_state['user_traits_input'] = ''
    if 'user_traits_input_temp' not in st.session_state:
        st.session_state['user_traits_input_temp'] = ''
    def update_user_traits():
        st.session_state['user_traits_input'] = st.session_state['user_traits_input_temp']
    user_traits = st.text_area(
        "Your Character's Traits",
        value=st.session_state['user_traits_input_temp'],
        key="user_traits_input_temp",
        on_change=update_user_traits
    )
    
    if user_traits.strip():
        st.success("🌟 Perfect! You're going to be the heart of this world.")

    st.markdown("---")

    # ===== STEP 3: CREATE MAIN CHARACTERS =====
    st.markdown("## 👥 Step 3: Create Main Characters")
    st.markdown('<div id="step-3"></div>', unsafe_allow_html=True)
    st.info("Now let's meet the other characters who will join your story!")

    # Get values from previous steps
    world_title = st.session_state.get("world_title_temp", st.session_state.get("world_title", "Your Sekai World"))
    world_setting = st.session_state.get("world_setting_temp", st.session_state.get("world_setting", "A magical world"))
    world_keywords = st.session_state.get("world_keywords_input_temp", st.session_state.get("world_keywords_input", ""))
    world_genres = st.session_state.get("world_genre_temp") or st.session_state.get("world_genre", [])
    user_name = st.session_state.get("user_name", st.session_state.get("user_name_input", "Alex"))
    user_traits = st.session_state.get("user_traits", st.session_state.get("user_traits_input", "Curious and brave"))

    # Number of Characters
    st.markdown("### 🎭 How many characters will join your story?")
    st.markdown("Choose between 1 and 5 to start.")
    num_characters = st.slider("Number of Characters", 1, 5, 2, key="num_characters_slider")
    
    if num_characters > 1:
        st.success(f"🎉 Great! {num_characters} characters will make this story even more exciting!")

    # Generate All Characters Button
    if st.button("✨ AI: Generate All Characters", type="primary"):
        with st.spinner(f"Creating {num_characters} unique characters..."):
            # Build comprehensive world context
            genre_str = ', '.join([g.split(' ', 1)[0] for g in world_genres]) if world_genres else 'Fantasy'
            world_context = f"World: {world_setting}\nTitle: {world_title}\nGenre: {genre_str}"
            if world_keywords:
                world_context += f"\nKeywords: {world_keywords}"
            
            prompt = f"""Generate {num_characters} completely unique and different characters for the following world:

{world_context}

Player Character: {user_name} ({user_traits})

Create {num_characters} supporting characters that:
- Are distinct from each other and from the player character
- Would naturally exist in this world
- Have interesting personalities and abilities
- Could interact meaningfully with the player character
- Fit the genre and tone of the world

Please provide {num_characters} character descriptions separated by '---'.

Each character description must follow this format:
Name: <A standard first name and optional last name only, no titles or descriptions>
Role: <Character Role>
Traits: <Personality traits and special abilities>"""
            
            response_text = generate_field(prompt)
            generated_characters = response_text.strip().split("\n---\n")

            for i in range(num_characters):
                if i < len(generated_characters):
                    st.session_state[f"char_{i}"] = generated_characters[i].strip()
                else:
                    st.session_state[f"char_{i}"] = ""
            st.rerun()

    # Character Forms
    characters = []
    for i in range(num_characters):
        st.markdown(f"### Character {i+1}")
        
        # Character Idea
        if f"idea_{i}" not in st.session_state:
            st.session_state[f"idea_{i}"] = ""
        idea = st.text_input(
            f"Character Idea {i+1}",
            placeholder="Knight with amnesia who might be evil / Librarian who hides a secret / Rival time mage",
            key=f"idea_{i}"
        )
        
        # Generate Individual Character Button
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button(f"🧠 AI: Generate Character {i+1}", key=f"gen_{i}"):
                # Get complete world and user information
                world_genres = st.session_state.get("world_genre_temp") or st.session_state.get("world_genre", [])
                genre_str = ', '.join([g.split(' ', 1)[0] for g in world_genres]) if world_genres else 'Fantasy'
                world_context = f"World: {world_setting}\nTitle: {world_title}\nGenre: {genre_str}"
                if world_keywords:
                    world_context += f"\nKeywords: {world_keywords}"
                
                other_chars = [st.session_state.get(f"char_{j}", "") for j in range(num_characters) if j != i]
                existing_chars_text = "\n".join(other_chars) if other_chars else "None"
                
                prompt = f"""Create a new character for the following world:

{world_context}

Player Character: {user_name} ({user_traits})

Existing Characters:
{existing_chars_text}

Create a character that:
- Is clearly different from the player character and any existing characters
- Would naturally exist in this world
- Has an interesting personality and abilities
- Could interact meaningfully with the player character
- Fits the genre and tone of the world

Respond in this format:
Name: <A standard first name and optional last name only, no titles or descriptions>
Role: <Character Role>
Traits: <Personality traits and special abilities>"""
                
                result = generate_field(prompt)
                st.session_state[f"char_{i}"] = result
                st.rerun()
        
        # Parse generated character
        default_text = st.session_state.get(f"char_{i}", "")
        parsed_name, parsed_role, parsed_traits = "", "", ""
        if "Name:" in default_text and "Role:" in default_text and "Traits:" in default_text:
            try:
                parsed_name = default_text.split("Name:")[1].split("Role:")[0].strip()
                parsed_role = default_text.split("Role:")[1].split("Traits:")[0].strip()
                parsed_traits = default_text.split("Traits:")[1].strip()
            except Exception:
                parsed_name, parsed_role, parsed_traits = "", "", ""

        # Character Details
        name = st.text_input(f"Name {i+1}", key=f"name_{i}", value=parsed_name)
        role = st.text_input(f"Role {i+1}", key=f"role_{i}", value=parsed_role, placeholder="Librarian who hides a secret / Rival time mage")
        trait = st.text_area(f"Key Traits {i+1}", key=f"trait_{i}", value=parsed_traits, height=100, placeholder="Describe their personality, abilities, and backstory...")
        
        # Optional Add-ons
        with st.expander(f"🌟 Optional Add-ons for Character {i+1}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                voice_style = st.selectbox(
                    f"Voice Style",
                    ["Default", "Cute", "Serious", "Snarky", "Mysterious", "Energetic", "Calm"],
                    key=f"voice_style_{i}"
                )
            with col2:
                opening_line = st.text_input(
                    f"AI Opening Line (or leave blank to auto-gen)",
                    placeholder="What should they say when you first meet?",
                    key=f"opening_line_{i}"
                )
        
        characters.append({
            "name": name, 
            "role": role, 
            "traits": trait,
            "voice_style": voice_style if 'voice_style' in locals() else "Default",
            "opening_line": opening_line if 'opening_line' in locals() else ""
        })

    st.markdown("---")

    # ===== STEP 4: GENERATE SEKAI STORY TEMPLATE =====
    st.markdown("## 📜 Step 4: Generate Sekai Story Template")
    st.markdown('<div id="step-4"></div>', unsafe_allow_html=True)
    st.info("Let's bring everything together and create your story template!")

    # Opening Line Setup
    st.markdown("### 💬 Opening Scene Setup")
    st.markdown("**💡 Tip:** This will be the first scene of your story!")
    
    # Initialize session state for opening scene
    if "opening_scene_input" not in st.session_state:
        st.session_state["opening_scene_input"] = ""
    if "opening_scene_generated" not in st.session_state:
        st.session_state["opening_scene_generated"] = ""
    
    # If AI just generated a value, update the input and clear the flag
    if st.session_state["opening_scene_generated"]:
        st.session_state["opening_scene_input"] = st.session_state["opening_scene_generated"]
        st.session_state["opening_scene_generated"] = ""
    
    def update_opening_scene():
        st.session_state["opening_scene_input"] = st.session_state["opening_scene_input"]
    
    col1, col2 = st.columns([3, 1])
    with col1:
        # AI button is now above the text area
        if st.button("✨ AI: Generate Opening Scene", key="generate_opening_scene"):
            with st.spinner("Creating an engaging opening scene..."):
                char_list = f"Player: {user_name} ({user_traits})\n"
                for c in characters:
                    char_list += f"- {c['name']} ({c['role']}): {c['traits']}\n"
                prompt = f"""
Generate an engaging opening scene for an interactive story.

World Information:
- Title: {world_title}
- Setting: {world_setting}
- Keywords: {world_keywords}
- Genre: {', '.join(selected_genres) if selected_genres else 'Fantasy'}

Characters:
{char_list}

Create a vivid opening scene that:
- Introduces the world and setting
- Establishes the player character's situation
- Hints at the story to come
- Is 2-3 sentences maximum
- Feels immersive and engaging

Generate only the opening scene description, nothing else.
"""
                try:
                    response = model.generate_content(prompt)
                    generated_opening = response.text.strip()
                    if generated_opening.startswith('"') and generated_opening.endswith('"'):
                        generated_opening = generated_opening[1:-1]
                    st.session_state["opening_scene_generated"] = generated_opening
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to generate opening scene: {e}")
        opening_scene = st.text_area(
            "Describe the opening scene (optional - leave blank for AI generation)",
            value=st.session_state["opening_scene_input"],
            placeholder="You wake up in a mysterious library at midnight... / The city streets are filled with floating dreams...",
            height=100,
            key="opening_scene_input",
            on_change=update_opening_scene
        )

    if opening_scene.strip():
        st.success("🎭 Perfect! This opening scene will set the tone for your adventure!")

    # Advanced Settings (collapsed by default)
    with st.expander("🧙‍♂️ Advanced Settings (Optional)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            story_tone = st.selectbox(
                "Story Tone",
                ["Balanced", "Light", "Serious", "Romantic", "Chaotic", "Mysterious"],
                key="story_tone"
            )
            pacing = st.selectbox(
                "Pacing",
                ["Balanced", "Slow burn", "Fast plot twists", "Episodic"],
                key="pacing"
            )
        with col2:
            pov = st.selectbox(
                "Point of View",
                ["Third person", "First person", "Omniscient"],
                key="pov"
            )
            narration_style = st.selectbox(
                "Narration Style",
                ["Balanced", "Minimal (chat only)", "Vivid prose", "Light storytelling"],
                key="narration_style"
            )

    # Generate Template Button
    if st.button("🧙 Generate Template", type="primary"):
        with st.spinner("Talking to Gemini AI..."):
            # Debug: Show what values we're using
            st.info(f"Using world info: Title='{world_title}', Setting='{world_setting}', Keywords='{world_keywords}'")
            st.info(f"Using user character: Name='{user_name}', Traits='{user_traits}'")
            st.info(f"Using {len(characters)} characters from Step 3")
            
            # Build comprehensive character information including optional add-ons
            character_details = []
            for c in characters:
                if c['name'].strip() and c['traits'].strip():
                    char_info = f"- {c['name']} ({c['role']}): {c['traits']}"
                    if c.get('voice_style') and c['voice_style'] != "Default":
                        char_info += f" | Voice: {c['voice_style']}"
                    if c.get('opening_line'):
                        char_info += f" | Opening: {c['opening_line']}"
                    character_details.append(char_info)
            
            prompt = f"""
You are an AI for building JSON-based interactive stories.
Generate a story JSON with: title, setting, genre, keywords, characters (array of name, role, description, voice_style, opening_line), and openingScene.

Title: {world_title}
Setting: {world_setting}
Genre: {', '.join(selected_genres) if selected_genres else 'Fantasy'}
Keywords: {world_keywords}
Characters:
- {user_name} (Player): {user_traits}
"""
            for char_detail in character_details:
                prompt += f"{char_detail}\n"
            
            # Add opening scene if provided
            if opening_scene.strip():
                prompt += f"\nOpening Scene: {opening_scene}\n"
            
            # Add advanced settings to prompt
            if story_tone != "Balanced":
                prompt += f"\nTone: {story_tone}\n"
            if pacing != "Balanced":
                prompt += f"Pacing: {pacing}\n"
            if pov != "Third person":
                prompt += f"POV: {pov}\n"
            if narration_style != "Balanced":
                prompt += f"Narration: {narration_style}\n"
            
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
                st.success("🎉 Sekai story template generated successfully!")
                st.json(sekai_json)
            except json.JSONDecodeError:
                st.error("Failed to parse JSON. Please try again.")
                st.code(output)

    st.markdown("---")

    # ===== STEP 5: PLAY / START THE STORY =====
    st.markdown("## 🎮 Step 5: Start Your Sekai Journey!")
    st.markdown('<div id="step-5"></div>', unsafe_allow_html=True)
    
    # Get values
    user_name = st.session_state.get("user_name", st.session_state.get("user_name_input", "Alex"))
    world_title = st.session_state.get("world_title", st.session_state.get("world_title_temp", "Your Sekai World"))
    
    st.success(f"🎉 You're all set! Ready to begin your Sekai journey with {user_name} in {world_title}? Let's go!")
    
    st.markdown("""
📜 **How to play:**
- Type your character's **dialogue** normally: e.g., `What are you doing here?`
- Type your character's **actions** with asterisks: e.g., `*run away from the library*`
- The AI will narrate the story and have other characters respond!
    """)

    # Check if template is generated
    if "sekai_json" not in st.session_state:
        st.warning("⚠️ You need to generate a story template first!")
        st.markdown("""
**To start the game, you need to:**
1. Complete **Step 4: Generate Sekai Story Template** above
2. Click **"🧙 Generate Template"** to create your story
3. Then return here to start playing!
        """)
    else:
        if st.button("🎮 Start Game", type="primary"):
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
- End with: **"What do you do?"**

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
                st.rerun()

    # --- Game UI (only appears after game starts) ---
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

        # Game input (only appears when game is active)
        st.markdown("### 🎮 Your Turn")
        
        # Generate 3 choice options
        choices = generate_choices()
        
        # Display choice buttons
        st.markdown("**Choose an action or write your own:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(f"🎯 {choices[0][:30]}{'...' if len(choices[0]) > 30 else ''}", 
                        key=f"choice_1_{len(st.session_state['game_state'])}", 
                        on_click=handle_choice_click, args=(choices[0],)):
                pass
        
        with col2:
            if st.button(f"🎯 {choices[1][:30]}{'...' if len(choices[1]) > 30 else ''}", 
                        key=f"choice_2_{len(st.session_state['game_state'])}", 
                        on_click=handle_choice_click, args=(choices[1],)):
                pass
        
        with col3:
            if st.button(f"🎯 {choices[2][:30]}{'...' if len(choices[2]) > 30 else ''}", 
                        key=f"choice_3_{len(st.session_state['game_state'])}", 
                        on_click=handle_choice_click, args=(choices[2],)):
                pass
        
        # Show full choice text on hover (using tooltips)
        st.markdown(f"""
        <details>
        <summary>📋 View full choice descriptions</summary>
        <ul>
        <li><strong>Choice 1:</strong> {choices[0]}</li>
        <li><strong>Choice 2:</strong> {choices[1]}</li>
        <li><strong>Choice 3:</strong> {choices[2]}</li>
        </ul>
        </details>
        """, unsafe_allow_html=True)
        
        # Freeform input
        st.markdown("**Or write your own action/dialogue:**")
        st.text_input("Enter your next action or dialogue", key="reply_input")
        st.button("🔄 Send", on_click=handle_send)

    # Footer
    st.caption("Built by Claire Wang for the Sekai PM Take-Home Project ✨")

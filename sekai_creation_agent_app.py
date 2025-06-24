import streamlit as st
import google.generativeai as genai
import json
import random
import re

# Add custom CSS for animated feedback
st.markdown("""
<style>
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes sparkle {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

.feedback-animation {
    animation: fadeInUp 0.6s ease-out;
}

.emoji-sparkle {
    animation: sparkle 0.8s ease-in-out;
    display: inline-block;
}

.step-progress {
    text-align: center;
    font-weight: bold;
    color: #4CAF50;
}

.step-inactive {
    color: #ccc;
}
</style>
""", unsafe_allow_html=True)

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
            "sekai_json", "game_state", "story_colors", "user_inputs", "story_tone", "pacing", "pov", "narration_style",
            # New guided world creation variables (without step tracking)
            "world_inspiration", "world_environment", "world_mood", "world_magic"
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

    def strip_stars(s):
        return s.strip().strip('*').strip()

    def handle_send():
        user_input = st.session_state.get("reply_input", "")
        if user_input.strip():
            # Get the template context
            sekai_json = st.session_state.get("sekai_json", {})
            
            # Get advanced settings from the JSON template
            story_tone = sekai_json.get('storyTone', 'Balanced')
            pacing = sekai_json.get('pacing', 'Balanced')
            point_of_view = sekai_json.get('pointOfView', 'Third person')
            narration_style = sekai_json.get('narrationStyle', 'Balanced')
            
            # Build the full context including template and conversation history
            template_context = f"""
STORY TEMPLATE:
Title: {sekai_json.get('title', 'Unknown')}
Setting: {sekai_json.get('setting', 'Unknown')}
Genre: {sekai_json.get('genre', 'Fantasy')}
Keywords: {sekai_json.get('keywords', '')}

Story Style:
- Tone: {story_tone}
- Pacing: {pacing}
- Point of View: {point_of_view}
- Narration Style: {narration_style}

Characters:
"""
            # Add all characters from template
            for char in sekai_json.get('characters', []):
                char_name = char.get('name', 'Unknown')
                char_role = char.get('role', '')
                char_description = char.get('description', '')
                char_voice = char.get('voice_style', '')
                template_context += f"- {char_name} ({char_role}): {char_description}"
                if char_voice:
                    template_context += f" | Voice: {char_voice}"
                template_context += "\n"
            
            # Add opening scene if available
            if sekai_json.get('openingScene'):
                template_context += f"\nOpening Scene: {sekai_json.get('openingScene')}\n"
            
            # Build conversation history
            conversation_history = ""
            for i, (turn, user_input_hist) in enumerate(zip(st.session_state["game_state"], st.session_state["user_inputs"])):
                if user_input_hist.strip():
                    conversation_history += f"Player: {user_input_hist}\n"
                conversation_history += f"Story: {turn}\n\n"
            
            introduction_instruction = ""
            # Ensure all characters are introduced within the first 3 turns
            if len(st.session_state["game_state"]) < 3:
                full_story_text = "".join(st.session_state["game_state"])
                all_characters_in_json = sekai_json.get("characters", [])
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
            reply_prompt = f"""
You are an interactive fiction narrator for a visual novel.

{template_context}

CONVERSATION HISTORY:
{conversation_history}

The player character is {player_name}.
The player's input (action or dialogue) is: '{user_input}'.

Your role is to describe what happens next. Narrate the scene and have other non-player characters react.
IMPORTANT: Do NOT write dialogue or thoughts for the player character, {player_name}. Their input is already given.
{introduction_instruction}
Continue the story in script format. Keep narration brief. Do not give choices.
Stay consistent with the story template and character descriptions provided above.

Story Style Guidelines:
- Match the story tone: {story_tone}
- Use the specified pacing: {pacing}
- Write from the specified point of view: {point_of_view}
- Apply the narration style: {narration_style}
"""
            new_turn = model.generate_content(reply_prompt).text.strip()
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
            # Get the template context
            sekai_json = st.session_state.get("sekai_json", {})
            
            # Get advanced settings from the JSON template
            story_tone = sekai_json.get('storyTone', 'Balanced')
            pacing = sekai_json.get('pacing', 'Balanced')
            point_of_view = sekai_json.get('pointOfView', 'Third person')
            narration_style = sekai_json.get('narrationStyle', 'Balanced')
            
            # Build template context
            template_context = f"""
STORY TEMPLATE:
Title: {sekai_json.get('title', 'Unknown')}
Setting: {sekai_json.get('setting', 'Unknown')}
Genre: {sekai_json.get('genre', 'Fantasy')}
Keywords: {sekai_json.get('keywords', '')}

Story Style:
- Tone: {story_tone}
- Pacing: {pacing}
- Point of View: {point_of_view}
- Narration Style: {narration_style}

Characters:
"""
            # Add all characters from template
            for char in sekai_json.get('characters', []):
                char_name = char.get('name', 'Unknown')
                char_role = char.get('role', '')
                char_description = char.get('description', '')
                char_voice = char.get('voice_style', '')
                template_context += f"- {char_name} ({char_role}): {char_description}"
                if char_voice:
                    template_context += f" | Voice: {char_voice}"
                template_context += "\n"
            
            # Build conversation history
            conversation_history = ""
            for i, (turn, user_input_hist) in enumerate(zip(st.session_state["game_state"], st.session_state["user_inputs"])):
                if user_input_hist.strip():
                    conversation_history += f"Player: {user_input_hist}\n"
                conversation_history += f"Story: {turn}\n\n"
            
            player_name = st.session_state.get("user_name", "the player")
            
            choice_prompt = f"""
Based on the current story situation, generate 3 different action choices for {player_name}.

{template_context}

CONVERSATION HISTORY:
{conversation_history}

Generate 3 distinct choices that would make sense for the player character in this situation. 
Each choice should be:
- 1-2 sentences maximum
- Specific and actionable
- Different from each other
- Appropriate for the story context and character personalities
- Consistent with the story template and setting
- Match the story tone: {story_tone}
- Consider the pacing: {pacing}

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
    st.info("🌟 Let's create your magical world together! Each little detail will make it uniquely yours 💫")

    # --- World Inspiration ---
    st.markdown("### 🌈 World Inspiration")
    st.markdown("**What's a theme, object, or feeling that inspires your world? Anything works — just a spark!**")
    
    if "world_inspiration" not in st.session_state:
        st.session_state["world_inspiration"] = ""
    
    world_inspiration = st.text_input(
        "Your inspiration spark",
        value=st.session_state["world_inspiration"],
        placeholder="zoo / library / sunset / music / dreams / friendship",
        key="world_inspiration"
    )
    
    if world_inspiration.strip():
        # Dynamic feedback based on input
        inspiration_lower = world_inspiration.lower()
        if any(word in inspiration_lower for word in ["zoo", "animal", "creature"]):
            st.markdown('<div class="feedback-animation">🦁 <span class="emoji-sparkle">Ooooh, a zoo world!</span> That sounds fascinating! Let\'s shape it into something magical together.</div>', unsafe_allow_html=True)
        elif any(word in inspiration_lower for word in ["library", "book", "story"]):
            st.markdown('<div class="feedback-animation">📚 <span class="emoji-sparkle">A library world!</span> That sounds fascinating! Let\'s shape it into something magical together.</div>', unsafe_allow_html=True)
        elif any(word in inspiration_lower for word in ["sunset", "sun", "light"]):
            st.markdown('<div class="feedback-animation">🌅 <span class="emoji-sparkle">A sunset world!</span> That sounds fascinating! Let\'s shape it into something magical together.</div>', unsafe_allow_html=True)
        elif any(word in inspiration_lower for word in ["music", "song", "melody"]):
            st.markdown('<div class="feedback-animation">🎵 <span class="emoji-sparkle">A music world!</span> That sounds fascinating! Let\'s shape it into something magical together.</div>', unsafe_allow_html=True)
        elif any(word in inspiration_lower for word in ["dream", "sleep", "night"]):
            st.markdown('<div class="feedback-animation">💭 <span class="emoji-sparkle">A dream world!</span> That sounds fascinating! Let\'s shape it into something magical together.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="feedback-animation">✨ <span class="emoji-sparkle">Ooooh, that sounds fascinating!</span> Let\'s shape it into something magical together.</div>', unsafe_allow_html=True)

    # --- Environment / Setting ---
    st.markdown("### 🌍 Environment / Setting")
    st.markdown("**Where does your world take place? Think big: forest canopy, underwater palace, moonlit garden…**")
    
    if "world_environment" not in st.session_state:
        st.session_state["world_environment"] = ""
    
    world_environment = st.text_input(
        "Your world's environment",
        value=st.session_state["world_environment"],
        placeholder="a floating island in the sky / underwater palace / forest canopy / moonlit garden",
        key="world_environment"
    )
    
    if world_environment.strip():
        # Dynamic feedback based on input
        environment_lower = world_environment.lower()
        if any(word in environment_lower for word in ["floating", "sky", "air", "cloud"]):
            st.markdown('<div class="feedback-animation">☁️ <span class="emoji-sparkle">I can already picture it!</span> A floating world is full of wonder and potential.</div>', unsafe_allow_html=True)
        elif any(word in environment_lower for word in ["underwater", "ocean", "sea", "water"]):
            st.markdown('<div class="feedback-animation">🌊 <span class="emoji-sparkle">I can already picture it!</span> An underwater world is full of wonder and potential.</div>', unsafe_allow_html=True)
        elif any(word in environment_lower for word in ["forest", "tree", "nature"]):
            st.markdown('<div class="feedback-animation">🌳 <span class="emoji-sparkle">I can already picture it!</span> A forest world is full of wonder and potential.</div>', unsafe_allow_html=True)
        elif any(word in environment_lower for word in ["garden", "flower", "plant"]):
            st.markdown('<div class="feedback-animation">🌸 <span class="emoji-sparkle">I can already picture it!</span> A garden world is full of wonder and potential.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="feedback-animation">🏞️ <span class="emoji-sparkle">I can already picture it!</span> That setting is full of wonder and potential.</div>', unsafe_allow_html=True)

    # --- Mood / Vibe ---
    st.markdown("### 🎭 Mood / Vibe")
    st.markdown("**What kind of mood does your world have? Cozy? Mysterious? Epic? Peaceful?**")
    
    if "world_mood" not in st.session_state:
        st.session_state["world_mood"] = ""
    
    world_mood = st.text_input(
        "Your world's mood",
        value=st.session_state["world_mood"],
        placeholder="serene and dreamlike / cozy and warm / mysterious and dark / epic and adventurous",
        key="world_mood"
    )
    
    if world_mood.strip():
        # Dynamic feedback based on input
        mood_lower = world_mood.lower()
        if any(word in mood_lower for word in ["serene", "peaceful", "calm", "tranquil"]):
            st.markdown('<div class="feedback-animation">🧘 <span class="emoji-sparkle">Such a beautiful mood!</span> This world is going to feel unforgettable.</div>', unsafe_allow_html=True)
        elif any(word in mood_lower for word in ["cozy", "warm", "comfortable", "homey"]):
            st.markdown('<div class="feedback-animation">🏠 <span class="emoji-sparkle">Such a beautiful mood!</span> This world is going to feel unforgettable.</div>', unsafe_allow_html=True)
        elif any(word in mood_lower for word in ["mysterious", "dark", "enigmatic", "secret"]):
            st.markdown('<div class="feedback-animation">🔮 <span class="emoji-sparkle">Such a beautiful mood!</span> This world is going to feel unforgettable.</div>', unsafe_allow_html=True)
        elif any(word in mood_lower for word in ["epic", "adventurous", "heroic", "grand"]):
            st.markdown('<div class="feedback-animation">⚔️ <span class="emoji-sparkle">Such a beautiful mood!</span> This world is going to feel unforgettable.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="feedback-animation">💫 <span class="emoji-sparkle">Such a beautiful mood!</span> This world is going to feel unforgettable.</div>', unsafe_allow_html=True)

    # --- Magical Rule or Twist ---
    st.markdown("### 🧬 Magical Rule or Twist")
    st.markdown("**Is there something unique or magical about this world? Something that bends reality?**")
    
    if "world_magic" not in st.session_state:
        st.session_state["world_magic"] = ""
    
    world_magic = st.text_input(
        "Your world's magical twist",
        value=st.session_state["world_magic"],
        placeholder="time flows backward at sunset / gravity works sideways / memories become physical objects",
        key="world_magic"
    )
    
    if world_magic.strip():
        # Dynamic feedback based on input
        magic_lower = world_magic.lower()
        if any(word in magic_lower for word in ["time", "clock", "hour", "minute"]):
            st.markdown('<div class="feedback-animation">⏰ <span class="emoji-sparkle">Whoa… that\'s such a cool twist!</span> Your world just got even more unique.</div>', unsafe_allow_html=True)
        elif any(word in magic_lower for word in ["gravity", "float", "fall", "weight"]):
            st.markdown('<div class="feedback-animation">🌌 <span class="emoji-sparkle">Whoa… that\'s such a cool twist!</span> Your world just got even more unique.</div>', unsafe_allow_html=True)
        elif any(word in magic_lower for word in ["memory", "remember", "forget", "mind"]):
            st.markdown('<div class="feedback-animation">🧠 <span class="emoji-sparkle">Whoa… that\'s such a cool twist!</span> Your world just got even more unique.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="feedback-animation">🌀 <span class="emoji-sparkle">Whoa… that\'s such a cool twist!</span> Your world just got even more unique.</div>', unsafe_allow_html=True)

    # --- Genre Tags ---
    st.markdown("### 🎬 Optional Genre Tags")
    st.markdown("**Want to pick a genre to help shape the story? (You can mix two!)**")
    
    genre_options = [
        "Fantasy 🧝‍♀️", "Sci-Fi 🚀", "Romance 💘", "Slice of Life 🍰",
        "Mystery 🔍", "Horror 👻", "Comedy 😂", "Action ⚔️", "Historical 🏯"
    ]
    if 'world_genre' not in st.session_state:
        st.session_state['world_genre'] = []

    selected_genres = st.multiselect(
        "Your Sekai's Genre(s)",
        genre_options,
        default=st.session_state['world_genre'],
        key="world_genre"
    )
    
    if selected_genres:
        # Dynamic feedback based on genre selection
        genre_names = [g.split(' ', 1)[0] for g in selected_genres]
        if "Slice of Life" in genre_names:
            st.markdown('<div class="feedback-animation">📚 <span class="emoji-sparkle">Great choice!</span> Your Sekai will have a warm, reflective vibe with that genre.</div>', unsafe_allow_html=True)
        elif "Fantasy" in genre_names:
            st.markdown('<div class="feedback-animation">🧙‍♀️ <span class="emoji-sparkle">Great choice!</span> Your Sekai will have a magical, wondrous vibe with that genre.</div>', unsafe_allow_html=True)
        elif "Sci-Fi" in genre_names:
            st.markdown('<div class="feedback-animation">🚀 <span class="emoji-sparkle">Great choice!</span> Your Sekai will have a futuristic, innovative vibe with that genre.</div>', unsafe_allow_html=True)
        elif "Romance" in genre_names:
            st.markdown('<div class="feedback-animation">💕 <span class="emoji-sparkle">Great choice!</span> Your Sekai will have a heartfelt, emotional vibe with that genre.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="feedback-animation">🌟 <span class="emoji-sparkle">Great choice!</span> Your Sekai will have an amazing vibe with that genre.</div>', unsafe_allow_html=True)

    # --- AI World Generation Button ---
    if st.button("🔮 Generate My Magical World", type="primary"):
        st.toast("Working magic... Generating your Sekai world ✨")
        
        # Collect all the world creation data
        inspiration = st.session_state.get("world_inspiration", "").strip()
        environment = st.session_state.get("world_environment", "").strip()
        mood = st.session_state.get("world_mood", "").strip()
        magic = st.session_state.get("world_magic", "").strip()
        genres = st.session_state.get("world_genre", [])
        
        # Safety check for genres
        if not isinstance(genres, list):
            genres = []
        
        genre_str = ', '.join([g.split(' ', 1)[0] for g in genres if g]) if genres else ''
        
        # Build comprehensive prompt
        world_context = f"Inspiration: {inspiration}\nEnvironment: {environment}\nMood: {mood}"
        if magic:
            world_context += f"\nMagical Twist: {magic}"
        if genre_str:
            world_context += f"\nGenre: {genre_str}"
        
        prompt = f"""Generate a creative Sekai world concept based on the following guided creation:

{world_context}

Create a magical world that combines all these elements into a cohesive and engaging setting.

Respond with:
- Sekai Title (creative and memorable)
- World Setting (3-5 vivid sentences describing the world)
- Keywords (comma separated, 3-6 words that capture the essence)"""
        
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
        if setting:
            clean_setting = strip_stars(setting.group(1))
            st.session_state["world_setting"] = clean_setting
        if keywords:
            clean_keywords = strip_stars(keywords.group(1))
            st.session_state["world_keywords_input"] = clean_keywords
        
        st.rerun()

    # --- Display Generated World (if available) ---
    if st.session_state.get("world_title") or st.session_state.get("world_setting"):
        st.markdown("---")
        st.markdown("### 🎨 Your Generated World")
        
        # Display the generated world
        world_title = st.session_state.get("world_title", "")
        world_setting = st.session_state.get("world_setting", "")
        world_keywords = st.session_state.get("world_keywords_input", "")
        
        if world_title:
            st.markdown(f"**🎨 Sekai Title:** {world_title}")
        
        if world_setting:
            st.markdown(f"**📖 Sekai Description:** {world_setting}")
        
        if world_keywords:
            st.markdown(f"**🏷️ Keywords:** {world_keywords}")
        
        if world_title or world_setting:
            st.markdown('<div class="feedback-animation">🌟 <span class="emoji-sparkle">Your world is born!</span> It already feels so real… Let\'s meet your characters next!</div>', unsafe_allow_html=True)

    # --- Legacy fields (for manual editing) ---
    st.markdown("---")
    st.markdown("### ✏️ Manual World Details (Optional)")
    
    # Title + Setting Description
    if 'world_title' not in st.session_state:
        st.session_state['world_title'] = ''
    
    world_title = st.text_input(
        "Sekai Title",
        value=st.session_state['world_title'],
        key="world_title_edit"
    )
    
    if 'world_setting' not in st.session_state:
        st.session_state['world_setting'] = ''
    
    world_setting = st.text_area(
        "Describe the World Setting",
        value=st.session_state['world_setting'],
        key="world_setting_edit"
    )
    
    # World Keywords/Tags
    if 'world_keywords_input' not in st.session_state:
        st.session_state['world_keywords_input'] = ''
    
    world_keywords = st.text_input(
        "Keywords",
        value=st.session_state['world_keywords_input'],
        key="world_keywords_edit"
    )

    st.markdown("---")

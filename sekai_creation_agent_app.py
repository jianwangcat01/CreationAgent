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
        st.markdown(f"{step1_active} **Step 1: Core Details**")
    with col2:
        step2_active = "🟢" if st.session_state["char_creation_step"] >= 2 else "⚪"
        st.markdown(f"{step2_active} **Step 2: Personality**")
    with col3:
        step3_active = "🟢" if st.session_state["char_creation_step"] >= 3 else "⚪"
        st.markdown(f"{step3_active} **Step 3: Final Touches**")
    st.markdown("---")

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

    # Initialize session state for roleplay creation
    if "roleplay_step" not in st.session_state:
        st.session_state["roleplay_step"] = 1
    if "roleplay_feedback" not in st.session_state:
        st.session_state["roleplay_feedback"] = {}

    # Progress indicator
    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        step1_active = "🟢" if st.session_state["roleplay_step"] >= 1 else "⚪"
        st.markdown(f"{step1_active} **Step 1: World**")
    with col2:
        step2_active = "🟢" if st.session_state["roleplay_step"] >= 2 else "⚪"
        st.markdown(f"{step2_active} **Step 2: You**")
    with col3:
        step3_active = "🟢" if st.session_state["roleplay_step"] >= 3 else "⚪"
        st.markdown(f"{step3_active} **Step 3: Characters**")
    with col4:
        step4_active = "🟢" if st.session_state["roleplay_step"] >= 4 else "⚪"
        st.markdown(f"{step4_active} **Step 4: Template**")
    with col5:
        step5_active = "🟢" if st.session_state["roleplay_step"] >= 5 else "⚪"
        st.markdown(f"{step5_active} **Step 5: Play!**")
    st.markdown("---")

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

    # Step 1: Create Your Sekai World
    if st.session_state["roleplay_step"] == 1:
        st.subheader("🌍 Step 1: Create Your Sekai World")
        st.info("Let's start with your spark of inspiration! Don't overthink it — just share a mood, a moment, or a single word! We'll turn it into magic together 💫")

        # World Spark (Seed Idea)
        st.markdown("### 💡 What's your initial idea or vibe?")
        world_idea = st.text_input(
            "Your world spark",
            placeholder="A city where dreams are currency / Cyberpunk witches at high school / Haunted aquarium / Post-apocalyptic tea shop",
            key="world_idea_input"
        )
        
        if world_idea.strip():
            st.success("✨ Ooooh, that sounds fascinating. Let's shape it into something special!")

        # AI Suggestion Button
        if st.button("✨ AI: Turn My Idea into a World", type="primary"):
            st.toast("Working magic... Generating your Sekai world ✨")
            suggestion = generate_field(
                f"Let's craft a compelling concept around the '{world_idea}' idea.\n\n"
                "Please generate a structured Sekai concept with:\n\n"
                "**Title:** (a short and poetic title)\n"
                "**Genre:** (1-2 genres only, like Fantasy / Romance)\n"
                "**World Setting:** (2-3 sentence vivid description)\n"
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
            genre_options = ["Fantasy", "Sci-Fi", "Romance", "Slice of Life", "Mystery", "Horror", "Comedy", "Action", "Historical"]
            if new_genres:
                valid_genres = [g for g in new_genres if g in genre_options]
                if valid_genres:
                    st.session_state["world_genre"] = valid_genres
            st.rerun()

        # Genre Picker
        st.markdown("### 📚 Pick a Genre")
        st.markdown("Choose one or two — feel free to mix for unique vibes!")
        st.markdown("*Try combining Romance + Horror for something like vampire dating!*")
        
        genre_options = ["Fantasy 🧝‍♀️", "Sci-Fi 🚀", "Romance 💘", "Slice of Life 🍰", "Mystery 🔍", "Horror 👻", "Comedy 😂", "Action ⚔️", "Historical 🏯"]
        selected_genres = st.multiselect("Your Sekai's Genre(s)", genre_options, key="world_genre")
        
        if selected_genres:
            st.success(f"🌟 Awesome! Your world will have a {', '.join(selected_genres)} vibe!")

        # Title + Setting Description
        st.markdown("### 📖 Title and World Description")
        world_title = st.text_input(
            "Sekai Title", 
            value=st.session_state.get("world_title", ""),
            placeholder="The Midnight Library / Dream Currency City / Cyber Witch Academy"
        )
        
        world_setting = st.text_area(
            "Describe the World Setting", 
            value=st.session_state.get("world_setting", ""),
            placeholder="A magical library that only appears at midnight, where books come alive and stories write themselves...",
            height=100
        )
        
        if world_setting.strip():
            st.success("📝 This already feels so vivid! We're almost ready to meet your characters…")

        # World Keywords/Tags (optional)
        st.markdown("### 🏷️ World Keywords/Tags (Optional)")
        st.markdown("*These help AI generation later - add themes, elements, or vibes!*")
        world_keywords = st.text_input(
            "Keywords",
            placeholder="dreams, magic library, talking animals, steampunk, time travel",
            key="world_keywords_input"
        )

        # Navigation
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Back to Menu"):
                st.session_state["app_mode"] = None
                st.rerun()
        with col2:
            if world_title.strip() and world_setting.strip():
                if st.button("➡️ Next: Your Character", type="primary"):
                    st.session_state["roleplay_step"] = 2
                    st.rerun()
            else:
                st.button("➡️ Next: Your Character", disabled=True)

    # Step 2: Create Your Character (You in the World)
    elif st.session_state["roleplay_step"] == 2:
        st.subheader("👤 Step 2: Create Your Character")
        st.info("Now let's meet you! You'll be the heart of this world, so tell us about yourself.")

        # Get values from previous step
        world_title = st.session_state.get("world_title", "Your Sekai World")
        world_setting = st.session_state.get("world_setting", "A magical world")

        # Character Name
        st.markdown("### 🏷️ Character Name")
        st.markdown("Give yourself a name — or use your real one, it's up to you!")
        user_name = st.text_input(
            "Your Character's Name",
            value=st.session_state.get("user_name", ""),
            placeholder="Alex / Luna / Kai / Your real name",
            key="user_name_input"
        )

        # Character Traits
        st.markdown("### 💫 Traits / Background")
        st.markdown("Describe your personality, quirks, or even your magical powers 💫")
        user_traits = st.text_area(
            "Your Character's Traits",
            value=st.session_state.get("user_traits", ""),
            placeholder="Brave but impulsive, always rushing to help others / A quiet artist who sees spirits / Invented a tea that lets people relive memories",
            height=100,
            key="user_traits_input"
        )
        
        if user_traits.strip():
            st.success("🌟 Perfect! You're going to be the heart of this world.")

        # Navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Back"):
                st.session_state["roleplay_step"] = 1
                st.rerun()
        with col3:
            if user_name.strip() and user_traits.strip():
                if st.button("➡️ Next: Main Characters", type="primary"):
                    st.session_state["roleplay_step"] = 3
                    st.rerun()
            else:
                st.button("➡️ Next: Main Characters", disabled=True)

    # Step 3: Create Main Characters
    elif st.session_state["roleplay_step"] == 3:
        st.subheader("👥 Step 3: Create Main Characters")
        st.info("Now let's meet the other characters who will join your story!")

        # Get values from previous steps
        world_title = st.session_state.get("world_title", "Your Sekai World")
        world_setting = st.session_state.get("world_setting", "A magical world")
        user_name = st.session_state.get("user_name", "Alex")

        # Number of Characters
        st.markdown("### 🎭 How many characters will join your story?")
        st.markdown("Choose between 1 and 5 to start.")
        num_characters = st.slider("Number of Characters", 1, 5, 2, key="num_characters_slider")
        
        if num_characters > 1:
            st.success(f"🎉 Great! {num_characters} characters will make this story even more exciting!")

        # Generate All Characters Button
        if st.button("✨ AI: Generate All Characters", type="primary"):
            with st.spinner(f"Creating {num_characters} unique characters..."):
                prompt = (
                    f"Generate {num_characters} completely unique and different characters for the world: {world_setting}.\n"
                    f"The player's character is named '{user_name}'. Do not use this name for any of the generated characters.\n"
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
            st.rerun()

        # Character Forms
        characters = []
        for i in range(num_characters):
            st.markdown(f"### Character {i+1}")
            
            # Character Idea
            idea = st.text_input(
                f"Character Idea {i+1}",
                placeholder="Knight with amnesia who might be evil / Librarian who hides a secret / Rival time mage",
                key=f"idea_{i}"
            )
            
            # Generate Individual Character Button
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"🧠 AI: Generate Character {i+1}", key=f"gen_{i}"):
                    other_chars = [st.session_state.get(f"char_{j}", "") for j in range(num_characters) if j != i]
                    prompt = (
                        f"Create a new character for the following world: {world_setting}. "
                        f"The player's character is named '{user_name}'. Do not use this name.\n"
                        f"Ensure this character is clearly different from the player and any existing characters:\n"
                        + "\n".join(other_chars) +
                        "\n\nRespond in this format:\n"
                        "Name: <A standard first name and optional last name only, no titles or descriptions>\n"
                        "Role: <Character Role>\n"
                        "Traits: <Personality traits and special abilities>"
                    )
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
            
            characters.append({"name": name, "role": role, "traits": trait})

        # Navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Back"):
                st.session_state["roleplay_step"] = 2
                st.rerun()
        with col3:
            if all(char["name"].strip() and char["traits"].strip() for char in characters):
                if st.button("➡️ Next: Generate Template", type="primary"):
                    st.session_state["roleplay_step"] = 4
                    st.rerun()
            else:
                st.button("➡️ Next: Generate Template", disabled=True)

    # Step 4: Generate Sekai Story Template
    elif st.session_state["roleplay_step"] == 4:
        st.subheader("🪐 Step 4: Generate Sekai Story Template")
        st.info("Let's bring everything together and create your story template!")

        # Get values from previous steps
        world_title = st.session_state.get("world_title", "Your Sekai World")
        world_setting = st.session_state.get("world_setting", "A magical world")
        selected_genres = st.session_state.get("world_genre", [])
        user_name = st.session_state.get("user_name", "Alex")
        user_traits = st.session_state.get("user_traits", "Curious and brave")
        
        # Build characters list
        num_characters = st.session_state.get("num_characters_slider", 2)
        characters = []
        for i in range(num_characters):
            name = st.session_state.get(f"name_{i}", "")
            role = st.session_state.get(f"role_{i}", "")
            traits = st.session_state.get(f"trait_{i}", "")
            if name and traits:
                characters.append({"name": name, "role": role, "traits": traits})

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
                prompt = f"""
You are an AI for building JSON-based interactive stories.
Generate a story JSON with: title, setting, genre, characters (array of name, role, description), and openingScene.

Title: {world_title}
Setting: {world_setting}
Genre: {', '.join(selected_genres) if selected_genres else 'Fantasy'}
Characters:
- {user_name} (Player): {user_traits}
"""
                for c in characters:
                    prompt += f"- {c['name']} ({c['role']}): {c['traits']}\n"
                
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

        # Navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Back"):
                st.session_state["roleplay_step"] = 3
                st.rerun()
        with col3:
            if "sekai_json" in st.session_state:
                if st.button("➡️ Next: Start Game!", type="primary"):
                    st.session_state["roleplay_step"] = 5
                    st.rerun()
            else:
                st.button("➡️ Next: Start Game!", disabled=True)

    # Step 5: Start the Game
    elif st.session_state["roleplay_step"] == 5:
        st.subheader("🎮 Step 5: Start Your Sekai Journey!")
        
        # Get values
        user_name = st.session_state.get("user_name", "Alex")
        world_title = st.session_state.get("world_title", "Your Sekai World")
        
        st.success(f"🎉 You're all set! Ready to begin your Sekai journey with {user_name} in {world_title}? Let's go!")
        
        st.markdown("""
📜 **How to play:**
- Type your character's **dialogue** normally: e.g., `What are you doing here?`
- Type your character's **actions** with asterisks: e.g., `*run away from the library*`
- The AI will narrate the story and have other characters respond!
        """)

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

        # Navigation
        if st.button("⬅️ Back"):
            st.session_state["roleplay_step"] = 4
            st.rerun()

    # --- Game UI (after Start) ---
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

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

@keyframes memoryGlow {
    0%, 100% { box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    50% { box-shadow: 0 4px 16px rgba(138, 43, 226, 0.2); }
}

.feedback-animation {
    animation: fadeInUp 0.6s ease-out;
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    color: #155724;
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

.memory-card {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border: 1px solid #dee2e6;
    border-radius: 12px;
    padding: 16px;
    margin: 12px 0;
    position: relative;
    transition: all 0.3s ease;
    animation: memoryGlow 2s ease-in-out infinite;
}

.memory-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}

.memory-text {
    font-size: 14px;
    line-height: 1.5;
    color: #495057;
    margin: 0;
}

.memories-sidebar {
    background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
    border-left: 2px solid #e9ecef;
    padding: 20px;
    border-radius: 0 12px 12px 0;
}

.empty-memories {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border: 2px dashed #dee2e6;
    border-radius: 12px;
    padding: 30px 20px;
    text-align: center;
    color: #6c757d;
    font-style: italic;
    transition: all 0.3s ease;
}

.empty-memories:hover {
    border-color: #8a2be2;
    color: #8a2be2;
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
Design a unique character, then chat with them as if they were real! The AI will fully embody their personality, quirks, and charm.
""")

    if st.button("⬅️ Go Back to Menu", key="back_to_menu_char"):
        st.session_state["app_mode"] = None
        st.rerun()

    # Clear button at the top
    if st.button("🗑️ Clear All & Start Over", type="secondary", use_container_width=True):
        # Clear all character creation related session state
        keys_to_clear = [
            "char_creation_step", "char_feedback", "char_name_input", "char_role_input",
            "char_traits_input", "voice_style_input", "emotional_style_input", "lore_snippets_input",
            "opening_line_input", "char_image_upload", "chat_started", "chat_history",
            "character_prompt", "random_name_clicked", "random_role_clicked", "random_traits_clicked",
            "random_voice_clicked", "random_emotional_clicked", "random_lore_clicked", "random_opening_clicked",
            # New user fields
            "user_name_input", "user_role_input", "user_traits_input", "user_details_input",
            "random_user_name_clicked", "random_user_role_clicked", "random_user_traits_clicked", "random_user_details_clicked",
            # Memories
            "memories"
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    # --- Step Overview ---
    st.markdown("---")
    st.markdown("### 📋 Creation Steps Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 10px; background-color: #f8f9fa; border-radius: 8px; border: 2px solid #e9ecef;">
            <div style="font-size: 24px;">🌟</div>
            <div style="font-weight: bold; color: #495057;">Step 1</div>
            <div style="color: #6c757d; font-size: 14px;">Core Details</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 10px; background-color: #f8f9fa; border-radius: 8px; border: 2px solid #e9ecef;">
            <div style="font-size: 24px;">🧠</div>
            <div style="font-weight: bold; color: #495057;">Step 2</div>
            <div style="color: #6c757d; font-size: 14px;">Personality & Background</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 10px; background-color: #f8f9fa; border-radius: 8px; border: 2px solid #e9ecef;">
            <div style="font-size: 24px;">💫</div>
            <div style="font-weight: bold; color: #495057;">Step 3</div>
            <div style="color: #6c757d; font-size: 14px;">Expression & Relationships</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div style="text-align: center; padding: 10px; background-color: #f8f9fa; border-radius: 8px; border: 2px solid #e9ecef;">
            <div style="font-size: 24px;">🌟</div>
            <div style="font-weight: bold; color: #495057;">Step 4</div>
            <div style="color: #6c757d; font-size: 14px;">Your Role in the Story</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown("""
        <div style="text-align: center; padding: 10px; background-color: #f8f9fa; border-radius: 8px; border: 2px solid #e9ecef;">
            <div style="font-size: 24px;">✨</div>
            <div style="font-weight: bold; color: #495057;">Step 5</div>
            <div style="color: #6c757d; font-size: 14px;">Final Touches</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")

    # Helper function for random examples
    def get_random_example(field_type):
        examples = {
            "name": ["Eliora", "Jack the Brave", "Neko-chan", "Luna", "Kai", "Aria", "Artemis", "Rei"],
            "role": ["Your loyal knight", "The mischievous demon you summoned", "Your online girlfriend who only lives in a phone", "Time-traveling librarian", "Guardian spirit", "Space pirate captain", "Witch who sells cursed flowers", "Guardian spirit of your dreams"],
            "traits": [
                "Soft-spoken but bold when protecting loved ones. Speaks like an ancient priestess.",
                "He's sarcastic, flirty, and never serious — until someone mentions his tragic past.",
                "Chaotic and charming. A street magician who trusts no one but you.",
                "Calm, mysterious, and always speaks in riddles. Has knowledge of the past and future.",
                "Energetic and optimistic, but secretly carries deep emotional scars from their past.",
                "Wise and patient mentor figure who loves sharing stories and giving advice."
            ],
            "opening": [
                "Took you long enough. Shall we begin?",
                "You're late again, silly. I missed you.",
                "I thought you'd never return...",
                "Hey, it's you again! I've been waiting forever, dummy!",
                "Ah... another traveler. Come to disturb my peace?",
                "Greetings, brave soul! What brings you to my humble abode?",
                "Oh! You're finally here! I was starting to think you'd forgotten about me!",
                "Welcome, wanderer. I sense great potential within you..."
            ],
            "voice_style": [
                "Always says 'nya~' like a catgirl",
                "Talks in old poetic phrases",
                "Speaks bluntly and calls you 'human'",
                "Ends every sentence with 'my dear'",
                "Speaks in old English ('Thou art brave indeed!')",
                "Uses lots of exclamation marks and is very energetic",
                "Speaks very formally and uses big words",
                "Has a habit of repeating the last word of sentences"
            ],
            "emotional_style": [
                "Protective big brother energy",
                "Tsundere (hot and cold flirty)",
                "Warm and clingy childhood friend",
                "Obsessive yandere",
                "Gentle supportive best friend",
                "Mysterious and aloof but secretly caring",
                "Playful and teasing but deeply loyal"
            ],
            "lore_snippets": [
                "They still carry the ring you gave them long ago.",
                "You used to sneak into the temple garden together as kids.",
                "They once lost someone they loved, and still carry the necklace.",
                "You and the character used to play in the forest as kids.",
                "They have a mysterious scar that glows in the moonlight.",
                "The character saved your life once, but you don't remember it.",
                "They're actually from another dimension and miss their home.",
                "You both share a secret that no one else knows about."
            ],
            "user_name": ["Alex", "Mei", "Hiro", "Luna", "Kai", "Aria", "Sam", "Zoe", "Jordan", "Riley"],
            "user_role": [
                "The chosen one", "Their long-lost friend", "A time-traveling guest", 
                "The last hope", "A mysterious stranger", "Their destined partner",
                "A lost soul seeking answers", "The one who can save them",
                "A traveler from another world", "Their childhood friend returned"
            ],
            "user_traits": [
                "Curious but shy, always asking questions",
                "Assertive and logical, takes charge in difficult situations",
                "Flirty and playful, loves to tease and joke around",
                "Protective and caring, puts others before themselves",
                "Mysterious and quiet, speaks little but observes much",
                "Energetic and optimistic, brings light to dark situations",
                "Wise beyond their years, gives thoughtful advice",
                "Rebellious and free-spirited, doesn't follow rules"
            ],
            "user_details": [
                "Born on a full moon, loves stargazing",
                "Has a collection of antique books, favorite color is deep blue",
                "Learned to cook from their grandmother, loves spicy food",
                "Speaks three languages, dreams of traveling the world",
                "Has a pet cat named Shadow, afraid of thunderstorms",
                "Plays the violin, birthday is in autumn",
                "Collects seashells, favorite season is spring",
                "Loves to paint, has a scar on their left hand"
            ]
        }
        return random.choice(examples.get(field_type, ["Example"]))

    # Helper function to format character responses
    def format_character_response(response_text, char_name):
        """Format character responses to ensure expressions and movements are in parentheses and italics"""
        # Remove any existing character name prefix
        prefix = f"{char_name}:"
        if response_text.strip().lower().startswith(prefix.lower()):
            response_text = response_text.strip()[len(prefix):].lstrip()
        
        # Remove any quotation marks from dialogue
        response_text = response_text.strip()
        if response_text.startswith('"') and response_text.endswith('"'):
            response_text = response_text[1:-1]
        elif response_text.startswith('"'):
            response_text = response_text[1:]
        elif response_text.endswith('"'):
            response_text = response_text[:-1]
        
        # Ensure expressions and movements are properly formatted with parentheses and italics
        # The AI should already be formatting them correctly, but we can add some basic formatting if needed
        return response_text.strip()

    def memory_extractor(response_text, char_name):
        """Extract meaningful memories from AI character responses"""
        if not response_text.strip():
            return None
        
        # Configure Gemini API for memory extraction
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")
        
        memory_prompt = f"""
Analyze this character response and determine if it contains meaningful relationship-building content that should be remembered.

Character: {char_name}
Response: {response_text}

Look for:
- Emotional moments or revelations
- Secrets shared or confessions
- Important events or experiences mentioned
- Gifts given or received
- Promises made
- Personal stories shared
- Significant interactions or bonding moments
- Character development or relationship growth

If you find meaningful content, create a short memory (1-2 lines max) with an appropriate emoji.
If no meaningful content is found, respond with "NO_MEMORY".

Examples of good memories:
- 🎁 "Character gave you a special gift"
- 💝 "Character shared a personal secret about their past"
- 🌟 "Character promised to always protect you"
- 🎭 "Character revealed their true feelings for you"

Respond with either the memory or "NO_MEMORY".
"""
        
        try:
            response = model.generate_content(memory_prompt)
            memory = response.text.strip()
            
            # Clean up the response
            if memory.startswith('"') and memory.endswith('"'):
                memory = memory[1:-1]
            
            # Check if it's a valid memory (not NO_MEMORY)
            if memory and memory != "NO_MEMORY" and len(memory) > 5:
                return memory
            else:
                return None
        except Exception as e:
            # If memory extraction fails, return None
            return None

    # ===== STEP 1: CORE DETAILS =====
    st.markdown("---")
    st.markdown("## 🌟 Step 1: Core Details")
    st.info("Let's start with who they are.")

    # Character Name
    st.markdown("### 👤 Character Name")
    st.markdown("💡 **Pick something cool, elegant, or fun. Be as creative as you like!**")
    st.markdown("*Examples: Eliora, Jack the Brave, Neko-chan, Artemis, Rei*")
    
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
    
    # Random button below input
    if st.button("🎲 Random", key="random_name"):
        st.session_state["random_name_clicked"] = True
        st.rerun()
    
    if char_name.strip():
        st.markdown('<div class="feedback-animation">✅ <span class="emoji-sparkle">Love that name!</span> It already paints a picture in my mind.</div>', unsafe_allow_html=True)

    # Role/Occupation
    st.markdown("### 🎭 Role / Occupation")
    st.markdown("💡 **What's their role in your world or story? Be descriptive or playful!**")
    st.markdown("*Examples: Your loyal knight, Time-traveling librarian, Witch who sells cursed flowers, Guardian spirit of your dreams*")
    
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
    
    # Random button below input
    if st.button("🎲 Random", key="random_role"):
        st.session_state["random_role_clicked"] = True
        st.rerun()
    
    if char_role.strip():
        st.markdown('<div class="feedback-animation">✅ <span class="emoji-sparkle">That role is so vivid</span> — I want to meet them already!</div>', unsafe_allow_html=True)

    # ===== STEP 2: PERSONALITY & BACKGROUND =====
    st.markdown("---")
    st.markdown("## 🧠 Step 2: Personality & Background")
    st.info("Now give them depth — what makes them special?")

    # Personality Traits
    st.markdown("### 💫 Personality Traits & Backstory")
    st.markdown("💡 **Describe their nature, how they behave, and a glimpse of their story.**")
    st.markdown("*Examples:*")
    st.markdown("- *\"Soft-spoken but bold when protecting loved ones. Speaks like an ancient priestess.\"*")
    st.markdown("- *\"Chaotic and charming. A street magician who trusts no one but you.\"*")
    
    # Handle AI generation before creating the widget
    if st.button("🤖 AI Generate", key="ai_generate_traits"):
        if char_name.strip() and char_role.strip():
            # Configure Gemini API for generating traits
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")
            
            traits_prompt = f"""
Generate personality traits and backstory for a character based on their name and role.

Character Name: {char_name}
Role/Occupation: {char_role}

Create a compelling personality description that:
- Fits naturally with their name and role
- Includes personality traits and behavioral quirks
- Mentions a brief backstory or background
- Is 2-3 sentences maximum
- Feels authentic and engaging
- Avoids generic descriptions

Generate only the personality description, nothing else.
"""
            try:
                response = model.generate_content(traits_prompt)
                generated_traits = response.text.strip()
                if generated_traits.startswith('"') and generated_traits.endswith('"'):
                    generated_traits = generated_traits[1:-1]
                st.session_state["char_traits_input"] = generated_traits
                st.rerun()
            except Exception as e:
                st.error(f"Failed to generate traits: {e}")
        else:
            st.warning("Please complete Step 1 (Name and Role) before generating personality traits.")
    
    char_traits = st.text_area(
        "Tell us about their personality, background, and how they behave:",
        value=st.session_state.get("char_traits_input", ""),
        placeholder="Soft-spoken but bold when protecting loved ones. Speaks like an ancient priestess.",
        height=120,
        key="char_traits_input"
    )

    if char_traits.strip():
        st.markdown('<div class="feedback-animation">✅ <span class="emoji-sparkle">That\'s so rich</span> — they already feel alive!</div>', unsafe_allow_html=True)

    # ===== STEP 3: EXPRESSION & RELATIONSHIPS =====
    st.markdown("---")
    st.markdown("## 💫 Step 3: Expression & Relationships")
    st.info("Let's add how they speak and how they feel about you.")

    # Voice Style
    st.markdown("### 🗣️ Voice Style / Speech Quirks")
    st.markdown("💡 **Do they speak like a noble? A weirdo? A modern teen?**")
    st.markdown("*Examples:*")
    st.markdown("- *\"Always says 'nya~' like a catgirl\"*")
    st.markdown("- *\"Talks in old poetic phrases\"*")
    st.markdown("- *\"Speaks bluntly and calls you 'human'\"*")
    
    # Handle AI generation before creating the widget
    if st.button("🤖 AI Generate", key="ai_generate_voice"):
        if char_name.strip() and char_role.strip() and char_traits.strip():
            # Configure Gemini API for generating voice style
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")
            
            voice_prompt = f"""
Generate a unique voice style for a character based on their details.

Character Name: {char_name}
Role/Occupation: {char_role}
Personality/Background: {char_traits}

Create a distinctive speech pattern that:
- Matches their personality and role
- Is specific and memorable
- Could include speech quirks, mannerisms, or style
- Is 1-2 sentences maximum
- Feels authentic to the character

Generate only the voice style description, nothing else.
"""
            try:
                response = model.generate_content(voice_prompt)
                generated_voice = response.text.strip()
                if generated_voice.startswith('"') and generated_voice.endswith('"'):
                    generated_voice = generated_voice[1:-1]
                st.session_state["voice_style_input"] = generated_voice
                st.rerun()
            except Exception as e:
                st.error(f"Failed to generate voice style: {e}")
        else:
            st.warning("Please complete Steps 1 and 2 before generating voice style.")
    
    voice_style = st.text_input(
        "How do they speak? Any unique speech patterns?",
        value=st.session_state.get("voice_style_input", ""),
        placeholder="Always says 'nya~' like a catgirl / Talks in old poetic phrases",
        key="voice_style_input"
    )
    
    if voice_style.strip():
        st.markdown('<div class="feedback-animation">✅ <span class="emoji-sparkle">Nice!</span> I can already imagine hearing them talk.</div>', unsafe_allow_html=True)

    # Emotional Style
    st.markdown("### 💕 Emotional / Relationship Style")
    st.markdown("💡 **How do they emotionally connect with the user?**")
    st.markdown("*Examples:*")
    st.markdown("- *Protective big brother energy*")
    st.markdown("- *Tsundere (hot and cold flirty)*")
    st.markdown("- *Warm and clingy childhood friend*")
    
    # Handle AI generation before creating the widget
    if st.button("🤖 AI Generate", key="ai_generate_emotional"):
        if char_name.strip() and char_role.strip() and char_traits.strip():
            # Configure Gemini API for generating emotional style
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")
            
            emotional_prompt = f"""
Generate an emotional/relationship style for a character based on their details.

Character Name: {char_name}
Role/Occupation: {char_role}
Personality/Background: {char_traits}
Voice Style: {st.session_state.get('voice_style_input', '')}

Create an emotional connection style that:
- Fits their personality and role
- Describes how they relate to the user emotionally
- Could be protective, romantic, friendly, mysterious, etc.
- Is 1-2 sentences maximum
- Feels authentic and engaging

Generate only the emotional style description, nothing else.
"""
            try:
                response = model.generate_content(emotional_prompt)
                generated_emotional = response.text.strip()
                if generated_emotional.startswith('"') and generated_emotional.endswith('"'):
                    generated_emotional = generated_emotional[1:-1]
                st.session_state["emotional_style_input"] = generated_emotional
                st.rerun()
            except Exception as e:
                st.error(f"Failed to generate emotional style: {e}")
        else:
            st.warning("Please complete Steps 1 and 2 before generating emotional style.")
    
    emotional_style = st.text_input(
        "How do they treat the user emotionally?",
        value=st.session_state.get("emotional_style_input", ""),
        placeholder="Protective big brother energy / Tsundere (hot and cold flirty)",
        key="emotional_style_input"
    )
    
    if emotional_style.strip():
        st.markdown('<div class="feedback-animation">✅ <span class="emoji-sparkle">Adorable!</span> Their emotional vibe is going to make this chat really fun.</div>', unsafe_allow_html=True)

    # Lore Snippets
    st.markdown("### 📖 Memory or Lore Snippets")
    st.markdown("💡 **Add personal history or a shared memory with the user.**")
    st.markdown("*Examples:*")
    st.markdown("- *\"They still carry the ring you gave them long ago.\"*")
    st.markdown("- *\"You used to sneak into the temple garden together as kids.\"*")
    
    # Handle AI generation before creating the widget
    if st.button("🤖 AI Generate", key="ai_generate_lore"):
        if char_name.strip() and char_role.strip() and char_traits.strip():
            # Configure Gemini API for generating lore
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")
            
            lore_prompt = f"""
Generate a personal memory or lore snippet for a character based on their details.

Character Name: {char_name}
Role/Occupation: {char_role}
Personality/Background: {char_traits}
Voice Style: {st.session_state.get('voice_style_input', '')}
Emotional Style: {st.session_state.get('emotional_style_input', '')}

Create a shared memory or personal history that:
- Fits their personality and background
- Creates emotional connection with the user
- Could be a shared experience, gift, or meaningful moment
- Is 1-2 sentences maximum
- Adds depth to their relationship

Generate only the lore snippet, nothing else.
"""
            try:
                response = model.generate_content(lore_prompt)
                generated_lore = response.text.strip()
                if generated_lore.startswith('"') and generated_lore.endswith('"'):
                    generated_lore = generated_lore[1:-1]
                st.session_state["lore_snippets_input"] = generated_lore
                st.rerun()
            except Exception as e:
                st.error(f"Failed to generate lore: {e}")
        else:
            st.warning("Please complete Steps 1 and 2 before generating lore.")
    
    lore_snippets = st.text_area(
        "Any personal backstory or shared memories?",
        value=st.session_state.get("lore_snippets_input", ""),
        placeholder="They still carry the ring you gave them long ago. / You used to sneak into the temple garden together as kids.",
        height=80,
        key="lore_snippets_input"
    )
    
    if lore_snippets.strip():
        st.markdown('<div class="feedback-animation">✅ <span class="emoji-sparkle">That detail adds so much depth</span> — what a story!</div>', unsafe_allow_html=True)

    # ===== STEP 4: YOUR INFORMATION =====
    st.markdown("---")
    st.markdown("## 🌟 Step 4: Your Information")
    st.info("Now let's define who YOU are in this chat. This helps the character understand and interact with you better!")

    # User Name
    st.markdown("### 👤 Your Name")
    st.markdown("💡 **What's your name in this story?**")
    st.markdown("*Examples: Alex, Mei, Hiro, Luna, Kai, Aria*")
    
    # Get random user name if button was clicked
    if "random_user_name_clicked" not in st.session_state:
        st.session_state["random_user_name_clicked"] = False
    
    # Set default value based on random click or existing session state
    default_user_name = st.session_state.get("user_name_input", "")
    if st.session_state["random_user_name_clicked"]:
        default_user_name = get_random_example("user_name")
        st.session_state["user_name_input"] = default_user_name
        st.session_state["random_user_name_clicked"] = False
    
    user_name = st.text_input(
        "Your name",
        value=default_user_name,
        placeholder="Alex / Mei / Hiro / Luna",
        key="user_name_input"
    )
    
    # Random button below input
    if st.button("🎲 Random", key="random_user_name"):
        st.session_state["random_user_name_clicked"] = True
        st.rerun()
    
    if user_name.strip():
        st.markdown('<div class="feedback-animation">✅ <span class="emoji-sparkle">Nice name!</span> It suits you perfectly.</div>', unsafe_allow_html=True)

    # User Role/Identity
    st.markdown("### 🎭 Your Role / Identity")
    st.markdown("💡 **What's your role in relation to the character?**")
    st.markdown("*Examples: The chosen one, their long-lost friend, a time-traveling guest, the last hope*")
    
    # Get random user role if button was clicked
    if "random_user_role_clicked" not in st.session_state:
        st.session_state["random_user_role_clicked"] = False
    
    # Set default value based on random click or existing session state
    default_user_role = st.session_state.get("user_role_input", "")
    if st.session_state["random_user_role_clicked"]:
        default_user_role = get_random_example("user_role")
        st.session_state["user_role_input"] = default_user_role
        st.session_state["random_user_role_clicked"] = False
    
    user_role = st.text_input(
        "Your role or identity",
        value=default_user_role,
        placeholder="The chosen one / Their long-lost friend / A time-traveling guest",
        key="user_role_input"
    )
    
    # Random button below input
    if st.button("🎲 Random", key="random_user_role"):
        st.session_state["random_user_role_clicked"] = True
        st.rerun()
    
    if user_role.strip():
        st.markdown('<div class="feedback-animation">✅ <span class="emoji-sparkle">That role sounds exciting!</span> It adds so much depth to the story.</div>', unsafe_allow_html=True)

    # User Personality Traits
    st.markdown("### 💫 Your Key Personality Traits or Behavior")
    st.markdown("💡 **How do you behave? What's your personality like?**")
    st.markdown("*Examples: Curious but shy, assertive and logical, flirty and playful, protective and caring*")
    
    # Get random user traits if button was clicked
    if "random_user_traits_clicked" not in st.session_state:
        st.session_state["random_user_traits_clicked"] = False
    
    # Set default value based on random click or existing session state
    default_user_traits = st.session_state.get("user_traits_input", "")
    if st.session_state["random_user_traits_clicked"]:
        default_user_traits = get_random_example("user_traits")
        st.session_state["user_traits_input"] = default_user_traits
        st.session_state["random_user_traits_clicked"] = False
    
    user_traits = st.text_area(
        "Your personality traits or behavior",
        value=default_user_traits,
        placeholder="Curious but shy, always asking questions / Assertive and logical, takes charge in difficult situations",
        height=80,
        key="user_traits_input"
    )
    
    # Random button below input
    if st.button("🎲 Random", key="random_user_traits"):
        st.session_state["random_user_traits_clicked"] = True
        st.rerun()
    
    if user_traits.strip():
        st.markdown('<div class="feedback-animation">✅ <span class="emoji-sparkle">Great personality!</span> The character will love getting to know you.</div>', unsafe_allow_html=True)

    # User Details
    st.markdown("### 📝 Anything Relevant the Character Should Know")
    st.markdown("💡 **Share some personal details that make you unique!**")
    st.markdown("*Examples: Born on a full moon, loves stargazing / Has a collection of antique books, favorite color is deep blue / Learned to cook from their grandmother, loves spicy food*")
    
    # Get random user details if button was clicked
    if "random_user_details_clicked" not in st.session_state:
        st.session_state["random_user_details_clicked"] = False
    
    # Set default value based on random click or existing session state
    default_user_details = st.session_state.get("user_details_input", "")
    if st.session_state["random_user_details_clicked"]:
        default_user_details = get_random_example("user_details")
        st.session_state["user_details_input"] = default_user_details
        st.session_state["random_user_details_clicked"] = False
    
    user_details = st.text_area(
        "Personal details or preferences",
        value=default_user_details,
        placeholder="Born on a full moon, loves stargazing / Has a collection of antique books, favorite color is deep blue",
        height=80,
        key="user_details_input"
    )
    
    # Random button below input
    if st.button("🎲 Random", key="random_user_details"):
        st.session_state["random_user_details_clicked"] = True
        st.rerun()
    
    if user_details.strip():
        st.markdown('<div class="feedback-animation">✅ <span class="emoji-sparkle">Those details are perfect!</span> They\'ll make conversations so much more personal.</div>', unsafe_allow_html=True)

    # ===== STEP 5: FINAL TOUCHES =====
    st.markdown("---")
    st.markdown("## ✨ Step 5: Final Touches")
    st.info("Let's get ready for your first encounter.")

    # Opening Lines
    st.markdown("### 💬 Opening Line (Optional)")
    st.markdown("💡 **What's the first thing they say when the story begins?**")
    st.markdown("*Examples:*")
    st.markdown("- *\"Took you long enough. Shall we begin?\"*")
    st.markdown("- *\"You're late again, silly. I missed you.\"*")
    st.markdown("- *\"I thought you'd never return...\"*")
    st.markdown("**💡 Tip:** If you don't write anything here, I'll come up with something fun for you!")
    
    # Handle AI generation before creating the widget
    if st.button("🤖 AI Generate", key="ai_generate_opening"):
        if char_name.strip() and char_role.strip() and char_traits.strip():
            # Configure Gemini API for generating opening line
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")
            
            opening_prompt = f"""
Generate an engaging opening line for a character based on their details.

Character Name: {char_name}
Role/Occupation: {char_role}
Personality/Background: {char_traits}
Voice Style: {st.session_state.get('voice_style_input', '')}
Emotional Style: {st.session_state.get('emotional_style_input', '')}
Lore: {st.session_state.get('lore_snippets_input', '')}

The opening line should:
- Be in character and reflect their personality
- Be welcoming and engaging
- Be 1-2 sentences maximum
- Feel natural and conversational
- Not mention being an AI or fictional character
- Incorporate their voice style if specified
- Match their emotional style
- FORMATTING: When you make expressions, movements, or actions, put them in parentheses and italics like (smiles warmly) or (adjusts their cloak). Dialogue should be normal text without quotation marks.

Generate only the opening line, nothing else.
"""
            try:
                response = model.generate_content(opening_prompt)
                generated_opening = response.text.strip()
                if generated_opening.startswith('"') and generated_opening.endswith('"'):
                    generated_opening = generated_opening[1:-1]
                st.session_state["opening_line_input"] = generated_opening
                st.rerun()
            except Exception as e:
                st.error(f"Failed to generate opening line: {e}")
        else:
            st.warning("Please complete Steps 1 and 2 before generating opening line.")
    
    opening_line = st.text_area(
        "What should they say to start the conversation?",
        value=st.session_state.get("opening_line_input", ""),
        placeholder="Took you long enough. Shall we begin?",
        height=80,
        key="opening_line_input"
    )

    if opening_line.strip():
        st.markdown('<div class="feedback-animation">✅ <span class="emoji-sparkle">Oooh, such a strong intro!</span> They\'re totally in character.</div>', unsafe_allow_html=True)

    # Character Image
    st.markdown("### 🖼️ Character Image (Optional)")
    st.markdown("💡 **Upload an image or generate one with Hugging Face models like animagine-xl or waifu-diffusion.**")
    
    char_image = st.file_uploader(
        "Upload: PNG / JPG / JPEG (Max 200MB)",
        type=["png", "jpg", "jpeg"],
        key="char_image_upload"
    )

    if char_image:
        st.markdown('<div class="feedback-animation">✅ <span class="emoji-sparkle">Visuals complete!</span> That\'s a full character now!</div>', unsafe_allow_html=True)

    # Character Preview
    st.markdown("### 👀 Character Preview")
    st.markdown("**Your character so far:**")
    
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
        **🎭 Name:** {char_name}
        
        **✨ Role:** {char_role}
        
        **💫 Personality:** {char_traits[:100]}{'...' if len(char_traits) > 100 else ''}
        
        **🗣️ Speech Style:** {voice_style if voice_style.strip() else 'Natural'}
        
        **💕 Emotion:** {emotional_style if emotional_style.strip() else 'Friendly'}
        
        **📖 Memory:** {lore_snippets if lore_snippets.strip() else 'None yet'}
        
        **💬 Opening Line:** {opening_line if opening_line.strip() else 'Will be generated'}
        
        **👤 Your Name:** {user_name if user_name.strip() else 'Not set yet'}
        
        **🎭 Your Role:** {user_role if user_role.strip() else 'Not set yet'}
        
        **💫 Your Traits:** {user_traits[:50] if user_traits.strip() else 'Not set yet'}{'...' if len(user_traits) > 50 and user_traits.strip() else ''}
        """)

    # ===== CHARACTER TEMPLATE GENERATION =====
    st.markdown("---")
    st.markdown("## 📜 Character Template Generation")
    st.info("Generate a character template to see all the information gathered and prepare for chat!")

    if st.button("🧙 Generate Character Template", type="primary"):
        if char_name.strip() and char_role.strip() and char_traits.strip():
            with st.spinner("Creating your character template..."):
                # Build character template
                character_template = {
                    "name": char_name,
                    "role": char_role,
                    "personality": char_traits,
                    "voice_style": voice_style if voice_style.strip() else "Natural",
                    "emotional_style": emotional_style if emotional_style.strip() else "Friendly",
                    "lore_snippets": lore_snippets if lore_snippets.strip() else "",
                    "opening_line": opening_line if opening_line.strip() else "",
                    "image_uploaded": char_image is not None,
                    # User information
                    "user_name": user_name if user_name.strip() else "User",
                    "user_role": user_role if user_role.strip() else "",
                    "user_traits": user_traits if user_traits.strip() else "",
                    "user_details": user_details if user_details.strip() else ""
                }
                
                st.session_state["character_template"] = character_template
                st.success("🎉 Character template generated successfully!")
        else:
            st.warning("⚠️ Please complete at least the Name, Role, and Personality fields before generating the template.")

    # Display generated template if available
    if "character_template" in st.session_state:
        st.markdown("### 📋 Generated Character Template")
        template = st.session_state["character_template"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Template Details:**")
            st.json(template)
        
        with col2:
            st.markdown("**Ready to Chat:**")
            st.markdown("""
            Your character template is ready! You can now:
            - Start chatting with your character
            - Edit any details above and regenerate
            - Save this template for future use
            """)

    # Start Chat Button
    st.markdown("---")
    if st.button("🔮 Start Chat with Character", type="primary", use_container_width=True):
        # Check if we have a template or enough basic info
        if "character_template" in st.session_state:
            template = st.session_state["character_template"]
            char_name = template["name"]
            char_role = template["role"]
            char_traits = template["personality"]
            voice_style = template["voice_style"]
            emotional_style = template["emotional_style"]
            lore_snippets = template["lore_snippets"]
            opening_line = template["opening_line"]
        elif char_name.strip() and char_role.strip() and char_traits.strip():
            # Use current form data
            pass
        else:
            st.error("Please complete the character creation and generate a template first.")
            st.stop()
        
        # Start the chat
        st.session_state["chat_started"] = True
        st.session_state["chat_history"] = []
        
        # Build character prompt with advanced options
        character_prompt = f"You are roleplaying as a fictional character named {char_name}. "
        character_prompt += f"Your role is: {char_role}. Your personality and background: {char_traits}.\n\n"
        
        if voice_style and voice_style != "Natural":
            character_prompt += f"Speech style: {voice_style}\n"
        if emotional_style and emotional_style != "Friendly":
            character_prompt += f"Emotional style: {emotional_style}\n"
        if lore_snippets:
            character_prompt += f"Background lore: {lore_snippets}\n"
        
        # Add user information to the character prompt
        if user_name.strip() and user_name != "User":
            character_prompt += f"\nThe user's name is: {user_name}\n"
        if user_role.strip():
            character_prompt += f"The user's role/identity is: {user_role}\n"
        if user_traits.strip():
            character_prompt += f"The user's personality traits: {user_traits}\n"
        if user_details.strip():
            character_prompt += f"Personal details about the user: {user_details}\n"
        
        character_prompt += "\nSpeak naturally as this character would. Stay in character and never say you're an AI.\n"
        character_prompt += "Keep your replies concise (under 100 words) unless the user asks for a long story or detailed answer.\n"
        character_prompt += "Use the information about the user to make conversations more personal and engaging.\n"
        character_prompt += "FORMATTING: When you make expressions, movements, or actions, put them in parentheses and italics like (smiles warmly) or (adjusts their cloak). Dialogue should be normal text without quotation marks.\n"
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
- FORMATTING: When you make expressions, movements, or actions, put them in parentheses and italics like (smiles warmly) or (adjusts their cloak). Dialogue should be normal text without quotation marks.

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
        
        # Initialize memories and extract from opening line
        if "memories" not in st.session_state:
            st.session_state["memories"] = []
        
        # Extract memory from opening line if meaningful
        opening_memory = memory_extractor(opening_line.strip(), char_name)
        if opening_memory:
            st.session_state["memories"].append(opening_memory)
        
        st.rerun()

    # --- Chat UI (after Start) ---
    if st.session_state.get("chat_started"):
        st.markdown("---")
        st.subheader(f"🗨️ Chat with {st.session_state.get('char_name_input', 'Your Character')}")
        
        # Chat instructions
        st.markdown("**💡 Chat Instructions:**")
        st.markdown("- Put your movements, gestures, and expressions in brackets like `(waves hello)` or `(smiles shyly)`")
        st.markdown("- Type normal text for what you want to say (no quotation marks needed)")
        st.markdown("- Example: `(adjusts glasses) Hello there! How are you today?`")
        st.markdown("---")
        
        # Initialize memories in session state if not exists
        if "memories" not in st.session_state:
            st.session_state["memories"] = []
        
        # Create two columns: chat and memories sidebar
        chat_col, memories_col = st.columns([3, 1])
        
        with chat_col:
            # Character info display
            char_name = st.session_state.get("char_name_input", "Luna")
            char_image = st.session_state.get("char_image_upload")
            
            if char_image:
                st.image(char_image, use_container_width=False, width=200, caption=f"{char_name}'s Avatar")
            
            # Chat history
            for i, entry in enumerate(st.session_state["chat_history"]):
                if entry['user']:
                    st.markdown(f"**You:** {entry['user']}")
                # Format character response
                bot_reply = format_character_response(entry['bot'], char_name)
                st.markdown(f"**{char_name}:** {bot_reply}")
            
            # Chat input
            user_input = st.text_input("Your Message", key="char_chat_input")
            if st.button("📩 Send"):
                # Get current memories for context
                memories_list = st.session_state.get("memories", [])
                memories_text = ""
                if memories_list:
                    memories_text = "\n\nHere are shared memories between user and character:\n" + "\n".join([f"- {memory}" for memory in memories_list])
                
                model = genai.GenerativeModel("gemini-2.5-flash-lite-preview-06-17")
                full_prompt = st.session_state["character_prompt"] + memories_text + "\n\n"
                for entry in st.session_state["chat_history"]:
                    if entry['user']:
                        full_prompt += f"You: {entry['user']}\n{char_name}: {entry['bot']}\n"
                    else:
                        full_prompt += f"{char_name}: {entry['bot']}\n"
                full_prompt += f"You: {user_input}\n{char_name}:"
                
                response = model.generate_content(full_prompt)
                reply = response.text.strip()
                # Format the reply before saving
                formatted_reply = format_character_response(reply, char_name)
                
                # Extract memory from the response
                new_memory = memory_extractor(formatted_reply, char_name)
                if new_memory and new_memory not in st.session_state["memories"]:
                    st.session_state["memories"].append(new_memory)
                
                st.session_state["chat_history"].append({
                    "user": user_input,
                    "bot": formatted_reply
                })
                
                # Clear the input field
                st.session_state["char_chat_input"] = ""
                st.rerun()

            # Back to character creation
            if st.button("🔄 Create New Character"):
                st.session_state["chat_started"] = False
                st.rerun()
        
        with memories_col:
            # Memories Sidebar
            st.markdown("""
            <div class="memories-sidebar">
                <h3>💭 Memories</h3>
                <p style="color: #6c757d; font-size: 14px; margin-bottom: 20px;">
                    <em>Important moments shared with your character</em>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.session_state["memories"]:
                for i, memory in enumerate(st.session_state["memories"]):
                    # Create a styled memory card
                    st.markdown(f"""
                    <div class="memory-card">
                        <p class="memory-text">{memory}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Delete button for each memory
                    col1, col2 = st.columns([4, 1])
                    with col2:
                        if st.button(f"🗑️", key=f"delete_memory_{i}", help="Delete this memory"):
                            st.session_state["memories"].pop(i)
                            st.rerun()
                
                st.markdown("---")
                # Clear all memories button
                if st.button("🗑️ Clear All Memories", key="clear_all_memories", use_container_width=True):
                    st.session_state["memories"] = []
                    st.rerun()
            else:
                st.markdown("""
                <div class="empty-memories">
                    No memories yet.<br>
                    Start chatting to create special moments! ✨
                </div>
                """, unsafe_allow_html=True)
    
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
                f"voice_style_{i}", f"relationship_{i}", f"opening_line_{i}", f"gen_{i}"
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
            # Add all characters from template with detailed descriptions
            for char in sekai_json.get('characters', []):
                char_name = char.get('name', 'Unknown')
                char_role = char.get('role', '')
                char_description = char.get('description', '')
                char_voice = char.get('voice_style', '')
                char_relationship = char.get('relationship', '')
                template_context += f"- {char_name} ({char_role}): {char_description}"
                if char_voice:
                    template_context += f" | Voice: {char_voice}"
                if char_relationship:
                    template_context += f" | Relationship: {char_relationship}"
                template_context += "\n"
            
            # Add opening scene if available
            if sekai_json.get('openingScene'):
                template_context += f"\nOpening Scene: {sekai_json.get('openingScene')}\n"
            
            # Build conversation history with better formatting
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
            
            # Enhanced prompt for better consistency and formatting
            reply_prompt = f"""
You are an interactive fiction narrator for a visual novel. Maintain consistent character voices and story coherence.

{template_context}

CONVERSATION HISTORY:
{conversation_history}

The player character is {player_name}.
The player's input (action or dialogue) is: '{user_input}'.

CRITICAL FORMATTING RULES:
- Write in visual novel script format
- Use this exact format for each line:
  narrator description of what happens (no quotes, no italics)
  CharacterName (expression/mood) "dialogue or thoughts"
- Keep narrator descriptions short and concise
- Maintain consistent character voices and personalities
- Do NOT write dialogue or thoughts for the player character, {player_name}
- End with: **What do you do?**

CONTENT GUIDELINES:
- Stay true to character personalities and voice styles from the template
- Maintain story coherence and logical progression
- Remember all character relationships and backstories from the template
- Keep responses engaging but not overwhelming
- {introduction_instruction}
- Match the story tone: {story_tone}
- Use the specified pacing: {pacing}
- Write from the specified point of view: {point_of_view}
- Apply the narration style: {narration_style}

MEMORY REQUIREMENTS:
- Remember the complete story template and all character details
- Maintain consistency with all previous interactions
- Keep track of character relationships and story progression
- Ensure character expressions and moods match their personalities

Generate the next story turn in proper visual novel script format:
"""
            
            try:
                new_turn = model.generate_content(reply_prompt).text.strip()
                
                # Clean up the response to ensure proper formatting
                cleaned_turn = clean_story_response(new_turn)
                
                st.session_state["game_state"].append(cleaned_turn)
                st.session_state["user_inputs"].append(user_input.strip())

                # Clear the input box for the next turn
                st.session_state["reply_input"] = ""

                existing_colors = st.session_state.get("story_colors", [])
                available_colors = [
                    c
                    for c in ["#fce4ec", "#e3f2fd", "#e8f5e9", "#fff8e1", "#ede7f6"]
                    if c != existing_colors[-1]
                ]
                new_color = random.choice(available_colors)
                st.session_state["story_colors"].append(new_color)
                
            except Exception as e:
                st.error(f"Error generating story response: {e}")
                # Fallback response
                fallback_response = f'narrator The story continues...\n**What do you do?**'
                st.session_state["game_state"].append(fallback_response)
                st.session_state["user_inputs"].append(user_input.strip())
                st.session_state["reply_input"] = ""
                
                existing_colors = st.session_state.get("story_colors", [])
                available_colors = [
                    c
                    for c in ["#fce4ec", "#e3f2fd", "#e8f5e9", "#fff8e1", "#ede7f6"]
                    if c != existing_colors[-1]
                ]
                new_color = random.choice(available_colors)
                st.session_state["story_colors"].append(new_color)
            # st.rerun is implicit with on_click callback

    def clean_story_response(response_text):
        """Clean and format the story response to ensure consistency"""
        if not response_text:
            return 'narrator The story continues...\n**What do you do?**'
        
        # Split into lines and clean each line
        lines = response_text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Handle different response formats
            if line.startswith('**') and line.endswith('**'):
                # Keep bold text as is
                cleaned_lines.append(line)
            elif '"' in line:
                # Check if it's already in script format with expression: CharacterName (expression) "dialogue"
                if re.match(r'^[a-zA-Z\s]+\([^)]*\)\s*["\']', line):
                    # Already in correct format, keep as is
                    cleaned_lines.append(line)
                # Check if it's in basic script format: CharacterName "dialogue"
                elif re.match(r'^[a-zA-Z\s]+["\']', line):
                    # Convert to new format: CharacterName (expression) "dialogue"
                    match = re.match(r'^([^"]+)\s*"([^"]+)"', line)
                    if match:
                        speaker = match.group(1).strip()
                        dialogue = match.group(2)
                        if speaker.lower() == 'narrator':
                            # Narrator without quotes
                            cleaned_lines.append(f'narrator {dialogue}')
                        else:
                            # Character with expression
                            cleaned_lines.append(f'{speaker} (calmly) "{dialogue}"')
                    else:
                        cleaned_lines.append(line)
                else:
                    # Try to convert to script format
                    match = re.match(r'^([^:]+):\s*["\'](.+)["\']', line)
                    if match:
                        speaker = match.group(1).strip()
                        dialogue = match.group(2)
                        if speaker.lower() == 'narrator':
                            cleaned_lines.append(f'narrator {dialogue}')
                        else:
                            cleaned_lines.append(f'{speaker} (calmly) "{dialogue}"')
                    else:
                        # Assume it's narration
                        cleaned_lines.append(f'narrator {line}')
            else:
                # Assume it's narration
                cleaned_lines.append(f'narrator {line}')
        
        # Ensure it ends with "What do you do?"
        if not any('What do you do?' in line for line in cleaned_lines):
            cleaned_lines.append('**What do you do?**')
        
        return '\n'.join(cleaned_lines)

    def format_story_block(block_text):
        """Format story block for consistent display"""
        if not block_text:
            return '<p style="margin:4px 0; color:#666;">Story continues...</p>'
        
        formatted_lines = []
        lines = block_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Handle "What do you do?" prompt
            if 'What do you do?' in line:
                formatted_lines.append('<p style="margin:8px 0; font-weight:bold; color:#2c3e50;">**What do you do?**</p>')
                continue
            
            # Remove 'narrator' prefix for narration lines
            if line.startswith('narrator '):
                content = line[9:]  # Remove 'narrator '
                formatted_lines.append(f'<p style="margin:4px 0; color:#555;">{content}</p>')
                continue
            
            # Character dialogue with expressions: bold everything before the first quote
            if '"' in line:
                # Try to extract speaker with expression: CharacterName (expression) "dialogue"
                match = re.match(r'^([^(]+\([^)]*\))\s*"([^"]+)"', line)
                if match:
                    speaker_expr = match.group(1).strip()
                    dialogue = match.group(2)
                    formatted_lines.append(f'<p style="margin:4px 0;"><b style="color:#2c3e50;">{speaker_expr}:</b> "{dialogue}"</p>')
                    continue
                
                # Try to extract speaker without expression: CharacterName "dialogue"
                match = re.match(r'^([^"]+)\s*"([^"]+)"', line)
                if match:
                    speaker = match.group(1).strip()
                    dialogue = match.group(2)
                    # Only bold if it looks like a character name (not just random text)
                    if not speaker.lower() in ['narrator', 'story', 'scene'] and len(speaker.strip()) > 0:
                        formatted_lines.append(f'<p style="margin:4px 0;"><b style="color:#2c3e50;">{speaker}:</b> "{dialogue}"</p>')
                    else:
                        formatted_lines.append(f'<p style="margin:4px 0; color:#555;">{speaker}: "{dialogue}"</p>')
                    continue
            
            # Handle other formats (fallback)
            if line.startswith('**') and line.endswith('**'):
                # Bold text
                content = line[2:-2]
                formatted_lines.append(f'<p style="margin:4px 0; font-weight:bold; color:#2c3e50;">{content}</p>')
            else:
                # Plain narration (no narrator prefix)
                formatted_lines.append(f'<p style="margin:4px 0; color:#555;">{line}</p>')
        
        return ''.join(formatted_lines)

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
                char_relationship = char.get('relationship', '')
                template_context += f"- {char_name} ({char_role}): {char_description}"
                if char_voice:
                    template_context += f" | Voice: {char_voice}"
                if char_relationship:
                    template_context += f" | Relationship: {char_relationship}"
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
- Different from each other (one dialogue, one action, one investigation/exploration)
- Appropriate for the story context and character personalities
- Consistent with the story template and setting
- Match the story tone: {story_tone}
- Consider the pacing: {pacing}

CHOICE TYPES:
1. Dialogue choice (speaking to someone)
2. Action choice (doing something physical)
3. Investigation/Exploration choice (examining surroundings or moving)

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
                
                # Ensure we have exactly 3 choices with fallbacks
                while len(choices) < 3:
                    if len(choices) == 0:
                        choices.append("Ask someone nearby what's happening")
                    elif len(choices) == 1:
                        choices.append("Look around the area for clues")
                    else:
                        choices.append("Continue exploring the surroundings")
                
                if len(choices) > 3:
                    choices = choices[:3]
                
                return choices
            except Exception as e:
                # Fallback choices
                return [
                    "Ask someone nearby what's happening",
                    "Look around the area for clues", 
                    "Continue exploring the surroundings"
                ]
        return [
            "Ask someone nearby what's happening",
            "Look around the area for clues", 
            "Continue exploring the surroundings"
        ]

    # --- Step Overview ---
    st.markdown("---")
    st.markdown("### 📋 Creation Steps Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 10px; background-color: #f8f9fa; border-radius: 8px; border: 2px solid #e9ecef;">
            <div style="font-size: 24px;">🌟</div>
            <div style="font-weight: bold; color: #495057;">Step 1</div>
            <div style="color: #6c757d; font-size: 14px;">Core Details</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 10px; background-color: #f8f9fa; border-radius: 8px; border: 2px solid #e9ecef;">
            <div style="font-size: 24px;">🧠</div>
            <div style="font-weight: bold; color: #495057;">Step 2</div>
            <div style="color: #6c757d; font-size: 14px;">Personality & Background</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 10px; background-color: #f8f9fa; border-radius: 8px; border: 2px solid #e9ecef;">
            <div style="font-size: 24px;">💫</div>
            <div style="font-weight: bold; color: #495057;">Step 3</div>
            <div style="color: #6c757d; font-size: 14px;">Expression & Relationships</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div style="text-align: center; padding: 10px; background-color: #f8f9fa; border-radius: 8px; border: 2px solid #e9ecef;">
            <div style="font-size: 24px;">🌟</div>
            <div style="font-weight: bold; color: #495057;">Step 4</div>
            <div style="color: #6c757d; font-size: 14px;">Your Role in the Story</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown("""
        <div style="text-align: center; padding: 10px; background-color: #f8f9fa; border-radius: 8px; border: 2px solid #e9ecef;">
            <div style="font-size: 24px;">✨</div>
            <div style="font-weight: bold; color: #495057;">Step 5</div>
            <div style="color: #6c757d; font-size: 14px;">Final Touches</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")

    # ===== STEP 1: CREATE YOUR SEKAI WORLD =====
    st.markdown("---")
    st.markdown("## 🌍 Step 1: Your Sekai World")

    # --- World Inspiration ---
    st.markdown("### 🌈 World Inspiration")
    st.markdown("**What's a theme, object, or feeling that inspires your world? Anything works — just a spark!**")

    # Add random button above input
    if st.button("🎲 Random Inspiration", key="random_inspiration"):
        random_inspirations = [
            "zoo", "library", "sunset", "music", "dreams", "friendship", "ancient ruins", "lost city", "enchanted forest", "forgotten melody"
        ]
        st.session_state["world_inspiration"] = random.choice(random_inspirations)
        st.rerun()
    
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
            st.success("🦁 Ooooh, a zoo world! That sounds fascinating! Let's shape it into something magical together.")
        elif any(word in inspiration_lower for word in ["library", "book", "story"]):
            st.success("📚 A library world! That sounds fascinating! Let's shape it into something magical together.")
        elif any(word in inspiration_lower for word in ["sunset", "sun", "light"]):
            st.success("🌅 A sunset world! That sounds fascinating! Let's shape it into something magical together.")
        elif any(word in inspiration_lower for word in ["music", "song", "melody"]):
            st.success("🎵 A music world! That sounds fascinating! Let's shape it into something magical together.")
        elif any(word in inspiration_lower for word in ["dream", "sleep", "night"]):
            st.success("💭 A dream world! That sounds fascinating! Let's shape it into something magical together.")
        else:
            st.success("✨ Ooooh, that sounds fascinating! Let's shape it into something magical together.")

    # --- Environment / Setting ---
    st.markdown("### 🌍 Environment / Setting")
    st.markdown("**Where does your world take place? Think big: forest canopy, underwater palace, moonlit garden…**")

    # Add random button above input
    if st.button("🎲 Random Environment", key="random_environment"):
        random_envs = [
            "a floating island in the sky", "underwater palace", "forest canopy", "moonlit garden", "crystal caves", "ancient ruins", "desert oasis", "city of clouds", "volcanic fortress"
        ]
        st.session_state["world_environment"] = random.choice(random_envs)
        st.rerun()
    
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
            st.success("☁️ I can already picture it! A floating world is full of wonder and potential.")
        elif any(word in environment_lower for word in ["underwater", "ocean", "sea", "water"]):
            st.success("🌊 I can already picture it! An underwater world is full of wonder and potential.")
        elif any(word in environment_lower for word in ["forest", "tree", "nature"]):
            st.success("🌳 I can already picture it! A forest world is full of wonder and potential.")
        elif any(word in environment_lower for word in ["garden", "flower", "plant"]):
            st.success("🌸 I can already picture it! A garden world is full of wonder and potential.")
        else:
            st.success("🏞️ I can already picture it! That setting is full of wonder and potential.")

    # --- Mood / Vibe ---
    st.markdown("### 🎭 Mood / Vibe")
    st.markdown("**What kind of mood does your world have? Cozy? Mysterious? Epic? Peaceful?**")

    # Add random button above input
    if st.button("🎲 Random Mood", key="random_mood"):
        random_moods = [
            "serene and dreamlike", "cozy and warm", "mysterious and dark", "epic and adventurous", "whimsical and playful", "melancholic and nostalgic", "tense and suspenseful", "romantic and hopeful"
        ]
        st.session_state["world_mood"] = random.choice(random_moods)
        st.rerun()
    
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
            st.success("🧘 Such a beautiful mood! This world is going to feel unforgettable.")
        elif any(word in mood_lower for word in ["cozy", "warm", "comfortable", "homey"]):
            st.success("🏠 Such a beautiful mood! This world is going to feel unforgettable.")
        elif any(word in mood_lower for word in ["mysterious", "dark", "enigmatic", "secret"]):
            st.success("🔮 Such a beautiful mood! This world is going to feel unforgettable.")
        elif any(word in mood_lower for word in ["epic", "adventurous", "heroic", "grand"]):
            st.success("⚔️ Such a beautiful mood! This world is going to feel unforgettable.")
        else:
            st.success("💫 Such a beautiful mood! This world is going to feel unforgettable.")

    # --- Magical Rule or Twist ---
    st.markdown("### 🧬 Magical Rule or Twist")
    st.markdown("**Is there something unique or magical about this world? Something that bends reality?**")

    # Add random button above input
    if st.button("🎲 Random Magic", key="random_magic"):
        random_magics = [
            "time flows backward at sunset", "gravity works sideways", "memories become physical objects", "everyone can talk to animals", "dreams shape the landscape", "music controls the weather", "secrets are visible as glowing runes", "people swap bodies at midnight"
        ]
        st.session_state["world_magic"] = random.choice(random_magics)
        st.rerun()
    
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
            st.success("⏰ Whoa… that's such a cool twist! Your world just got even more unique.")
        elif any(word in magic_lower for word in ["gravity", "float", "fall", "weight"]):
            st.success("🌌 Whoa… that's such a cool twist! Your world just got even more unique.")
        elif any(word in magic_lower for word in ["memory", "remember", "forget", "mind"]):
            st.success("🧠 Whoa… that's such a cool twist! Your world just got even more unique.")
        else:
            st.success("🌀 Whoa… that's such a cool twist! Your world just got even more unique.")

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
            st.success("📚 Great choice! Your Sekai will have a warm, reflective vibe with that genre.")
        elif "Fantasy" in genre_names:
            st.success("🧙‍♀️ Great choice! Your Sekai will have a magical, wondrous vibe with that genre.")
        elif "Sci-Fi" in genre_names:
            st.success("🚀 Great choice! Your Sekai will have a futuristic, innovative vibe with that genre.")
        elif "Romance" in genre_names:
            st.success("💕 Great choice! Your Sekai will have a heartfelt, emotional vibe with that genre.")
        else:
            st.success("🌟 Great choice! Your Sekai will have an amazing vibe with that genre.")

    # --- AI Generate World Details Button ---
    st.markdown("---")
    if st.button("🤖 AI: Generate Your World Details", key="ai_generate_world_details", type="primary"):
        # Get all the guided creation information
        world_inspiration = st.session_state.get("world_inspiration", "")
        world_environment = st.session_state.get("world_environment", "")
        world_mood = st.session_state.get("world_mood", "")
        world_magic = st.session_state.get("world_magic", "")
        world_genres = st.session_state.get("world_genre", [])
        
        # Safety check for genres
        if not isinstance(world_genres, list):
            world_genres = []
        
        if not (world_inspiration.strip() or world_environment.strip() or world_mood.strip() or world_magic.strip()):
            st.warning("Please fill in at least one of the guided creation fields above before generating world details.")
        else:
            # Build a comprehensive prompt with all available world information
            genre_str = ', '.join([g.split(' ', 1)[0] for g in world_genres if g]) if world_genres else 'Fantasy'
            
            prompt = f"""Generate world details for a Sekai world based on the following information:

Inspiration: {world_inspiration}
Environment: {world_environment}
Mood: {world_mood}
Magical Rule: {world_magic}
Genre: {genre_str}

Create:
1. A compelling world title (2-4 words)
2. A detailed world setting description (2-3 sentences)
3. Relevant keywords (3-5 words separated by commas)

The world details should:
- Be cohesive and fit together naturally
- Be engaging and imaginative
- Match the genre and mood specified
- Incorporate the magical elements if provided
- Feel like a complete, immersive world

Respond in this format:
Title: <world title>
Setting: <detailed setting description>
Keywords: <comma-separated keywords>"""
            
            try:
                response = model.generate_content(prompt)
                generated_world = response.text.strip()
                
                # Parse the response
                title_match = re.search(r'Title\s*[:：\-]\s*(.*)', generated_world)
                setting_match = re.search(r'Setting\s*[:：\-]\s*(.*)', generated_world)
                keywords_match = re.search(r'Keywords\s*[:：\-]\s*(.*)', generated_world)
                
                if title_match:
                    st.session_state['world_title'] = title_match.group(1).strip()
                if setting_match:
                    st.session_state['world_setting'] = setting_match.group(1).strip()
                if keywords_match:
                    st.session_state['world_keywords_input'] = keywords_match.group(1).strip()
                
                st.success("🌟 World details generated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to generate world details: {e}")

    # --- Sekai World Details (ALWAYS VISIBLE) ---
    st.markdown("---")
    st.markdown("### 🌟 Your Sekai World Details")
    st.markdown("**Review and edit your world details below, or use the guided creation above:**")
    if 'world_title' not in st.session_state:
        st.session_state['world_title'] = ''
    world_title = st.text_input(
        "Sekai Title",
        value=st.session_state['world_title'],
        key="world_title_display"
    )
    if 'world_setting' not in st.session_state:
        st.session_state['world_setting'] = ''
    world_setting = st.text_area(
        "Describe the World Setting",
        value=st.session_state['world_setting'],
        key="world_setting_display"
    )
    if 'world_keywords_input' not in st.session_state:
        st.session_state['world_keywords_input'] = ''
    world_keywords = st.text_input(
        "Keywords",
        value=st.session_state['world_keywords_input'],
        key="world_keywords_display"
    )
    if world_title.strip() or world_setting.strip():
        st.markdown('<div class="feedback-animation">🌟 <span class="emoji-sparkle">Your world is taking shape!</span> Ready to move to the next step!</div>', unsafe_allow_html=True)

    # ===== STEP 2: CREATE YOUR CHARACTER (YOU IN THE WORLD) =====
    st.markdown("## 👤 Step 2: Create Your Character")
    st.markdown('<div id="step-2"></div>', unsafe_allow_html=True)
    st.info("Now let's meet you! You'll be the heart of this world, so tell us about yourself.")

    # --- AI Character Generation Button ---
    if st.button("✨ AI: Generate My Character", key="ai_generate_player_char", type="primary"):
        # Get complete world information from Step 1
        world_title = st.session_state.get('world_title', '')
        world_setting = st.session_state.get('world_setting', '')
        world_keywords = st.session_state.get('world_keywords_input', '')
        world_genres = st.session_state.get('world_genre', [])
        
        # Safety check for genres
        if not isinstance(world_genres, list):
            world_genres = []
        
        if not (world_title and world_setting):
            st.warning("Please complete Step 1 (Sekai World) before generating your character.")
        else:
            # Build a comprehensive prompt with all available world information
            genre_str = ', '.join([g.split(' ', 1)[0] for g in world_genres if g]) if world_genres else 'Fantasy'
            world_context = f"Title: {world_title}\nSetting: {world_setting}"
            if world_keywords:
                world_context += f"\nKeywords: {world_keywords}"
            
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
            valid = False
            if name and traits:
                clean_name = strip_stars(name.group(1))
                clean_traits = strip_stars(traits.group(1))
                if clean_name and clean_traits and not clean_name.lower().startswith("let's craft"):
                    st.session_state['user_name_input'] = clean_name
                    st.session_state['user_traits_input'] = clean_traits
                    valid = True
            if not valid:
                st.error("AI could not generate a valid character. Please check your world info in Step 1 and try again.")
            else:
                st.rerun()

    # --- Character Name ---
    if 'user_name_input' not in st.session_state:
        st.session_state['user_name_input'] = ''
    
    user_name = st.text_input(
        "Your Character's Name",
        value=st.session_state['user_name_input'],
        key="user_name_input"
    )

    # --- Character Traits ---
    if 'user_traits_input' not in st.session_state:
        st.session_state['user_traits_input'] = ''
    
    user_traits = st.text_area(
        "Your Character's Traits",
        value=st.session_state['user_traits_input'],
        key="user_traits_input"
    )
    
    if user_traits.strip():
        st.success("🌟 Perfect! You're going to be the heart of this world.")

    st.markdown("---")

    # ===== STEP 3: CREATE MAIN CHARACTERS =====
    st.markdown("## 👥 Step 3: Create Main Characters")
    st.markdown('<div id="step-3"></div>', unsafe_allow_html=True)
    st.info("Now let's meet the other characters who will join your story!")

    # Get values from previous steps
    world_title = st.session_state.get("world_title", "Your Sekai World")
    world_setting = st.session_state.get("world_setting", "A magical world")
    world_keywords = st.session_state.get("world_keywords_input", "")
    world_genres = st.session_state.get("world_genre", [])
    
    # Safety check for genres
    if not isinstance(world_genres, list):
        world_genres = []
    
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
            # Safety check for genres
            if not isinstance(world_genres, list):
                world_genres = []
            genre_str = ', '.join([g.split(' ', 1)[0] for g in world_genres if g]) if world_genres else 'Fantasy'
            world_context = f"World: {world_setting}\nTitle: {world_title}\nGenre: {genre_str}"
            if world_keywords:
                world_context += f"\nKeywords: {world_keywords}"
            
            # Generate each character individually based on their idea
            for i in range(num_characters):
                # Get the character idea for this specific character
                character_idea = st.session_state.get(f"idea_{i}", "").strip()
                
                # Build existing characters list (excluding current character)
                other_chars = []
                for j in range(num_characters):
                    if j != i:  # Skip the current character being generated
                        char_name = st.session_state.get(f"name_{j}", "")
                        char_role = st.session_state.get(f"role_{j}", "")
                        char_traits = st.session_state.get(f"trait_{j}", "")
                        char_voice = st.session_state.get(f"voice_style_{j}", "")
                        char_relationship = st.session_state.get(f"relationship_{j}", "")
                        if char_name and char_traits:  # Only include characters that have been generated
                            char_info = f"- {char_name} ({char_role}): {char_traits}"
                            if char_voice and char_voice != "Default":
                                char_info += f" | Voice: {char_voice}"
                            if char_relationship and char_relationship.strip():
                                char_info += f" | Relationship: {char_relationship}"
                            other_chars.append(char_info)
                
                existing_chars_text = "\n".join(other_chars) if other_chars else "None"
                
                # Create prompt based on whether character idea exists
                if character_idea:
                    prompt = f"""Create a new character for the following world:

{world_context}

Player Character: {user_name} ({user_traits})

Character Idea: {character_idea}

Existing Characters:
{existing_chars_text}

Create a character that:
- Incorporates the character idea: {character_idea}
- Is clearly different from the player character and any existing characters
- Would naturally exist in this world
- Has an interesting personality and abilities
- Could interact meaningfully with the player character
- Fits the genre and tone of the world

Respond in this format:
Name: <A standard first name and optional last name only, no titles or descriptions>
Role: <Character Role>
Traits: <Personality traits and special abilities>
Voice Style: <How do they speak?>
Relationship: <How do they relate to the player character? Are they friends, rivals, mentors, etc.?>"""
                else:
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
Traits: <Personality traits and special abilities>
Voice Style: <How do they speak?>
Relationship: <How do they relate to the player character? Are they friends, rivals, mentors, etc.?>"""
                
                try:
                    result = generate_field(prompt)
                    # Parse the result
                    parsed_name, parsed_role, parsed_traits, parsed_voice, parsed_relationship = "", "", "", "", ""
                    try:
                        # Use regex for robust parsing
                        name_match = re.search(r'Name\s*[:：\-]\s*(.*)', result)
                        role_match = re.search(r'Role\s*[:：\-]\s*(.*)', result)
                        traits_match = re.search(r'Traits?\s*[:：\-]\s*(.*)', result)
                        voice_match = re.search(r'Voice Style\s*[:：\-]\s*(.*)', result)
                        relationship_match = re.search(r'Relationship\s*[:：\-]\s*(.*)', result)
                        if name_match:
                            parsed_name = name_match.group(1).strip()
                        if role_match:
                            parsed_role = role_match.group(1).strip()
                        if traits_match:
                            parsed_traits = traits_match.group(1).strip()
                        if voice_match:
                            parsed_voice = voice_match.group(1).strip()
                        if relationship_match:
                            parsed_relationship = relationship_match.group(1).strip()
                    except Exception:
                        pass
                    
                    # Store parsed fields in session state
                    st.session_state[f"char_{i}"] = result
                    st.session_state[f"name_{i}"] = parsed_name
                    st.session_state[f"role_{i}"] = parsed_role
                    st.session_state[f"trait_{i}"] = parsed_traits
                    st.session_state[f"voice_style_{i}"] = parsed_voice
                    st.session_state[f"relationship_{i}"] = parsed_relationship
                    
                    # Also update the input field values
                    st.session_state[f"name_input_{i}"] = parsed_name
                    st.session_state[f"role_input_{i}"] = parsed_role
                    st.session_state[f"trait_input_{i}"] = parsed_traits
                    st.session_state[f"voice_input_{i}"] = parsed_voice
                    st.session_state[f"relationship_input_{i}"] = parsed_relationship
                    
                    # Increment generation counter to force form refresh
                    current_gen_count = st.session_state.get(f"gen_count_{i}", 0)
                    st.session_state[f"gen_count_{i}"] = current_gen_count + 1
                    
                    # Show success message
                    st.success(f"✅ Character {i+1} generated successfully! The form below has been updated.")
                except Exception as e:
                    st.error(f"Failed to generate character {i+1}: {e}")
                    # Set empty values if generation fails
                    st.session_state[f"char_{i}"] = ""
                    st.session_state[f"name_{i}"] = ""
                    st.session_state[f"role_{i}"] = ""
                    st.session_state[f"trait_{i}"] = ""
                    st.session_state[f"voice_style_{i}"] = ""
                    st.session_state[f"relationship_{i}"] = ""
            
            st.success(f"✅ All {num_characters} characters generated successfully!")
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
                if not idea.strip():
                    st.warning(f"Please enter a character idea for Character {i+1} before generating.")
                else:
                    with st.spinner(f"Generating Character {i+1}..."):
                        # Get complete world and user information
                        world_genres = st.session_state.get("world_genre", [])
                        # Safety check for genres
                        if not isinstance(world_genres, list):
                            world_genres = []
                        genre_str = ', '.join([g.split(' ', 1)[0] for g in world_genres if g]) if world_genres else 'Fantasy'
                        world_context = f"World: {world_setting}\nTitle: {world_title}\nGenre: {genre_str}"
                        if world_keywords:
                            world_context += f"\nKeywords: {world_keywords}"
                        
                        other_chars = []
                        for j in range(num_characters):
                            if j != i:  # Skip the current character being generated
                                char_name = st.session_state.get(f"name_{j}", "")
                                char_role = st.session_state.get(f"role_{j}", "")
                                char_traits = st.session_state.get(f"trait_{j}", "")
                                char_voice = st.session_state.get(f"voice_style_{j}", "")
                                char_relationship = st.session_state.get(f"relationship_{j}", "")
                                if char_name and char_traits:  # Only include characters that have been generated
                                    char_info = f"- {char_name} ({char_role}): {char_traits}"
                                    if char_voice and char_voice != "Default":
                                        char_info += f" | Voice: {char_voice}"
                                    if char_relationship and char_relationship.strip():
                                        char_info += f" | Relationship: {char_relationship}"
                                    other_chars.append(char_info)
                
                        existing_chars_text = "\n".join(other_chars) if other_chars else "None"
                        
                        prompt = f"""Create a new character for the following world:

{world_context}

Player Character: {user_name} ({user_traits})

Character Idea: {idea}

Existing Characters:
{existing_chars_text}

Create a character that:
- Incorporates the character idea: {idea}
- Is clearly different from the player character and any existing characters
- Would naturally exist in this world
- Has an interesting personality and abilities
- Could interact meaningfully with the player character
- Fits the genre and tone of the world

Respond in this format:
Name: <A standard first name and optional last name only, no titles or descriptions>
Role: <Character Role>
Traits: <Personality traits and special abilities>
Voice Style: <How do they speak?>
Relationship: <How do they relate to the player character? Are they friends, rivals, mentors, etc.?>"""
                        
                        try:
                            result = generate_field(prompt)
                            # Parse the result
                            parsed_name, parsed_role, parsed_traits, parsed_voice, parsed_relationship = "", "", "", "", ""
                            try:
                                # Use regex for robust parsing
                                name_match = re.search(r'Name\s*[:：\-]\s*(.*)', result)
                                role_match = re.search(r'Role\s*[:：\-]\s*(.*)', result)
                                traits_match = re.search(r'Traits?\s*[:：\-]\s*(.*)', result)
                                voice_match = re.search(r'Voice Style\s*[:：\-]\s*(.*)', result)
                                relationship_match = re.search(r'Relationship\s*[:：\-]\s*(.*)', result)
                                if name_match:
                                    parsed_name = name_match.group(1).strip()
                                if role_match:
                                    parsed_role = role_match.group(1).strip()
                                if traits_match:
                                    parsed_traits = traits_match.group(1).strip()
                                if voice_match:
                                    parsed_voice = voice_match.group(1).strip()
                                if relationship_match:
                                    parsed_relationship = relationship_match.group(1).strip()
                            except Exception:
                                pass
                            
                            # Only update this specific character's data
                            st.session_state[f"char_{i}"] = result
                            st.session_state[f"name_{i}"] = parsed_name
                            st.session_state[f"role_{i}"] = parsed_role
                            st.session_state[f"trait_{i}"] = parsed_traits
                            st.session_state[f"voice_style_{i}"] = parsed_voice
                            st.session_state[f"relationship_{i}"] = parsed_relationship
                            
                            # Also update the input field values
                            st.session_state[f"name_input_{i}"] = parsed_name
                            st.session_state[f"role_input_{i}"] = parsed_role
                            st.session_state[f"trait_input_{i}"] = parsed_traits
                            st.session_state[f"voice_input_{i}"] = parsed_voice
                            st.session_state[f"relationship_input_{i}"] = parsed_relationship
                            
                            # Increment generation counter to force form refresh
                            current_gen_count = st.session_state.get(f"gen_count_{i}", 0)
                            st.session_state[f"gen_count_{i}"] = current_gen_count + 1
                            
                            # Show success message
                            st.success(f"✅ Character {i+1} generated successfully! The form below has been updated.")
                        except Exception as e:
                            st.error(f"Failed to generate character {i+1}: {e}")
        
        # Parse generated character
        default_text = st.session_state.get(f"char_{i}", "")
        parsed_name = st.session_state.get(f"name_{i}", "")
        parsed_role = st.session_state.get(f"role_{i}", "")
        parsed_traits = st.session_state.get(f"trait_{i}", "")
        parsed_voice = st.session_state.get(f"voice_style_{i}", "")
        parsed_relationship = st.session_state.get(f"relationship_{i}", "")

        # Character Details
        # Use a unique key that changes when character is generated to force refresh
        generation_key = st.session_state.get(f"gen_count_{i}", 0)
        
        # Get the current values from session state, with fallback to stored values
        current_name = st.session_state.get(f"name_input_{i}", st.session_state.get(f"name_{i}", parsed_name))
        current_role = st.session_state.get(f"role_input_{i}", st.session_state.get(f"role_{i}", parsed_role))
        current_traits = st.session_state.get(f"trait_input_{i}", st.session_state.get(f"trait_{i}", parsed_traits))
        current_voice = st.session_state.get(f"voice_input_{i}", st.session_state.get(f"voice_style_{i}", parsed_voice))
        current_relationship = st.session_state.get(f"relationship_input_{i}", st.session_state.get(f"relationship_{i}", parsed_relationship))
        
        name = st.text_input(f"Name {i+1}", key=f"name_input_{i}", value=current_name)
        role = st.text_input(f"Role {i+1}", key=f"role_input_{i}", value=current_role, placeholder="Librarian who hides a secret / Rival time mage")
        trait = st.text_area(f"Key Traits {i+1}", key=f"trait_input_{i}", value=current_traits, height=100, placeholder="Describe their personality, abilities, and backstory...")
        relationship = st.text_area(
            f"Relationship with {user_name}",
            value=current_relationship,
            key=f"relationship_input_{i}",
            placeholder="Close childhood friend who always looks out for you / Mysterious rival who challenges your beliefs / Wise mentor who guides your journey",
            height=80
        )
        
        # Optional Add-ons
        with st.expander(f"🌟 Optional Add-ons for Character {i+1}", expanded=False):
            voice_style = st.text_input(
                f"Voice Style",
                value=current_voice,
                key=f"voice_input_{i}"
            )
        
        # Sync the form values back to session state for persistence
        st.session_state[f"name_{i}"] = name
        st.session_state[f"role_{i}"] = role
        st.session_state[f"trait_{i}"] = trait
        st.session_state[f"relationship_{i}"] = relationship
        st.session_state[f"voice_style_{i}"] = voice_style if 'voice_style' in locals() else "Default"
        
        characters.append({
            "name": name, 
            "role": role, 
            "traits": trait,
            "relationship": relationship,
            "voice_style": voice_style if 'voice_style' in locals() else "Default"
        })

    st.markdown("---")

    # ===== STEP 4: GENERATE SEKAI STORY TEMPLATE =====
    st.markdown("---")
    st.markdown("### 📜 Step 4: Generate Sekai Story Template")
    st.markdown('<div id="step-4"></div>', unsafe_allow_html=True)
    st.info("Let's bring everything together and create your story template!")

    # Opening Line Setup
    st.markdown("### 💬 Opening Scene Setup")
    st.markdown("**💡 Tip:** This will be the first scene of your story!")
    
    # Initialize session state for opening scene
    if "opening_scene_input" not in st.session_state:
        st.session_state["opening_scene_input"] = ""
    
    col1, col2 = st.columns([3, 1])
    with col1:
        # AI button is now above the text area
        if st.button("✨ AI: Generate Opening Scene", key="generate_opening_scene"):
            with st.spinner("Creating an engaging opening scene..."):
                char_list = f"Player: {user_name} ({user_traits})\n"
                for c in characters:
                    char_list += f"- {c['name']} ({c['role']}): {c['traits']}"
                    if c.get('relationship'):
                        char_list += f" | Relationship: {c['relationship']}"
                    char_list += "\n"
                
                # Get advanced settings for opening scene generation
                story_tone = st.session_state.get("story_tone", "Balanced")
                pacing = st.session_state.get("pacing", "Balanced")
                pov = st.session_state.get("pov", "Third person")
                narration_style = st.session_state.get("narration_style", "Balanced")
                
                prompt = f"""
Generate an engaging opening scene for an interactive story.

World Information:
- Title: {world_title}
- Setting: {world_setting}
- Keywords: {world_keywords}
- Genre: {', '.join(selected_genres) if selected_genres and isinstance(selected_genres, list) else 'Fantasy'}

Story Style:
- Tone: {story_tone}
- Pacing: {pacing}
- Point of View: {pov}
- Narration Style: {narration_style}

Characters:
{char_list}

Create a vivid opening scene that:
- Introduces the world and setting
- Establishes the player character's situation
- Hints at the story to come
- Is 2-3 sentences maximum
- Feels immersive and engaging
- Matches the story tone: {story_tone}
- Uses appropriate pacing: {pacing}
- Written from the specified point of view: {pov}
- Applies the narration style: {narration_style}

Generate only the opening scene description, nothing else.
"""
                try:
                    response = model.generate_content(prompt)
                    generated_opening = response.text.strip()
                    if generated_opening.startswith('"') and generated_opening.endswith('"'):
                        generated_opening = generated_opening[1:-1]
                    st.session_state["opening_scene_input"] = generated_opening
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to generate opening scene: {e}")
        opening_scene = st.text_area(
            "Describe the opening scene (optional - leave blank for AI generation)",
            value=st.session_state["opening_scene_input"],
            placeholder="You wake up in a mysterious library at midnight... / The city streets are filled with floating dreams...",
            height=100,
            key="opening_scene_input"
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
            st.info(f"Using {len(characters)} characters from Step 3")
            
            # Build comprehensive character information including relationships
            character_details = []
            for c in characters:
                if c['name'].strip() and c['traits'].strip():
                    char_info = f"- {c['name']} ({c['role']}): {c['traits']}"
                    if c.get('relationship') and c['relationship'].strip():
                        char_info += f" | Relationship: {c['relationship']}"
                    if c.get('voice_style') and c['voice_style'] != "Default":
                        char_info += f" | Voice: {c['voice_style']}"
                    character_details.append(char_info)
            
            prompt = f"""
You are an AI for building JSON-based interactive stories.
Generate a story JSON with: title, setting, genre, keywords, characters (array of name, role, description, voice_style, relationship), openingScene, storyTone, pacing, pointOfView, and narrationStyle.

Title: {world_title}
Setting: {world_setting}
Genre: {', '.join(selected_genres) if selected_genres and isinstance(selected_genres, list) else 'Fantasy'}
Keywords: {world_keywords}
Characters:
- {user_name} (Player): {user_traits}
"""
            for char_detail in character_details:
                prompt += f"{char_detail}\n"
            
            # Add opening scene if provided
            if opening_scene.strip():
                prompt += f"\nOpening Scene: {opening_scene}\n"
            
            # Add advanced settings to prompt and specify they should be included in JSON
            prompt += "\nAdvanced Settings (include these as JSON fields):\n"
            prompt += f"storyTone: {story_tone}\n"
            prompt += f"pacing: {pacing}\n"
            prompt += f"pointOfView: {pov}\n"
            prompt += f"narrationStyle: {narration_style}\n"
            
            prompt += "\nIMPORTANT: Include the COMPLETE relationship text for each character in the JSON, not just a summary. Preserve all the relationship details exactly as provided."
            prompt += "\nRespond with raw JSON only. Do NOT include a 'choices' field in the JSON. The player character should NOT have a voice_style or relationship field. Include all the advanced settings fields in the JSON output."

            response = model.generate_content(prompt)
            output = response.text.strip()

            if output.startswith("```json"):
                output = output.replace("```json", "").strip()
            if output.endswith("```"):
                output = output[:-3].strip()

            try:
                sekai_json = json.loads(output)
                # Remove 'choices' if present
                if 'choices' in sekai_json:
                    del sekai_json['choices']
                # Remove 'voice_style' and 'relationship' from player (assume first character is player)
                if 'characters' in sekai_json and len(sekai_json['characters']) > 0:
                    if 'voice_style' in sekai_json['characters'][0]:
                        del sekai_json['characters'][0]['voice_style']
                    if 'relationship' in sekai_json['characters'][0]:
                        del sekai_json['characters'][0]['relationship']
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
    world_title = st.session_state.get("world_title", "Your Sekai World")
    
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
            # Get advanced settings from the JSON template
            sekai_json = st.session_state['sekai_json']
            story_tone = sekai_json.get('storyTone', 'Balanced')
            pacing = sekai_json.get('pacing', 'Balanced')
            point_of_view = sekai_json.get('pointOfView', 'Third person')
            narration_style = sekai_json.get('narrationStyle', 'Balanced')
            
            story_prompt = f"""
You are an interactive fiction narrator for a visual novel.
Begin the story using the following JSON world structure.

Story Style Guidelines:
- Tone: {story_tone}
- Pacing: {pacing}
- Point of View: {point_of_view}
- Narration Style: {narration_style}

CRITICAL FORMATTING RULES:
- Write in visual novel script format
- Use this exact format for each line:
  narrator description of what happens (no quotes, no italics)
  CharacterName (expression/mood) "dialogue or thoughts"
- Keep narrator descriptions short and concise
- Maintain consistent character voices and personalities
- Do NOT write dialogue or thoughts for the player character
- End with: **What do you do?**

CONTENT GUIDELINES:
- Introduce the world and setting vividly but concisely
- Establish the player character's situation
- Introduce at least one other character from the JSON
- Keep the opening engaging but not overwhelming
- Match the story tone: {story_tone}
- Use the specified pacing: {pacing}
- Write from the specified point of view: {point_of_view}
- Apply the narration style: {narration_style}

MEMORY REQUIREMENTS:
- Remember the complete story template and all character details
- Set up character relationships and story elements for future interactions
- Ensure character expressions and moods match their personalities from the template

JSON:
{json.dumps(st.session_state['sekai_json'], indent=2)}

Write the opening scene below in proper visual novel script format:
"""
            try:
                first_turn = model.generate_content(story_prompt).text.strip()

                if first_turn.startswith("{") or first_turn.startswith('"title"'):
                    st.error("Model returned raw JSON instead of story text. Please retry.")
                else:
                    # Clean up the initial story response
                    cleaned_first_turn = clean_story_response(first_turn)
                    
                    st.session_state["game_state"] = [cleaned_first_turn]
                    st.session_state["story_colors"] = [random.choice(["#fce4ec", "#e3f2fd", "#e8f5e9", "#fff8e1", "#ede7f6"])]
                    st.session_state["user_inputs"] = [""]
                    st.rerun()
            except Exception as e:
                st.error(f"Error starting the game: {e}")
                # Fallback opening
                fallback_opening = f'narrator Welcome to {sekai_json.get("title", "your adventure")}!\nnarrator The story begins...\n**What do you do?**'
                st.session_state["game_state"] = [fallback_opening]
                st.session_state["story_colors"] = [random.choice(["#fce4ec", "#e3f2fd", "#e8f5e9", "#fff8e1", "#ede7f6"])]
                st.session_state["user_inputs"] = [""]
                st.rerun()

    # --- Game UI (only appears after game starts) ---
    if "game_state" in st.session_state:
        st.markdown("---")
        st.subheader("🚀 Game In Progress")

        for i, (block, user_input) in enumerate(zip(st.session_state["game_state"], st.session_state["user_inputs"])):
            color = st.session_state.get("story_colors", ["#e3f2fd"])[i % len(st.session_state["story_colors"])]
            user_reply_html = f'<p style="margin-bottom:8px; padding:4px; background-color:#f0f0f0; border-radius:4px;"><b>You:</b> {user_input}</p>' if user_input.strip() else ""

            # Enhanced formatting for better readability
            formatted_block = format_story_block(block)

            st.markdown(
                f'<div style="background-color:{color}; padding:15px; border-radius:10px; margin-bottom:15px; box-shadow:0 2px 4px rgba(0,0,0,0.1)">{user_reply_html}{formatted_block}</div>',
                unsafe_allow_html=True,
            )

        # Game input (only appears when game is active)
        st.markdown("### 🎮 Your Turn")
        
        # Generate 3 choice options
        choices = generate_choices()
        
        # Display choice buttons vertically with full description
        st.markdown("**Choose an action or write your own:**")
        for idx, choice in enumerate(choices):
            btn_label = f"Choice {idx+1}: {choice}"
            if st.button(btn_label, key=f"choice_{idx+1}_{len(st.session_state['game_state'])}", on_click=handle_choice_click, args=(choice,)):
                pass
        
        # Freeform input
        st.markdown("**Or write your own action/dialogue:**")
        st.text_input("Enter your next action or dialogue", key="reply_input")
        st.button("Send", on_click=handle_send)

    # Footer
    st.caption("Built by Claire Wang for the Sekai PM Take-Home Project ✨")
    
    st.stop()

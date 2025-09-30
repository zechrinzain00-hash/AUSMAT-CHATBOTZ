import streamlit as st
import random
import time

# --- 1. CONFIGURATION: Element Theme Mapping ---

# Note: Only the 'Fire' theme colors will be used for the entire app now.
ELEMENT_THEMES = {
    "Fire": {"color": "#FF4500", "background": "#FFF0E0"},      # Orange/Red (Used Globally)
    "Water": {"color": "#1E90FF", "background": "#E0F7FF"},     
    "Earth": {"color": "#8B4513", "background": "#F0EAD6"},     
    "Wind": {"color": "#3CB371", "background": "#E6FFF0"},      
    "Lightning": {"color": "#FFD700", "background": "#FFFFE0"},  
}

# The public URL for the background music. REPLACE THIS.
LAUFEY_MUSIC_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

# URL for the new fire background image. REPLACE THIS with a different image if you like!
FIRE_BACKGROUND_URL = "https://images.unsplash.com/photo-1549419149-a2e63327d620?q=80&w=2940&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" 

# --- 2. STATIC QUIZ DATA (Anime Trivia: Naruto, JJK, AoT, One Piece, Dandadan) ---

STATIC_QUIZ_DATA = [
    {"question": "What is the name of the tailed beast sealed inside Naruto Uzumaki?", "options": ["Nine-Tails", "Eight-Tails", "Six-Tails", "Seven-Tails"], "correctIndex": 0, "element": "Fire"},
    {"question": "What is the name of Luffy's signature attack, typically used to stretch his limbs?", "options": ["Gum-Gum Pistol", "Gum-Gum Bazooka", "Gum-Gum Whip", "Gum-Gum Rocket"], "correctIndex": 0, "element": "Water"},
    {"question": "What organization is Levi Ackerman the captain of?", "options": ["Military Police", "Garrison Regiment", "Scout Regiment", "Royal Guard"], "correctIndex": 2, "element": "Wind"},
    {"question": "What cursed technique allows Gojo Satoru to manipulate space and distance?", "options": ["Limitless", "Cursed Speech", "Ten Shadows Technique", "Idle Transfiguration"], "correctIndex": 0, "element": "Lightning"},
    {"question": "Who is known as the Copy Ninja, famous for using the Sharingan?", "options": ["Kakashi Hatake", "Sasuke Uchiha", "Itachi Uchiha", "Jiraiya"], "correctIndex": 0, "element": "Lightning"},
    {"question": "Before Franky, who was the shipwright of the Going Merry?", "options": ["Usopp", "Zoro", "Koby", "Nobody"], "correctIndex": 3, "element": "Earth"},
    {"question": "What kind of creature possesses Momo Ayase's grandmother, Seiko, in Dandadan?", "options": ["A Space Alien", "A Cryptid", "A Spirit", "A Yōkai"], "correctIndex": 3, "element": "Earth"},
    {"question": "What protective wall surrounds the innermost capital district in Attack on Titan?", "options": ["Wall Maria", "Wall Sina", "Wall Rose", "Wall Titans"], "correctIndex": 1, "element": "Earth"},
    {"question": "What is Yuji Itadori's main goal after becoming Sukuna's vessel in Jujutsu Kaisen?", "options": ["Become a curse", "Save his friends", "Find all Sukuna's fingers", "Die a good death"], "correctIndex": 3, "element": "Fire"},
    {"question": "What is the protagonist Ken Takakura's nickname in Dandadan?", "options": ["Okarun", "Ayase", "Turbo Granny", "Alien Boy"], "correctIndex": 0, "element": "Water"},
    {"question": "What type of devil fruit did Tony Tony Chopper eat in One Piece?", "options": ["Dog-Dog Fruit", "Human-Human Fruit", "Animal-Animal Fruit", "Heal-Heal Fruit"], "correctIndex": 1, "element": "Earth"},
    {"question": "What is the name of the leaf village's head leader in Naruto?", "options": ["Hokage", "Kazekage", "Mizukage", "Raikage"], "correctIndex": 0, "element": "Fire"},
    {"question": "What is the special ability of the Armored Titan in Attack on Titan?", "options": ["Hardening", "Regeneration", "Speed", "Invisibility"], "correctIndex": 0, "element": "Earth"},
    {"question": "What is the name of Sanji's cooking technique where his leg bursts into flames?", "options": ["Diable Jambe", "Hell Memories", "Sky Walk", "Blue Walk"], "correctIndex": 0, "element": "Fire"},
    {"question": "What technique allows Naruto to create solid clones of himself?", "options": ["Shadow Clone Jutsu", "Substitution Jutsu", "Transformation Jutsu", "Rasengan"], "correctIndex": 0, "element": "Wind"},
]

MAX_QUESTIONS = len(STATIC_QUIZ_DATA)

# --- 3. State Initialization and Utilities ---

def init_state():
    """Initializes session state variables for the quiz game."""
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.current_quiz = []
        st.session_state.selected_option = None
        st.session_state.answer_revealed = False
        st.session_state.num_questions = 5

init_state()

def reset_quiz_state():
    """Resets all relevant session state variables to return to setup."""
    st.session_state.quiz_started = False
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.current_quiz = []
    st.session_state.selected_option = None
    st.session_state.answer_revealed = False

# --- 4. Core Game Functions ---

def start_quiz(num_questions):
    """Shuffles the data and starts a new quiz."""
    if num_questions > MAX_QUESTIONS:
        st.error(f"Cannot select more than {MAX_QUESTIONS} questions.")
        return
        
    random.shuffle(STATIC_QUIZ_DATA)
    st.session_state.current_quiz = STATIC_QUIZ_DATA[:num_questions]
    st.session_state.current_index = 0
    st.session_state.score = 0
    st.session_state.selected_option = None
    st.session_state.answer_revealed = False
    st.session_state.quiz_started = True

def check_answer(question, selected_index):
    """Checks the selected answer against the correct answer."""
    st.session_state.selected_option = selected_index
    
    if st.session_state.answer_revealed:
        # Prevent re-checking if already revealed
        return
        
    is_correct = question['correctIndex'] == selected_index
    if is_correct:
        st.session_state.score += 1
    
    st.session_state.answer_revealed = True
    time.sleep(0.01)

def next_question():
    """Moves to the next question or finishes the quiz."""
    if st.session_state.current_index < len(st.session_state.current_quiz) - 1:
        st.session_state.current_index += 1
        st.session_state.selected_option = None
        st.session_state.answer_revealed = False
    else:
        # Quiz is complete
        st.session_state.current_index += 1
        st.session_state.quiz_started = False 

# --- 5. Dynamic Theme Retrieval (Now always returns Fire) ---

def get_current_element_theme():
    """Retrieves the hardcoded Fire theme colors for a consistent look."""
    # Always return the Fire theme
    return ELEMENT_THEMES['Fire']


# --- 6. Streamlit UI Functions ---

def render_question():
    """Renders the current question, options, and check/next buttons."""
    if not st.session_state.current_quiz:
        return

    q_data = st.session_state.current_quiz[st.session_state.current_index]
    
    # Display Score and Progress
    st.info(f"Question {st.session_state.current_index + 1} of {len(st.session_state.current_quiz)} | Score: **{st.session_state.score}**")

    st.markdown(f"### {q_data['question']}")

    # Radio button key must change for each question to reset selection
    key_prefix = f"q_{st.session_state.current_index}"
    
    # Use st.radio for the selection mechanism
    selected_val = st.radio(
        label="Options",
        options=range(len(q_data['options'])),
        format_func=lambda i: q_data['options'][i],
        key=f"{key_prefix}_radio",
        index=None, # Ensure nothing is selected initially
        disabled=st.session_state.answer_revealed,
    )
    
    # Capture the selected option index from the radio widget
    if selected_val is not None:
        st.session_state.selected_option = selected_val
    
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        check_disabled = st.session_state.answer_revealed or st.session_state.selected_option is None
        
        # Check Answer Button
        st.button(
            "Check Answer", 
            on_click=check_answer, 
            args=(q_data, st.session_state.selected_option),
            disabled=check_disabled,
            type="primary"
        )

    with col2:
        next_disabled = not st.session_state.answer_revealed
        
        # Next Question Button (or Finish Quiz)
        button_label = "Next Question" if st.session_state.current_index < len(st.session_state.current_quiz) - 1 else "Finish Quiz"
        st.button(
            button_label, 
            on_click=next_question,
            disabled=next_disabled
        )
        
    # Feedback Display
    if st.session_state.answer_revealed:
        correct_index = q_data['correctIndex']
        if st.session_state.selected_option == correct_index:
            st.success("✅ Correct! You nailed that trivia point.")
        else:
            correct_answer = q_data['options'][correct_index]
            st.error(f"❌ Incorrect. The correct answer was: **{correct_answer}**.")
            
def render_quiz_setup():
    """Renders the initial setup screen for selecting question count."""
    st.markdown("## 😠 GrumpyQuest Setup")
    
    # New, prominent text
    st.markdown("## Ready to test your skill?")

    # Question Count Slider
    num_questions_slider = st.slider(
        "Number of Questions",
        min_value=1,
        max_value=MAX_QUESTIONS,
        value=st.session_state.num_questions,
        step=1
    )
    
    # Update state for the slider
    st.session_state.num_questions = num_questions_slider

    # Start Button
    if st.button("🚀 Start GrumpyQuest", type="primary"):
        start_quiz(st.session_state.num_questions)
        st.rerun()

def render_quiz_complete():
    """Renders the final results screen."""
    st.balloons()
    st.markdown("## 🏆 GrumpyQuest Complete! **Final Results**")
    
    final_score = st.session_state.score
    total_questions = len(st.session_state.current_quiz)
    percentage = (final_score / total_questions) * 100
    
    if percentage == 100:
        st.success(f"### 🎉 Perfect Score! {final_score}/{total_questions}")
        st.markdown("You are a walking encyclopedia of anime facts!")
    elif percentage >= 70:
        st.success(f"### Great Job! {final_score}/{total_questions}")
        st.markdown("Your knowledge of Shonen is strong!")
    else:
        st.warning(f"### Good Effort! {final_score}/{total_questions}")
        st.markdown("Keep training! There's more lore to discover.")

    if st.button("Start New Quiz", type="primary"):
        # Reset state and return to setup screen
        reset_quiz_state()
        st.rerun()

# --- 7. Main Application Flow ---

def main_app():
    """Controls the overall layout and flow of the application."""
    # Updated Page Title
    st.set_page_config(page_title="GrumpyQuest: Anime Trivia", layout="centered", initial_sidebar_state="collapsed")
    
    # --- Hidden Autoplay Music Injection ---
    # This injects a hidden <audio> tag with autoplay and loop attributes.
    audio_html = f"""
        <audio controls autoplay loop style="display:none;">
            <source src="{LAUFEY_MUSIC_URL}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)
    # --- END MUSIC INJECTION ---

    # --- Dynamic Style Application (Locked to Fire Theme with Image) ---
    current_theme = get_current_element_theme() # Returns Fire theme colors
    ACCENT_COLOR = current_theme['color']
    TEXT_COLOR = "#FFFFFF" # Set text to white for contrast against a dark background image
    DARK_BG_OVERLAY = "rgba(0, 0, 0, 0.7)" # Dark, semi-transparent background for content boxes
    
    st.markdown(f"""
        <style>
            /* Import awesome font for title */
            @import url('https://fonts.googleapis.com/css2?family=Bungee&display=swap');
            
            .stApp {{
                /* Set Fire Image as Background */
                background-image: url("{FIRE_BACKGROUND_URL}");
                background-size: cover;
                background-attachment: fixed;
                background-position: center;
                
                color: {TEXT_COLOR}; /* White text for contrast */
                transition: none;
            }}
            
            /* Ensure all text elements are white globally */
            .stApp, .stText, .stRadio, .stSlider label p, .stMarkdown, .css-1iyw478 * {{
                 color: {TEXT_COLOR} !important;
            }}

            /* Override colors for alert boxes (st.info, st.success, etc.) for DARK MODE look */
            .stAlert, .stInfo, .stSuccess, .stWarning, .stAlert * {{
                color: {TEXT_COLOR} !important; /* White text inside alerts */
                background-color: {DARK_BG_OVERLAY}; /* Dark, transparent background */
                border-radius: 8px;
                border: 1px solid {ACCENT_COLOR}; /* Add a border highlight */
            }}
            /* Specific success/error text color */
            .stSuccess, .stError {{
                background-color: {DARK_BG_OVERLAY}; 
                border-left: 5px solid {ACCENT_COLOR};
            }}
            
            /* Change the primary button color to reflect the Fire accent */
            .stButton>button {{
                width: 100%;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 15px;
                /* Dark Mode Styling for Buttons */
                background-color: {ACCENT_COLOR}; /* Use the Fire color */
                color: black; /* Black text on bright red button */
                border: none;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.5);
            }}
            
            /* Dynamic Question Accent Color (Locked Fire Color) */
            .stMarkdown h3 {{
                color: {ACCENT_COLOR}; 
                margin-top: 0.5rem;
                margin-bottom: 1.5rem;
                border-left: 4px solid {ACCENT_COLOR};
                padding-left: 10px;
                background-color: rgba(0, 0, 0, 0.4); /* Slightly lighter dark background for questions */
                border-radius: 4px;
            }}
            
            /* Style the Main H1 Title with the custom font */
            h1 {{
                color: {ACCENT_COLOR};
                text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.9);
                font-family: 'Bungee', cursive;
                font-size: 3.5rem;
            }}
            
            /* Style the new setup prompt 'Ready to test your skill?' (which is an h2) */
            .stMarkdown h2 {{
                color: #FFD700; /* Gold color for high contrast */
                font-size: 2.2rem;
                text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.7);
                margin-bottom: 2rem;
            }}
            
            /* Make the options container dark/transparent */
            .stRadio > label {{
                background-color: rgba(0, 0, 0, 0.3); /* Dark background for options */
                padding: 8px;
                border-radius: 4px;
                margin-bottom: 5px;
            }}

        </style>
    """, unsafe_allow_html=True)
    
    # Updated Main Title
    st.title("🔥😠 GrumpyQuest: Anime Trivia")
    
    st.markdown("---")


    if st.session_state.quiz_started:
        if st.session_state.current_index < len(st.session_state.current_quiz):
            render_question()
        else:
            render_quiz_complete()
    else:
        is_quiz_completed = len(st.session_state.current_quiz) > 0 and st.session_state.current_index >= len(st.session_state.current_quiz)

        if is_quiz_completed:
            render_quiz_complete()
        else:
            render_quiz_setup()


if __name__ == "__main__":
    main_app()


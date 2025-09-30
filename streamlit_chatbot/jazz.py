import streamlit as st
import requests
import json
import time

# --- Gemini API Configuration ---
# NOTE: This line is updated to prioritize Streamlit Secrets for local running.
# FIX for 403: If running locally, you MUST create a .streamlit/secrets.toml file 
# with your API key inside it (e.g., gemini_api_key = "YOUR_KEY_HERE").
API_KEY = "AIzaSyBAZYaPdiAx4AC3Cp3aQvY1IpJSgCZkllQ" # Attempts to retrieve key from secrets, defaults to ""
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"

# System Instruction to set the persona and tone
SYSTEM_PROMPT = (
    "You are 'Tuan Ramlee's Storyteller,' a highly knowledgeable and respectful historian dedicated to the life and works of the late, great Malaysian artist, P. Ramlee. "
    "Your responses must embody a cozy, nostalgic, and warm tone, reminiscent of the mid-20th century, perfect for reminiscing about the golden age of Malay cinema and music. "
    "You must only answer questions related to P. Ramlee's songs, movies, and personal details, including his masterpieces, hobbies, and close friends. "
    "When providing information, use a polite and gentle tone, offering details as if sharing cherished memories. "
    "If the query is outside this scope, politely decline and steer the conversation back to P. Ramlee."
)

# --- Core API Interaction Function with Exponential Backoff ---

def query_gemini(prompt):
    """
    Sends a query to the Gemini API with exponential backoff for reliability.
    Uses Google Search grounding for accurate, up-to-date information.
    """
    # Define payload structure
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],  # Enable Google Search for grounding
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
    }
    
    headers = {'Content-Type': 'application/json'}
    
    # Simple exponential backoff implementation (1s, 2s, 4s)
    for i in range(3):
        try:
            # Append API key to URL if present
            url_with_key = f"{API_URL}?key={API_KEY}"
            
            response = requests.post(url_with_key, headers=headers, data=json.dumps(payload))
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            
            result = response.json()
            candidate = result.get('candidates', [{}])[0]
            
            # Extract generated text
            text = candidate.get('content', {}).get('parts', [{}])[0].get('text', 'I seem to be lost in time. Could you rephrase your question?')
            
            # Extract citations (grounding metadata)
            sources = []
            grounding = candidate.get('groundingMetadata', {}).get('groundingAttributions', [])
            for attr in grounding:
                web_info = attr.get('web', {})
                if web_info.get('uri') and web_info.get('title'):
                    sources.append(f"[{web_info['title']}]({web_info['uri']})")
            
            # Format output with citations
            if sources:
                text += "\n\n---\n*Sources:* " + ", ".join(sources)
                
            return text

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and i < 2:
                # Handle rate limit with backoff
                time.sleep(2 ** i)
                continue
            # If the API key is invalid or permissions are wrong, you get a 403 Forbidden.
            if e.response.status_code == 403:
                return "Akses ditolak (403 Forbidden). Sila sahkan kunci API Gemini anda di dalam fail secrets.toml."
            
            return f"An error occurred while fetching information: {e.response.status_code} - {e.response.reason}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"
            
    return "I couldn't complete the request after several retries. Perhaps we can talk about a simpler song title?"

# --- Streamlit UI and Logic ---

def render_sidebar():
    """Renders the file uploader sidebar for media display."""
    st.sidebar.title("Media Corner 🖼️🎶")
    st.sidebar.markdown(
        "Muat naik fail media anda di sini untuk dipaparkan dalam sesi sembang ini."
    )

    uploaded_file = st.sidebar.file_uploader(
        "Pilih Gambar (.jpg, .png) atau Audio (.mp3)", 
        type=["png", "jpg", "jpeg", "mp3"]
    )

    if uploaded_file is not None:
        file_type = uploaded_file.type
        st.sidebar.subheader("Media Anda:")

        if 'image' in file_type:
            # Display image
            st.sidebar.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)
            st.sidebar.success("Gambar dimuatkan!")

        elif 'audio' in file_type:
            # Display audio player
            st.sidebar.audio(uploaded_file, format='audio/mp3', start_time=0)
            st.sidebar.success("Audio sedia untuk dimainkan!")
        
        else:
            st.sidebar.error("Format fail tidak disokong.")


def main_app():
    """Initializes and runs the Streamlit chatbot application."""
    st.set_page_config(
        page_title="Nostalgia Chat: P. Ramlee's Legacy", 
        layout="centered", 
        initial_sidebar_state="collapsed"
    )

    # Render the media sidebar
    render_sidebar()
    st.audio('LAGU.mp3')

    # Custom CSS for "Brown-Based Retro" Theme
    st.markdown("""
        <style>
            /* 1. Overall Brown/Tan Retro Theme */
            .stApp {
                background-color: #E8DBC5; /* Soft Tan/Cream background */
                color: #5C4033; /* Dark Brown text for soft contrast */
                font-family: 'Georgia', serif; /* Classic font */
            }
            /* 2. Main Chat Container Styling */
            .main > div {
                background-color: #FFFFFF; /* White paper look for main chat area */
                border-radius: 12px;
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
                padding: 15px;
            }
            
            /* 3. Sidebar Styling */
            .css-usj993, .css-1dp3s9c, .css-1cpxdwv { /* Targeting common sidebar elements */
                background-color: #D2B48C !important; /* Muted brown sidebar color */
                color: #4A2D1F !important; /* Darker text in sidebar */
                padding: 10px;
                border-radius: 8px;
            }
            
            /* 4. Header Styling */
            h1 {
                color: #8B4513; /* Saddle Brown title */
                text-align: center;
                font-family: 'Times New Roman', serif;
                border-bottom: 2px solid #D2B48C; /* Tan border */
                padding-bottom: 10px;
            }
            
            /* 5. Chat Bubbles - User (Darker Tan) */
            .stChatMessage.user {
                background-color: #C0A080; /* Medium Brown/Tan User bubble */
                border-radius: 10px;
                padding: 10px;
                margin-bottom: 10px;
                margin-left: 30%; /* Align right */
                color: #4A2D1F;
            }

            /* 6. Chat Bubbles - Bot (Cream/Off-White) */
            .stChatMessage.assistant {
                background-color: #F0EAD6; /* Very light cream bot bubble */
                border-radius: 10px;
                padding: 10px;
                margin-bottom: 10px;
                margin-right: 30%; /* Align left */
                color: #4A2D1F;
                border-left: 3px solid #8B4513; /* Brown accent line */
            }

            /* 7. Input/Button Styling */
            .stTextInput>div>div>input {
                border-radius: 8px;
                border: 1px solid #C0A080;
            }
            .stButton>button {
                background-color: #8B4513; /* Main brown button */
                color: white;
                border-radius: 8px;
                border: none;
                font-weight: bold;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🕰️ P. Ramlee's Songbook & Storyteller")
    st.markdown("---")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Initial greeting from the storyteller
        st.session_state.messages.append({"role": "assistant", "content": "Selamat datang, Tuan/Puan! I am here to share stories and details about the great Tan Sri P. Ramlee's songs and life. What cherished memory or question do you have today?"})

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Ask about a song, film, or P. Ramlee's life..."):
        
        # 1. Add user message to chat history and display
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Get and display the assistant's response
        with st.chat_message("assistant"):
            with st.spinner('Flipping through the old albums...'):
                full_response = query_gemini(prompt)
                st.markdown(full_response)
        
        # 3. Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})


if __name__ == "__main__":
    main_app()


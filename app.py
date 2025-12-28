import streamlit as st
import edge_tts
import asyncio
import os

# ==========================================
# 1. CONFIGURATION & VANI THEME
# ==========================================
st.set_page_config(
    page_title="SAMRION VANI",
    page_icon="🎙️",
    layout="wide"
)

st.markdown("""
<style>
    /* GLOBAL RESET */
    .stApp, p, h1, h2, h3, h4, h5, label, span, div, li, button {
        font-family: 'Inter', sans-serif !important;
        color: #ffffff !important;
    }

    /* BACKGROUND: SOUNDWAVE GRADIENT */
    .stApp {
        background: linear-gradient(135deg, #2b0c3d 0%, #4a196e 50%, #150524 100%);
        background-attachment: fixed;
    }

    /* GLASS INPUTS */
    .stTextArea > div > div > textarea {
        background-color: rgba(0, 0, 0, 0.3) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
    }
    
    /* DROPDOWNS */
    div[data-baseweb="select"] > div {
        background-color: rgba(255,255,255,0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.2);
    }
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul {
        background-color: #2b0c3d !important;
    }

    /* NEON BUTTONS (Purple/Pink) */
    div.stButton > button {
        background: linear-gradient(90deg, #da22ff, #9733ee) !important;
        border: none !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px #da22ff;
    }

    /* FOOTER */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #2b0c3d; /* Dark Purple */
        color: #ffffff; text-align: center; padding: 12px;
        font-size: 10px; letter-spacing: 2px; text-transform: uppercase;
        z-index: 9999; font-weight: 500;
        box-shadow: 0 -4px 10px rgba(0,0,0,0.3);
    }

    #MainMenu, footer, header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. VOICE DATABASE (Curated List)
# ==========================================
VOICES = {
    "🇮🇳 India - Neerja (Female)": "en-IN-NeerjaNeural",
    "🇮🇳 India - Prabhat (Male)": "en-IN-PrabhatNeural",
    "🇺🇸 US - Guy (Male - Professional)": "en-US-GuyNeural",
    "🇺🇸 US - Jenny (Female - Soft)": "en-US-JennyNeural",
    "🇺🇸 US - Aria (Female - Energetic)": "en-US-AriaNeural",
    "🇺🇸 US - Christopher (Male - Deep)": "en-US-ChristopherNeural",
    "🇬🇧 UK - Sonia (Female)": "en-GB-SoniaNeural",
    "🇬🇧 UK - Ryan (Male)": "en-GB-RyanNeural",
    "🇦🇺 Australia - Natasha (Female)": "en-AU-NatashaNeural",
    "🇯🇵 Japan - Keita (Male)": "ja-JP-KeitaNeural",
    "🇮🇳 Hindi - Swara (Female)": "hi-IN-SwaraNeural",
    "🇮🇳 Hindi - Madhur (Male)": "hi-IN-MadhurNeural",
    "🇫🇷 French - Denise (Female)": "fr-FR-DeniseNeural",
    "🇩🇪 German - Conrad (Male)": "de-DE-ConradNeural"
}

# ==========================================
# 3. ENGINE LOGIC
# ==========================================
async def generate_audio(text, voice, rate, pitch):
    """Generates audio using Edge TTS"""
    output_file = "vani_output.mp3"
    
    # Format rate and pitch
    rate_str = f"{rate:+d}%"
    pitch_str = f"{pitch:+d}Hz"
    
    communicate = edge_tts.Communicate(text, voice, rate=rate_str, pitch=pitch_str)
    await communicate.save(output_file)
    return output_file

# ==========================================
# 4. INTERFACE
# ==========================================
st.title("🎙️ SAMRION VANI")
st.markdown("### The Neural Voice Engine")

# MAIN LAYOUT
c1, c2 = st.columns([2, 1])

with c1:
    st.markdown("#### ✍️ Script Input")
    text_input = st.text_area("Type what you want Vani to say...", height=200, placeholder="Hello! I am Vani, the voice of the Samrion Ecosystem.")

with c2:
    st.markdown("#### 🎛️ Control Deck")
    
    # Voice Selector
    selected_voice_name = st.selectbox("Select Voice Model", list(VOICES.keys()))
    voice_id = VOICES[selected_voice_name]
    
    st.markdown("---")
    
    # Fine Tuning
    rate = st.slider("⚡ Speed", -50, 50, 0, format="%d%%")
    pitch = st.slider("🎵 Pitch", -50, 50, 0, format="%dHz")

    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("🚀 GENERATE SPEECH", use_container_width=True)

# EXECUTION
if generate_btn and text_input:
    with st.spinner("🎙️ Synthesizing Neural Audio..."):
        try:
            # Run Async function in Sync Streamlit
            output_file = asyncio.run(generate_audio(text_input, voice_id, rate, pitch))
            
            st.success("✅ Audio Generated Successfully!")
            
            # Audio Player
            audio_file = open(output_file, 'rb')
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mp3')
            
            # Download Button
            st.download_button(
                label="⬇️ DOWNLOAD MP3",
                data=audio_bytes,
                file_name="samrion_vani.mp3",
                mime="audio/mp3",
                type="primary"
            )
            
        except Exception as e:
            st.error(f"Synthesis Error: {e}")

# FOOTER
st.markdown("""
<div class="footer">
    POWERED BY SAMRION INTELLIGENCE &nbsp;|&nbsp; © 2026 SAMRION AI INFRASTRUCTURE &nbsp;|&nbsp; FOUNDER: NITIN RAJ
</div>
""", unsafe_allow_html=True)

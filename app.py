import streamlit as st
import json
import io
import zipfile
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from streamlit_mic_recorder import mic_recorder

# ==========================================
# 1. CONFIGURATION & THEME
# ==========================================
st.set_page_config(
    page_title="VANI ULTRA",
    page_icon="🧬",
    layout="wide"
)

# ULTRA-MODERN CSS
st.markdown("""
<style>
    .stApp, p, h1, h2, h3, label, div, button { font-family: 'Inter', sans-serif !important; color: white !important; }
    .stApp { background: linear-gradient(135deg, #000000 0%, #1e1e1e 100%); }
    
    /* NEON INPUTS */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #111 !important; border: 1px solid #333; color: #00ffcc !important;
    }
    
    /* CLONE BUTTON */
    div.stButton > button {
        background: linear-gradient(90deg, #00ffcc, #0099ff) !important;
        color: black !important; font-weight: bold; border: none;
    }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] { background-color: #111; padding: 10px; border-radius: 10px; }
    .stTabs [aria-selected="true"] { background-color: #00ffcc !important; color: black !important; }

    /* FOOTER */
    .footer {
        position: fixed; bottom: 0; width: 100%; background: black; color: #555;
        text-align: center; padding: 10px; font-size: 10px; letter-spacing: 2px;
    }
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================

def get_api_key():
    """Get ElevenLabs Key from Secrets"""
    try: return st.secrets["ELEVENLABS_API_KEY"]
    except: return None

def create_smrv_file(voice_id, voice_name, description):
    """Creates a proprietary .smrv file containing the Voice ID"""
    data = {
        "version": "2.0",
        "engine": "ElevenLabs",
        "voice_id": voice_id,
        "name": voice_name,
        "description": description
    }
    
    # Save as JSON inside a ZIP (masked as .smrv)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('soul.json', json.dumps(data, indent=4))
    
    buffer.seek(0)
    return buffer

def read_smrv_file(uploaded_file):
    """Reads the Voice ID from .smrv"""
    try:
        with zipfile.ZipFile(uploaded_file) as zf:
            data = json.loads(zf.read('soul.json'))
            return data
    except:
        return None

# ==========================================
# 3. MAIN INTERFACE
# ==========================================
st.title("🧬 VANI ULTRA")
st.markdown("### Neural Voice Cloning Lab")

api_key = get_api_key()

if not api_key:
    st.error("⚠️ API Key Missing! Please add `ELEVENLABS_API_KEY` to your secrets.")
    st.info("Get it from ElevenLabs.io (Free Tier gives 10,000 chars/month).")
    st.stop()

client = ElevenLabs(api_key=api_key)

tab_clone, tab_speak = st.tabs(["🧬 CLONE VOICE (Create .smrv)", "🗣️ SPEAK (Use .smrv)"])

# === TAB 1: CLONE VOICE ===
with tab_clone:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("#### 1. Record Sample")
        st.info("Record at least 1 minute of clear speech for best accuracy.")
        
        # Audio Recorder
        audio = mic_recorder(start_prompt="🔴 REC", stop_prompt="⏹️ STOP", key='recorder')
        
        if audio:
            st.audio(audio['bytes'])
            st.success("✅ Audio Captured")

    with c2:
        st.markdown("#### 2. Forge Soul")
        v_name = st.text_input("Voice Name", placeholder="e.g. Nitin AI")
        v_desc = st.text_area("Description", placeholder="Deep, calm, Indian accent")
        
        if st.button("🧬 INITIATE CLONING"):
            if audio and v_name:
                with st.spinner("Uploading to Neural Cloud..."):
                    try:
                        # 1. Add Voice to ElevenLabs
                        voice = client.clone(
                            name=v_name,
                            description=v_desc,
                            files=[io.BytesIO(audio['bytes'])],
                        )
                        
                        # 2. Generate .SMRV File
                        smrv_data = create_smrv_file(voice.voice_id, v_name, v_desc)
                        
                        st.success(f"✅ Voice Cloned! ID: {voice.voice_id}")
                        st.download_button(
                            "⬇️ DOWNLOAD .SMRV FILE",
                            data=smrv_data,
                            file_name=f"{v_name}.smrv",
                            mime="application/octet-stream"
                        )
                        
                    except Exception as e:
                        st.error(f"Cloning Error: {e}")
            else:
                st.warning("Record audio and name it first.")

# === TAB 2: SPEAK ===
with tab_speak:
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_up, col_tts = st.columns([1, 2])
    
    with col_up:
        st.markdown("#### 1. Insert Soul Card")
        uploaded_file = st.file_uploader("Upload .smrv file", type=["smrv"])
        
        active_voice_id = None
        
        if uploaded_file:
            soul = read_smrv_file(uploaded_file)
            if soul:
                st.success(f"🔹 ACTIVE: {soul['name']}")
                st.caption(soul['description'])
                active_voice_id = soul['voice_id']
            else:
                st.error("Invalid File")

    with col_tts:
        st.markdown("#### 2. Text-to-Speech")
        text = st.text_area("Script", height=150, placeholder="Type here...")
        
        if st.button("🚀 SPEAK NOW"):
            if active_voice_id and text:
                with st.spinner("Synthesizing..."):
                    try:
                        # Generate Audio
                        audio_stream = client.generate(
                            text=text,
                            voice=active_voice_id,
                            model="eleven_multilingual_v2"
                        )
                        
                        # Convert generator to bytes
                        audio_bytes = b""
                        for chunk in audio_stream:
                            audio_bytes += chunk
                            
                        st.audio(audio_bytes, format='audio/mp3')
                        st.download_button("⬇️ SAVE MP3", audio_bytes, "clone.mp3")
                        
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Upload a .smrv file and type text first.")

# FOOTER
st.markdown("""<div class="footer">POWERED BY SAMRION INTELLIGENCE | © 2026</div>""", unsafe_allow_html=True)

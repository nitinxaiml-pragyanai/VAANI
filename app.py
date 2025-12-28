import streamlit as st
import edge_tts
import asyncio
import io
import json
import zipfile
from elevenlabs.client import ElevenLabs
from streamlit_mic_recorder import mic_recorder

# ==========================================
# 1. CONFIGURATION & ROYAL THEME
# ==========================================
st.set_page_config(
    page_title="SAMRION VANI OMEGA",
    page_icon="🎙️",
    layout="wide"
)

# THE ROYAL BLUE & RED THEME
st.markdown("""
<style>
    /* 1. GLOBAL TEXT RESET */
    .stApp, p, h1, h2, h3, h4, h5, label, span, div, li, button, small {
        font-family: 'Inter', sans-serif !important;
        color: #ffffff !important;
    }

    /* 2. BACKGROUND: ROYAL IMPERIAL BLUE */
    .stApp {
        background: linear-gradient(135deg, #001f3f 0%, #003366 50%, #00509e 100%);
        background-attachment: fixed;
    }

    /* 3. INPUTS (Glass Style) */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: rgba(0, 0, 0, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white !important;
        border-radius: 10px;
    }
    div[data-baseweb="select"] > div {
        background-color: rgba(0, 0, 0, 0.4) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* 4. DROPDOWN MENUS (Dark Blue) */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul {
        background-color: #001f3f !important;
    }
    li[role="option"] {
        color: white !important;
    }

    /* 5. BUTTONS (ROYAL RED / PINK GRADIENT) */
    div.stButton > button {
        background: linear-gradient(90deg, #ff007f, #ff4081) !important; /* The Red/Pink you wanted */
        border: none !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        transition: 0.3s;
        box-shadow: 0 4px 15px rgba(255, 0, 127, 0.3);
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px #ff007f;
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px; background-color: rgba(0,0,0,0.2);
        padding: 10px; border-radius: 15px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff007f !important;
        color: white !important;
    }

    /* FOOTER */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background: rgba(0, 31, 63, 0.9); backdrop-filter: blur(10px);
        color: rgba(255,255,255,0.7); text-align: center;
        padding: 12px; font-size: 11px; letter-spacing: 1px; z-index: 999;
        border-top: 1px solid rgba(255,255,255,0.1);
    }
    #MainMenu, footer, header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. VOICE DATABASE (20 Preinstalled Voices)
# ==========================================
FREE_VOICES = {
    "🇮🇳 India - Prabhat (Male)": "en-IN-PrabhatNeural",
    "🇮🇳 India - Neerja (Female)": "en-IN-NeerjaNeural",
    "🇺🇸 US - Guy (Male - Pro)": "en-US-GuyNeural",
    "🇺🇸 US - Christopher (Male - Deep)": "en-US-ChristopherNeural",
    "🇺🇸 US - Eric (Male - Casual)": "en-US-EricNeural",
    "🇺🇸 US - Jenny (Female - Soft)": "en-US-JennyNeural",
    "🇺🇸 US - Aria (Female - Energetic)": "en-US-AriaNeural",
    "🇺🇸 US - Michelle (Female - Sweet)": "en-US-MichelleNeural",
    "🇬🇧 UK - Ryan (Male)": "en-GB-RyanNeural",
    "🇬🇧 UK - Sonia (Female)": "en-GB-SoniaNeural",
    "🇬🇧 UK - Libby (Female)": "en-GB-LibbyNeural",
    "🇦🇺 Australia - Natasha": "en-AU-NatashaNeural",
    "🇦🇺 Australia - William": "en-AU-WilliamNeural",
    "🇨🇦 Canada - Liam": "en-CA-LiamNeural",
    "🇯🇵 Japan - Keita": "ja-JP-KeitaNeural",
    "🇰🇷 Korea - InJoon": "ko-KR-InJoonNeural",
    "🇫🇷 French - Denise": "fr-FR-DeniseNeural",
    "🇩🇪 German - Conrad": "de-DE-ConradNeural",
    "🇮🇳 Hindi - Swara": "hi-IN-SwaraNeural",
    "🇮🇳 Hindi - Madhur": "hi-IN-MadhurNeural"
}

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def get_eleven_key():
    try: return st.secrets["ELEVENLABS_API_KEY"]
    except: return None

async def generate_edge_audio(text, voice, rate, pitch):
    output_file = "vani_std.mp3"
    rate_str = f"{rate:+d}%"
    pitch_str = f"{pitch:+d}Hz"
    communicate = edge_tts.Communicate(text, voice, rate=rate_str, pitch=pitch_str)
    await communicate.save(output_file)
    return output_file

def create_smrv_file(voice_id, voice_name, description):
    data = {"version": "2.0", "engine": "ElevenLabs", "voice_id": voice_id, "name": voice_name, "description": description}
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('soul.json', json.dumps(data, indent=4))
    buffer.seek(0)
    return buffer

def read_smrv_file(uploaded_file):
    try:
        with zipfile.ZipFile(uploaded_file) as zf:
            return json.loads(zf.read('soul.json'))
    except: return None

# ==========================================
# 4. MAIN INTERFACE
# ==========================================
st.title("🎙️ VANI OMEGA")
st.markdown("### The Ultimate Voice Ecosystem")

# TABS FOR MODES
tab_std, tab_clone, tab_god = st.tabs(["🗣️ Vani Standard (Free)", "🧬 God Mode (Cloning)", "💾 Soul Manager"])

# === TAB 1: STANDARD (EdgeTTS - 20 Voices) ===
with tab_std:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown("#### ✍️ Script")
        std_text = st.text_area("Type text...", height=200, placeholder="Hello, I am using the preinstalled voices.")
    
    with c2:
        st.markdown("#### 🎛️ Settings")
        selected_voice = st.selectbox("Choose Voice Model", list(FREE_VOICES.keys()))
        voice_code = FREE_VOICES[selected_voice]
        
        rate = st.slider("Speed", -50, 50, 0, key="std_rate")
        pitch = st.slider("Pitch", -50, 50, 0, key="std_pitch")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 GENERATE SPEECH", key="btn_std", use_container_width=True):
            if std_text:
                with st.spinner("Synthesizing..."):
                    out_file = asyncio.run(generate_edge_audio(std_text, voice_code, rate, pitch))
                    st.audio(out_file)
                    with open(out_file, "rb") as f:
                        st.download_button("⬇️ DOWNLOAD MP3", f, "vani_standard.mp3")

# === TAB 2: GOD MODE (ElevenLabs Cloning) ===
with tab_clone:
    st.markdown("<br>", unsafe_allow_html=True)
    
    api_key = get_eleven_key()
    if not api_key:
        st.error("⚠️ God Mode requires an ElevenLabs API Key in secrets.")
    else:
        client = ElevenLabs(api_key=api_key)
        
        c_rec, c_set = st.columns(2)
        with c_rec:
            st.markdown("#### 1. Record Target Voice")
            st.info("Record 1 minute of clear audio for 100% accuracy.")
            audio = mic_recorder(start_prompt="🔴 REC", stop_prompt="⏹️ STOP", key='recorder')
            if audio: st.audio(audio['bytes'])
            
        with c_set:
            st.markdown("#### 2. Forge Identity")
            v_name = st.text_input("Voice Name", placeholder="e.g. Nitin AI")
            v_desc = st.text_area("Description", placeholder="Deep Indian Accent")
            
            if st.button("🧬 INITIATE CLONING", key="btn_clone", use_container_width=True):
                if audio and v_name:
                    with st.spinner("Uploading to Neural Cloud..."):
                        try:
                            voice = client.clone(name=v_name, description=v_desc, files=[io.BytesIO(audio['bytes'])])
                            smrv_data = create_smrv_file(voice.voice_id, v_name, v_desc)
                            st.success(f"✅ Voice Cloned! ID: {voice.voice_id}")
                            st.download_button("⬇️ DOWNLOAD .SMRV", smrv_data, f"{v_name}.smrv")
                        except Exception as e: st.error(f"Error: {e}")

# === TAB 3: SOUL MANAGER (Use Cloned Voice) ===
with tab_god:
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not api_key:
        st.error("⚠️ Connect API Key first.")
    else:
        client = ElevenLabs(api_key=api_key)
        
        col_up, col_tts = st.columns([1, 2])
        with col_up:
            st.markdown("#### 1. Load Soul (.smrv)")
            uploaded_file = st.file_uploader("", type=["smrv"])
            active_id = None
            if uploaded_file:
                soul = read_smrv_file(uploaded_file)
                if soul:
                    st.success(f"🔹 ACTIVE: {soul['name']}")
                    active_id = soul['voice_id']

        with col_tts:
            st.markdown("#### 2. Text-to-Speech")
            god_text = st.text_area("Script", height=150, placeholder="I can now speak with the cloned voice.", key="god_txt")
            
            if st.button("🚀 SPEAK (GOD MODE)", key="btn_god", use_container_width=True):
                if active_id and god_text:
                    with st.spinner("Synthesizing..."):
                        try:
                            audio_stream = client.generate(text=god_text, voice=active_id, model="eleven_multilingual_v2")
                            audio_bytes = b"".join(audio_stream)
                            st.audio(audio_bytes, format='audio/mp3')
                            st.download_button("⬇️ DOWNLOAD CLONE", audio_bytes, "clone.mp3")
                        except Exception as e: st.error(f"Error: {e}")

# FOOTER
st.markdown("""
<div class="footer">
    POWERED BY SAMRION INTELLIGENCE | © 2026 SAMRION AI INFRASTRUCTURE | FOUNDER: NITIN RAJ
</div>
""", unsafe_allow_html=True)

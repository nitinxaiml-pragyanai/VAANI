import streamlit as st
import edge_tts
import asyncio
import io
import json
import zipfile
import random
import requests  # <--- DIRECT API CONNECTION (STABLE)
from streamlit_mic_recorder import mic_recorder

# ==========================================
# 1. CONFIGURATION & ROYAL THEME
# ==========================================
st.set_page_config(
    page_title="VANI",
    page_icon="🎙️",
    layout="wide"
)

# === THE ROYAL BLUE & RED CSS PATCH ===
st.markdown("""
<style>
    /* 1. GLOBAL FONT & COLOR */
    .stApp, p, h1, h2, h3, h4, h5, label, span, div, li, button, small {
        font-family: 'Inter', sans-serif !important;
        color: #ffffff !important;
    }

    /* 2. BACKGROUND: ROYAL BLUE THEME */
    .stApp {
        background: linear-gradient(135deg, #020024 0%, #090979 35%, #00d4ff 100%);
        background: linear-gradient(to bottom right, #001540, #002d72, #001540);
        background-attachment: fixed;
    }

    /* 3. INPUTS (Glass Style - Dark Blue) */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: rgba(0, 20, 60, 0.6) !important;
        border: 1px solid #ff0000;
        color: white !important;
        border-radius: 8px;
    }
    
    /* 4. DROPDOWN MENUS */
    div[data-baseweb="select"] > div {
        background-color: rgba(0, 20, 60, 0.8) !important;
        color: white !important;
        border: 1px solid #ff0000;
    }
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul {
        background-color: #001540 !important;
    }
    li[role="option"]:hover {
        background-color: #D60000 !important;
    }

    /* 5. TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(0,0,0,0.3);
        padding: 10px 20px;
        border-radius: 30px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border-radius: 20px;
        color: white;
        font-weight: 600;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #D60000 !important;
        box-shadow: 0 0 15px rgba(214, 0, 0, 0.6);
    }

    /* 6. BUTTONS */
    div.stButton > button {
        background: linear-gradient(90deg, #D60000, #ff4d4d) !important;
        border: none !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        transition: 0.3s;
        box-shadow: 0 4px 15px rgba(214, 0, 0, 0.4);
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px #ff0000;
    }

    /* 7. FILE UPLOADER FIX */
    [data-testid='stFileUploader'] {
        background-color: rgba(0, 20, 60, 0.5);
        border: 1px dashed #ff0000;
        border-radius: 10px;
        padding: 20px;
    }
    [data-testid='stFileUploader'] section {
        background-color: transparent !important;
    }
    [data-testid='stFileUploader'] button {
         background: transparent !important;
         border: 1px solid white !important;
    }

    /* FOOTER */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background: rgba(0, 21, 64, 0.95);
        color: rgba(255,255,255,0.7); text-align: center;
        padding: 12px; font-size: 11px; letter-spacing: 1px; z-index: 999;
        border-top: 1px solid #D60000;
    }
    #MainMenu, footer, header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. VOICE DATABASE
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

CALIBRATION_SENTENCES = [
    "1. The quick brown fox jumps over the lazy dog.",
    "2. Sphinx of black quartz, judge my vow.",
    "3. How vexingly quick daft zebras jump!",
    "4. Pack my box with five dozen liquor jugs.",
    "5. I am recording my voice for the Samrion Neural Engine."
]

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
st.title(" VANI ")
st.markdown("### The Royal Voice Ecosystem")

tab_std, tab_clone, tab_god = st.tabs([" Vani", "Cloning", "💾 Voice Manager"])

# === TAB 1: STANDARD (EdgeTTS) ===
with tab_std:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown("#### ✍️ Script")
        std_text = st.text_area("Type text...", height=200, placeholder="Hello, I am using the preinstalled voices.")
    
    with c2:
        st.markdown("#### 🎛️ Settings")
        selected_voice = st.selectbox("Choose Voice Model (20 Available)", list(FREE_VOICES.keys()))
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

# === TAB 2: GOD MODE (Direct API Cloning) ===
with tab_clone:
    st.markdown("<br>", unsafe_allow_html=True)
    
    api_key = get_eleven_key()
    if not api_key:
        st.warning("⚠️ God Mode requires an ElevenLabs API Key in secrets.")
    
    c_rec, c_set = st.columns(2)
    with c_rec:
        st.markdown("#### 1. Phonetic Calibration")
        st.info("⚠️ READ THIS EXACTLY to crack your voice style:")
        
        calibration_html = "<br>".join(CALIBRATION_SENTENCES)
        st.markdown(f"""
        <div style="background-color: rgba(0, 0, 0, 0.4); border: 2px solid #D60000; border-radius: 10px; padding: 15px; color: white; font-family: monospace;">
            {calibration_html}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        audio = mic_recorder(start_prompt="🔴 RECORD CALIBRATION", stop_prompt="⏹️ STOP", key='recorder')
        if audio: 
            st.audio(audio['bytes'])
            st.success("✅ Voice Sample Captured")
        
    with c_set:
        st.markdown("#### 2. Forge Identity")
        v_name = st.text_input("Voice Name", placeholder="e.g. Nitin AI")
        v_desc = st.text_area("Description", placeholder="Deep Indian Accent, Calm Tone")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🧬 INITIATE CLONING", key="btn_clone", use_container_width=True):
            if api_key and audio and v_name:
                with st.spinner("Uploading to Neural Cloud (Direct API)..."):
                    try:
                        # === DIRECT API APPROACH (BYPASS SDK) ===
                        url = "https://api.elevenlabs.io/v1/voices/add"
                        
                        headers = {
                            "xi-api-key": api_key
                        }
                        
                        # Multipart Form Data
                        files = {
                            'files': ('sample.wav', audio['bytes'], 'audio/wav')
                        }
                        data = {
                            'name': v_name,
                            'description': v_desc
                        }
                        
                        response = requests.post(url, headers=headers, data=data, files=files)
                        
                        if response.status_code == 200:
                            voice_id = response.json().get('voice_id')
                            smrv_data = create_smrv_file(voice_id, v_name, v_desc)
                            st.success(f"✅ Voice Cloned Successfully! ID: {voice_id}")
                            st.download_button("⬇️ DOWNLOAD .SMRV", smrv_data, f"{v_name}.smrv", use_container_width=True)
                        else:
                            st.error(f"Failed to clone: {response.text}")
                            
                    except Exception as e:
                        st.error(f"Connection Error: {e}")
            elif not api_key:
                st.error("Missing API Key.")

# === TAB 3: SOUL MANAGER ===
with tab_god:
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_up, col_tts = st.columns([1, 2])
    with col_up:
        st.markdown("#### 1. Load Soul (.smrv)")
        uploaded_file = st.file_uploader("", type=["smrv"])
        
        active_id = None
        if uploaded_file:
            soul = read_smrv_file(uploaded_file)
            if soul:
                st.markdown(f"""
                <div style="background: #D60000; padding: 10px; border-radius: 5px; text-align: center;">
                    <b>🔹 ACTIVE: {soul['name']}</b>
                </div>
                """, unsafe_allow_html=True)
                active_id = soul['voice_id']

    with col_tts:
        st.markdown("#### 2. Text-to-Speech")
        god_text = st.text_area("Script", height=150, placeholder="I can now speak with the cloned voice.", key="god_txt")
        
        if st.button("🚀 SPEAK (GOD MODE)", key="btn_god", use_container_width=True):
            if active_id and god_text and api_key:
                with st.spinner("Synthesizing (Direct API)..."):
                    try:
                        # === DIRECT API GENERATION (ROBUST) ===
                        # We use requests here too to match the robustness of the cloning tab
                        url = f"https://api.elevenlabs.io/v1/text-to-speech/{active_id}"
                        headers = {
                            "Accept": "audio/mpeg",
                            "Content-Type": "application/json",
                            "xi-api-key": api_key
                        }
                        data = {
                            "text": god_text,
                            "model_id": "eleven_multilingual_v2",
                            "voice_settings": {
                                "stability": 0.5,
                                "similarity_boost": 0.75
                            }
                        }
                        
                        response = requests.post(url, json=data, headers=headers)
                        
                        if response.status_code == 200:
                            st.audio(response.content, format='audio/mp3')
                            st.download_button("⬇️ DOWNLOAD CLONE", response.content, "clone.mp3")
                        else:
                            st.error(f"TTS Error: {response.text}")

                    except Exception as e:
                        st.error(f"Error: {e}")
            elif not api_key:
                st.error("API Key required.")

# FOOTER
st.markdown("""
<div class="footer">
    POWERED BY SAMRION INTELLIGENCE | © 2026 SAMRION AI INFRASTRUCTURE | FOUNDER: NITIN RAJ
</div>
""", unsafe_allow_html=True)

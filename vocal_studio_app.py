import streamlit as st
import os
import shutil
import subprocess
from audio_prep import process_file_pipeline

st.set_page_config(page_title="AI Vocal Studio", page_icon="🎤", layout="wide")

st.markdown("""
<style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    h1, h2, h3 {
        color: #58a6ff;
    }
    .stButton button {
        background-color: #238636;
        color: white;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #2ea043;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎤 AI Vocal Studio: Isolator & Dataset Prep")
st.markdown("Upload your old rap tracks. This tool will mathematically strip away the beat and chop your clean vocals into perfectly sized training chunks for the Voice Cloning AI.")

st.markdown("---")

uploaded_file = st.file_uploader("Upload an MP3 or WAV file", type=["mp3", "wav", "m4a"])

WORKSPACE_DIR = "workspace"
if not os.path.exists(WORKSPACE_DIR):
    os.makedirs(WORKSPACE_DIR)

# Check for ffmpeg installation
ffmpeg_installed = shutil.which("ffmpeg") is not None
if not ffmpeg_installed:
    st.error("🚨 **FFmpeg is not installed!** This is required for Demucs to process audio. Please run the install command provided by your AI assistant.")
    st.stop()

if uploaded_file is not None:
    # Save the uploaded file temporarily
    file_path = os.path.join(WORKSPACE_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    st.success(f"Uploaded {uploaded_file.name} successfully!")
    
    if st.button("Extract Vocals & Build Dataset", type="primary"):
        with st.status("Processing Audio (This may take a few minutes)...", expanded=True) as status:
            try:
                st.write("🎵 Running high-fidelity stem separation...")
                vocal_path, chunks = process_file_pipeline(file_path, WORKSPACE_DIR)
                
                status.update(label="Isolation Complete!", state="complete", expanded=False)
                
                st.subheader("🎧 Isolated Vocal Track")
                st.audio(vocal_path)
                
                st.subheader("📦 Training Dataset Generated")
                st.success(f"Successfully generated {len(chunks)} high-quality audio chunks for Voice Cloning!")
                
                with st.expander("Preview Training Chunks"):
                    for i, chunk_path in enumerate(chunks[:5]): # Preview up to 5
                        st.write(f"Chunk {i+1}:")
                        st.audio(chunk_path)
                    if len(chunks) > 5:
                        st.write(f"... and {len(chunks) - 5} more.")
                        
            except Exception as e:
                status.update(label="Processing Failed", state="error")
                st.error(f"An error occurred: {str(e)}")

st.markdown("---")
st.markdown("*Stage 1 of the AI Music Studio - Powered by Facebook HTDemucs & PyDub*")

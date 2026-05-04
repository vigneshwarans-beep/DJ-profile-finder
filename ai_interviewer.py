import os
import time
import pyttsx3

# --- SETUP TTS (Text-To-Speech) ---
# We use pyttsx3 because it is 100% free, offline, and built into Windows
engine = pyttsx3.init()
engine.setProperty('rate', 160) # Speed of speech
voices = engine.getProperty('voices')
# Try to find a female voice (usually index 1 on Windows)
if len(voices) > 1:
    engine.setProperty('voice', voices[1].id)

def speak(text):
    """Converts text to speech and plays it locally."""
    print(f"\n[AI INTERVIEWER]: {text}")
    engine.say(text)
    engine.runAndWait()

# --- SETUP AUDIO RECORDING ---
# Using sounddevice because it doesn't require complex C++ build tools on Windows
import sounddevice as sd
from scipy.io.wavfile import write

def listen():
    """Records audio from the microphone and prepares it for transcription."""
    print("\n[LISTENING...] (Recording for 5 seconds...)")
    fs = 44100  # Sample rate
    seconds = 5  # Duration of recording
    
    # Record audio
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    
    print("[PROCESSING AUDIO...]")
    # Save as WAV file
    filename = "temp_recording.wav"
    write(filename, fs, myrecording)
    
    # Placeholder for Local Whisper STT:
    # return local_whisper_model.transcribe(filename)
    
    # For now, we return a mock transcription since Whisper is heavy to install
    mock_transcriptions = [
        "Hi, I'm ready.",
        "I have 5 years of experience.",
        "I manage deadlines well.",
        "Thank you, goodbye!"
    ]
    import random
    text = random.choice(mock_transcriptions)
    print(f"[YOU (MOCK STT)]: {text}")
    return text

# --- MOCK LLM (Language Model) ---
def generate_ai_response(candidate_text):
    """
    This is where we will call a free-tier LLM (like Gemini or Groq) or a local Llama 3 model.
    For now, it uses simple mock logic to demonstrate the loop.
    """
    candidate_text = candidate_text.lower()
    
    if "hello" in candidate_text or "hi" in candidate_text:
        return "Hello! Thank you for joining the interview today. Could you start by telling me a little bit about your background?"
    elif "experience" in candidate_text or "years" in candidate_text or "worked" in candidate_text:
        return "That sounds like great experience. How do you handle tight deadlines in your previous roles?"
    elif "deadline" in candidate_text or "time" in candidate_text or "manage" in candidate_text:
        return "Excellent. Can you describe a time when you had to resolve a conflict with a team member?"
    elif "thank you" in candidate_text or "bye" in candidate_text:
        return "Thank you for your time today. We will be in touch regarding the next steps. Goodbye!"
    else:
        return "That's interesting. Can you elaborate a bit more on that?"

def run_interview():
    """Main interview loop."""
    print("="*50)
    print("STARTING AI AUDIO INTERVIEW MODULE")
    print("="*50)
    
    # Opening statement
    speak("Hello, and welcome to your automated interview. I am the AI Recruiter. Whenever you are ready, please say 'Hi' to begin.")
    
    conversation_active = True
    while conversation_active:
        candidate_response = listen()
        
        if candidate_response:
            ai_reply = generate_ai_response(candidate_response)
            speak(ai_reply)
            
            if "Goodbye!" in ai_reply:
                conversation_active = False

if __name__ == "__main__":
    # Note: Requires pip install sounddevice scipy pyttsx3
    run_interview()

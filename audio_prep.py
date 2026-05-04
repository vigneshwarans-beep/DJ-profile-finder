import os
import subprocess
import librosa
import soundfile as sf
import shutil

def isolate_vocals(input_audio_path, output_dir):
    """
    Uses Facebook's HTDemucs model to perfectly isolate vocals from an instrumental.
    Returns the path to the isolated vocal WAV file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"[*] Starting Vocal Isolation for: {os.path.basename(input_audio_path)}")
    print("[*] Note: This may take several minutes depending on your system.")
    
    # Run Demucs via command line to separate into just 2 stems (vocals / non-vocals)
    # Using htdemucs model which is high-fidelity
    command = [
        "python", "-m", "demucs.separate",
        "-n", "htdemucs",
        "--two-stems", "vocals",
        "-o", output_dir,
        input_audio_path
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        
        # Demucs creates a folder structure like: output_dir/htdemucs/filename/vocals.wav
        filename_no_ext = os.path.splitext(os.path.basename(input_audio_path))[0]
        vocal_track_path = os.path.join(output_dir, "htdemucs", filename_no_ext, "vocals.wav")
        
        if os.path.exists(vocal_track_path):
            print("[+] Isolation successful!")
            return vocal_track_path
        else:
            raise FileNotFoundError(f"Vocal track not found at expected path: {vocal_track_path}")
            
    except subprocess.CalledProcessError as e:
        print(f"[!] Demucs Error:\n{e.stderr}")
        raise RuntimeError("Failed to isolate vocals. Check console for details.")

def prepare_dataset(vocal_track_path, dataset_out_dir, top_db=40):
    """
    Removes silence and chunks the audio into ~10 second snippets for AI training using librosa.
    """
    if not os.path.exists(dataset_out_dir):
        os.makedirs(dataset_out_dir)
        
    print(f"[*] Slicing dataset from: {vocal_track_path}")
    
    # Load audio
    y, sr = librosa.load(vocal_track_path, sr=None)
    
    print("[*] Removing dead air and splitting on silence...")
    # Get non-silent intervals
    intervals = librosa.effects.split(y, top_db=top_db)
    
    # Target length in samples (10 seconds)
    target_length_samples = 10 * sr
    
    combined_chunks = []
    current_chunk = []
    current_length = 0
    
    for start, end in intervals:
        segment = y[start:end]
        current_chunk.extend(segment)
        current_length += len(segment)
        
        if current_length >= target_length_samples:
            combined_chunks.append(current_chunk)
            current_chunk = []
            current_length = 0
            
    if current_length > sr * 2: # keep if at least 2 seconds
        combined_chunks.append(current_chunk)
        
    print(f"[*] Created {len(combined_chunks)} perfect training chunks.")
    
    exported_files = []
    filename_prefix = os.path.splitext(os.path.basename(vocal_track_path))[0]
    
    import numpy as np
    for i, chunk in enumerate(combined_chunks):
        out_path = os.path.join(dataset_out_dir, f"{filename_prefix}_chunk_{i+1:03d}.wav")
        chunk_arr = np.array(chunk)
        sf.write(out_path, chunk_arr, sr)
        exported_files.append(out_path)
        
    print("[+] Dataset preparation complete!")
    return exported_files

def process_file_pipeline(input_path, workspace_dir="workspace"):
    """
    Full end-to-end pipeline: Isolate -> Chunk -> Save to dataset.
    """
    iso_dir = os.path.join(workspace_dir, "isolated_vocals")
    dataset_dir = os.path.join(workspace_dir, "training_dataset")
    
    vocal_track = isolate_vocals(input_path, iso_dir)
    chunks = prepare_dataset(vocal_track, dataset_dir)
    
    return vocal_track, chunks

if __name__ == "__main__":
    # Example usage for CLI testing
    import sys
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        process_file_pipeline(test_file)
    else:
        print("Provide an audio file path to test.")

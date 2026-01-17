import librosa
import numpy as np
import moviepy.editor as mp_editor
import os

class AudioAnalyzer:
    def __init__(self):
        print("[*] Initializing Librosa Audio Analyzer...")

    def get_best_clips(self, video_path: str):
        print(f"[*] Extracting audio from {os.path.basename(video_path)}...")
        
        # 1. Extract Audio to temporary file
        try:
            clip = mp_editor.VideoFileClip(video_path)
            audio_path = "temp_audio.wav"
            clip.audio.write_audiofile(audio_path, logger=None)
            video_duration = clip.duration
            clip.close()
        except Exception as e:
            print(f"[!] Error extracting audio: {e}")
            return []

        # 2. Load Audio with Librosa
        print("[*] Loading audio into Librosa...")
        y, sr = librosa.load(audio_path, sr=None)
        
        # 3. Calculate RMS Energy
        print("[*] Calculating Energy Profile...")
        hop_length = 512
        frame_length = 2048
        rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
        
        # Convert frames to time
        times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop_length)
        
        # 4. Find High Energy Segments
        # Strategy: specific 60s windows with highest average energy
        print("[*] Identifying Viral Moments (High Energy)...")
        
        window_size_sec = 60 # Target clip length (User requested 30-60s)
        step_size_sec = 20   # Overlap
        
        clips = []
        
        # Sliding window
        current_time = 0
        while current_time + window_size_sec < video_duration:
            start_frame = librosa.time_to_frames(current_time, sr=sr, hop_length=hop_length)
            end_frame = librosa.time_to_frames(current_time + window_size_sec, sr=sr, hop_length=hop_length)
            
            # Safe indexing
            start_frame = min(start_frame, len(rms))
            end_frame = min(end_frame, len(rms))
            
            if start_frame < end_frame:
                window_energy = np.mean(rms[start_frame:end_frame])
                clips.append({
                    "start": current_time,
                    "end": current_time + window_size_sec,
                    "score": window_energy
                })
            
            current_time += step_size_sec
            
        # Cleanup
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
        # Sort by score (descending) and take top 3
        clips.sort(key=lambda x: x["score"], reverse=True)
        top_clips = clips[:3]
        
        # Format for main.py
        final_clips = []
        for c in top_clips:
            final_clips.append({
                "start": float(c["start"]),
                "end": float(c["end"]),
                "reason": "High Energy / Loudness Peak"
            })
            
        print(f"[+] Found {len(final_clips)} high-energy clips via Librosa.")
        return final_clips

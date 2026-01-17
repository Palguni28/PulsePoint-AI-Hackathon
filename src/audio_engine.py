import os
from moviepy.editor import VideoFileClip

def extract_audio(video_path: str, output_audio_path: str = "temp_audio.wav") -> str:
    """
    Step 1: Extracts audio from the raw video file.
    
    Args:
        video_path (str): Path to the source video (mp4/mkv).
        output_audio_path (str): Destination for the .wav file.
        
    Returns:
        str: Path to the extracted audio file if successful, else None.
    """
    print(f"[*] Starting Audio Extraction for: {video_path}")
    
    # 1. Validation: Does the file exist?
    if not os.path.exists(video_path):
        print(f"[!] Error: Video file not found at {video_path}")
        return None

    try:
        # 2. Load Video
        video = VideoFileClip(video_path)
        
        # 3. Validation: Does it have audio?
        if video.audio is None:
            print("[!] Error: Source video has no audio track.")
            return None

        # 4. Extract and Write Audio
        # We use strict parameters to ensure compatibility with Whisper
        video.audio.write_audiofile(
            output_audio_path,
            codec='pcm_s16le', # 16-bit PCM (standard for WAV)
            fps=16000,         # 16kHz is Whisper's native sample rate
            verbose=False,
            logger=None
        )
        
        print(f"[+] Audio successfully extracted to: {output_audio_path}")
        return output_audio_path

    except Exception as e:
        print(f"[!] Critical Extraction Failure: {e}")
        return None
    finally:
        # Cleanup: Close the video file pointer to release system resources
        if 'video' in locals():
            video.close()
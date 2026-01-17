import os
from moviepy.editor import VideoFileClip
from vision_engine import VisionEngine
import cv2
from dotenv import load_dotenv

load_dotenv()

def process_video(video_path):
    print(f"=== PROCESSING: {video_path} ===")
    
    # 1. Validation
    if not os.path.exists(video_path):
        print(f"[!] Error: Input file not found at {video_path}")
        return []

    # 2. Logic Phase (Librosa Audio Analysis)
    from audio_analyzer import AudioAnalyzer
    analyzer = AudioAnalyzer()
    best_segments = analyzer.get_best_clips(video_path)
    
    generated_files = []

    if not best_segments:
        print("[!] No clips found. Check API Key or Input Video.")
        return []

    # 3. Vision Phase (Captions Disabled)
    vision = VisionEngine()
    original_clip = VideoFileClip(video_path)
    
    print(f"=== RENDERING {len(best_segments)} CLIPS ===")
    
    for i, seg in enumerate(best_segments):
        start = seg['start']
        end = seg['end']
        reason = seg.get('reason', 'viral_moment')
        
        if end > original_clip.duration:
            end = original_clip.duration
            
        print(f"Processing Clip {i+1}: {start}s - {end}s")
        
        # A. Subclip
        clip = original_clip.subclip(start, end)
        
        # B. Smart Crop (Dynamic)
        # 1. Analyze motion for this specific clip
        get_crop_x, new_width = vision.get_tracking_function(clip)
        
        # 2. Apply Dynamic Crop
        def crop_frame(get_frame, t):
            frame = get_frame(t)
            x_start = get_crop_x(t)
            return frame[:, x_start:x_start+new_width]
            
        final_clip = clip.fl(crop_frame)
        
        # C. Write Output
        clean_reason = "".join(x for x in reason if x.isalnum())[:15]
        output_filename = f"outputs/reel_{i+1}_Dynamic_{clean_reason}.mp4"
        
        try:
            final_clip.write_videofile(
                output_filename, 
                codec='libx264', 
                audio_codec='aac', 
                logger=None,
                fps=24 
            )
            generated_files.append(output_filename)
        except Exception as e:
            print(f"[!] Rendering Error: {e}")

    original_clip.close()
    print("=== PIPELINE COMPLETE ===")
    return generated_files

if __name__ == "__main__":
    # Point to your downloaded video
    VIDEO_PATH = "inputs/Input video for ByteSize Hackathon.mp4" 
    process_video(VIDEO_PATH)
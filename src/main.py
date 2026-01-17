import os
from moviepy.editor import VideoFileClip
from content_analyzer import ContentAnalyzer
from vision_engine import VisionEngine
from transcriber import Transcriber
import cv2
import os

def process_video(video_path):
    print(f"=== PROCESSING: {video_path} ===")
    
    # 1. Validation
    if not os.path.exists(video_path):
        print(f"[!] Error: Input file not found at {video_path}")
        return

    # 2. Logic Phase (Librosa Audio Analysis)
    from audio_analyzer import AudioAnalyzer
    analyzer = AudioAnalyzer()
    best_segments = analyzer.get_best_clips(video_path)
    
    if not best_segments:
        print("[!] No clips found. Check API Key or Input Video.")
        return

    # 3. Vision & Captioning Phase
    vision = VisionEngine()
    transcriber = Transcriber()
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
        # Manual crop using fl because moviepy 1.0.3 crop() doesn't support functions well
        def crop_frame(get_frame, t):
            frame = get_frame(t)
            x_start = get_crop_x(t)
            # Slice: [y:y+h, x:x+w]
            # Height is full, so 0:clip.h
            return frame[:, x_start:x_start+new_width]
            
        final_clip = clip.fl(crop_frame)
        
        # C. Transcribe & Captions
        # 1. Export temp audio for simple transcription
        temp_audio = f"temp_clip_{i}.wav"
        clip.audio.write_audiofile(temp_audio, logger=None)
        
        captions = transcriber.transcribe_clip(temp_audio)
        
        # Cleanup temp audio
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
            
        # 2. Burn Captions (Karaoke Style)
        # Group words for display (3-4 words per line)
        word_groups = []
        group_size = 4
        if captions:
            for k in range(0, len(captions), group_size):
                chunk = captions[k:k+group_size]
                if chunk:
                    # Extend end time of group to match start of next group? 
                    # For now just use word bounds.
                    word_groups.append({
                        'start': chunk[0].get('start', 0),
                        'end': chunk[-1].get('end', 0),
                        'words': chunk
                    })

        def process_frame(get_frame, t):
            frame = get_frame(t)
            
            # Find active group
            active_group = None
            for g in word_groups:
                # Add small buffer to keep text visible during pauses
                if g['start'] <= t <= g['end'] + 0.5:
                    active_group = g
                    break
            
            if active_group:
                font = cv2.FONT_HERSHEY_SIMPLEX
                scale = 1.0
                thickness = 3
                spacing = 20
                
                # Measure total width
                total_width = 0
                sizes = []
                for w in active_group['words']:
                    w_text = w.get('word', '')
                    sz = cv2.getTextSize(w_text, font, scale, thickness)[0]
                    sizes.append(sz)
                    total_width += sz[0] + spacing
                total_width -= spacing
                
                # Draw
                start_x = (frame.shape[1] - total_width) // 2
                y = int(frame.shape[0] * 0.85)
                
                curr_x = start_x
                for i, w in enumerate(active_group['words']):
                    w_text = w.get('word', '')
                    sz = sizes[i]
                    
                    # Highlight active word
                    # Color: BGR
                    color = (255, 255, 255) # White
                    if w.get('start', 0) <= t <= w.get('end', 0):
                        color = (0, 255, 255) # Yellow (B=0, G=255, R=255)
                    
                    # Outline
                    cv2.putText(frame, w_text, (curr_x, y), font, scale, (0,0,0), thickness+3, cv2.LINE_AA)
                    # Text
                    cv2.putText(frame, w_text, (curr_x, y), font, scale, color, thickness, cv2.LINE_AA)
                    
                    curr_x += sz[0] + spacing
            
            return frame

        # Apply transformation
        final_clip = final_clip.fl(process_frame)

        # Write Output
        clean_reason = "".join(x for x in reason if x.isalnum())[:15]
        output_filename = f"outputs/reel_{i+1}_Dynamic_{clean_reason}.mp4"
        
        try:
            final_clip.write_videofile(
                output_filename, 
                codec='libx264', 
                audio_codec='aac', 
                logger=None,
                fps=24 # Enforce FPS
            )
            print(f"[+] Saved: {output_filename}")
        except Exception as e:
            print(f"[!] Rendering Error: {e}")

    original_clip.close()
    print("=== PIPELINE COMPLETE ===")

if __name__ == "__main__":
    # Point to your downloaded video
    VIDEO_PATH = "inputs/Input video for ByteSize Hackathon.mp4" 
    process_video(VIDEO_PATH)
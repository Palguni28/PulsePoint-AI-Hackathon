import os
from moviepy.editor import VideoFileClip
from content_analyzer import ContentAnalyzer
from vision_engine import VisionEngine
from transcriber import Transcriber
import cv2
import cv2
import os
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

    # 3. Vision & Captioning Phase
    vision = VisionEngine()
    transcriber = Transcriber()
    original_clip = VideoFileClip(video_path)
    
    print(f"=== RENDERING {len(best_segments)} CLIPS ===")
    
    # Rate Limit Sleep
    import time

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
                    # Look ahead for next chunk start to bridge gap
                    next_start = 0
                    if k + group_size < len(captions):
                        next_start = captions[k+group_size].get('start', 0)
                    else:
                        next_start = chunk[-1].get('end', 0) + 1.5 # Last chunk lingers
                        
                    current_end = chunk[-1].get('end', 0)
                    # Extend end time to next start if gap is small (< 3 sec)
                    if next_start > current_end and (next_start - current_end) < 3.0:
                        group_end = next_start
                    else:
                        group_end = current_end + 0.5

                    word_groups.append({
                        'start': chunk[0].get('start', 0),
                        'end': group_end,
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
                thickness = 2
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
                
                # Coordinates
                start_x = (frame.shape[1] - total_width) // 2
                y = int(frame.shape[0] * 0.85)
                
                # 1. Background Box (Semi-transparent Black)
                padding = 20
                box_x1 = start_x - padding
                box_y1 = y - sizes[0][1] - padding
                box_x2 = start_x + total_width + padding
                box_y2 = y + padding
                
                overlay = frame.copy()
                cv2.rectangle(overlay, (box_x1, box_y1), (box_x2, box_y2), (0, 0, 0), -1)
                alpha = 0.6
                cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
                
                # 2. Draw Words (Pop-in Style)
                curr_x = start_x
                for i, w in enumerate(active_group['words']):
                    w_text = w.get('word', '')
                    sz = sizes[i]
                    
                    # Pop-in logic: Only draw if current time >= start of word
                    if t >= w.get('start', 0):
                        color = (255, 255, 255) # White
                        # Outline
                        # cv2.putText(frame, w_text, (curr_x, y), font, scale, (0,0,0), thickness+2, cv2.LINE_AA)
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
            generated_files.append(output_filename)
        except Exception as e:
            print(f"[!] Rendering Error: {e}")
            
        # Avoid Rate Limits
        print("[*] Sleeping 60s for API Rate Limit...")
        time.sleep(60)

    original_clip.close()
    print("=== PIPELINE COMPLETE ===")
    return generated_files

if __name__ == "__main__":
    # Point to your downloaded video
    VIDEO_PATH = "inputs/Input video for ByteSize Hackathon.mp4" 
    process_video(VIDEO_PATH)
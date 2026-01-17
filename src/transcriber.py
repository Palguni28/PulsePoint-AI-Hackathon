import google.generativeai as genai
import os
import json
import time

class Transcriber:
    def __init__(self):
        print("[*] Initializing Transcriber (Gemini 2.0 Flash Lite)...")
        # Reuse existing env
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def transcribe_clip(self, audio_path):
        """
        Uploads small audio clip and returns JSON timestamps.
        """
        print(f"[*] Transcribing {os.path.basename(audio_path)}...")
        
        # 1. Upload
        try:
            audio_file = genai.upload_file(path=audio_path)
        except Exception as e:
            print(f"[!] Upload failed: {e}")
            return []
            
        # 2. Wait for processing
        while audio_file.state.name == "PROCESSING":
            time.sleep(1)
            audio_file = genai.get_file(audio_file.name)
            
        if audio_file.state.name == "FAILED":
            print("[!] Audio processing failed.")
            return []
            
        # 3. Prompt
        prompt = """
        Transcribe this audio. Return a JSON list of INDIVIDUAL WORDS with timestamps.
        Format: [{"start": 0.5, "end": 0.8, "word": "Hello"}, {"start": 0.9, "end": 1.2, "word": "world"}]
        Ensure "start" and "end" are floats in seconds.
        Combine punctuation with the previous word if needed.
        RETURN JSON ONLY.
        """
        
        retries = 3
        for attempt in range(retries):
            try:
                response = self.model.generate_content([audio_file, prompt])
                text = response.text.replace("```json", "").replace("```", "").strip()
                captions = json.loads(text)
                return captions
            except Exception as e:
                if "429" in str(e):
                    print(f"[!] Rate Limit (429). Retrying in 60s... ({attempt+1}/{retries})")
                    time.sleep(60)
                else:
                    print(f"[!] Transcription error: {e}")
                    return []
        print("[!] Max retries exceeded.")
        return []

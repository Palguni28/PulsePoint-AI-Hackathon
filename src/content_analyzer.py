import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import ast
import time

class ContentAnalyzer:
    def __init__(self):
        # 1. Load Environment Variables
        load_dotenv()
        
        # 2. Fetch Key safely
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("[!] ERROR: GOOGLE_API_KEY not found in .env file")
            
        genai.configure(api_key=api_key)
        
        # Use Gemini 2.0 Flash Lite (Optimized for Quota)
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite')
        print("[*] Gemini 2.0 Flash Lite Loaded")

    def get_best_clips(self, video_path: str):
        print(f"[*] Uploading {os.path.basename(video_path)} to Gemini for analysis...")
        
        # 1. Upload
        video_file = genai.upload_file(path=video_path)
        print(f"[*] Upload Complete. Waiting for processing (File Name: {video_file.name})...")
        
        # 2. Wait for processing (THE FIX: Refresh the file state)
        while video_file.state.name == "PROCESSING":
            print('.', end='', flush=True)
            time.sleep(5) # Check every 5 seconds
            # CRITICAL FIX: Fetch the latest status from the server
            video_file = genai.get_file(video_file.name)
            
        if video_file.state.name == "FAILED":
            raise ValueError("[!] Video processing failed on Google's side.")
            
        print("\n[+] Video Processed.")

        # 3. The Logic Prompt
        prompt = """
        Analyze this video. Identify the 3 most "viral" and educational moments.
        Focus on: High energy, clear "Aha!" moments, and strong advice.
        Each clip must be between 30 and 60 seconds.
        
        Return ONLY a Python list of dictionaries in this exact format:
        [
          {"start": 10.5, "end": 45.0, "reason": "Explanation of failure patterns"},
          {"start": 120.0, "end": 160.0, "reason": "Defining the gap in mentorship"}
        ]
        """

        print("[*] Asking Gemini to find Golden Nuggets...")
        
        response = None
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content([video_file, prompt])
                break
            except Exception as e:
                if "quota" in str(e).lower() or "429" in str(e):
                    print(f"[!] Quota hit. Retrying in 60s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(60)
                else:
                    raise e
        
        if not response:
             raise ValueError("[!] Failed to generate content after retries.")
        try:
            text_data = response.text.replace("```python", "").replace("```json", "").replace("```", "").strip()
            
            try:
                clips = json.loads(text_data)
            except:
                clips = ast.literal_eval(text_data)
                
            print(f"[+] Gemini found {len(clips)} viral clips.")
            return clips
            
        except Exception as e:
            print(f"[!] Parsing Error: {e}")
            print(f"Raw Response: {response.text}")
            return []
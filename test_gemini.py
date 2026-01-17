import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("No API Key found")
else:
    genai.configure(api_key=api_key)
    with open("test_output.txt", "w", encoding="utf-8") as f:
        f.write(f"API Key loaded (length: {len(api_key)})\n")
        f.write("Listing models:\n")
        try:
            found = False
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    f.write(f"- {m.name}\n")
                    if 'gemini-1.5-flash' in m.name:
                        found = True
            
            f.write(f"\nTarget model 'gemini-1.5-flash' found: {found}\n")

            f.write("\nTesting generation:\n")
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Hello")
            f.write(f"Response: {response.text}\n")
        except Exception as e:
            f.write(f"Error during test: {e}\n")

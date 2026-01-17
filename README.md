
# PulsePoint AI 🎬

**PulsePoint AI** is an intelligent video processing tool designed to turn long-form content into viral short clips (Reels/TikToks) instantly. 

Built for the **ByteSize Hackathon**, it uses advanced AI to analyze audio energy, track faces, and generate engaging captions.

## 🚀 Features

*   **AI-Powered curation**: Automatically finds the most energetic/viral moments in a video using Audio Analysis.
*   **Smart Cropping**: Detects faces and crops standard 16:9 video to 9:16 mobile format, keeping the speaker in focus.
*   **Viral Captions**: Adds "Alex Hormozi" style pop-in captions with word-level timing.
*   **Modern UI**: Beautiful Dark Mode interface built with **Flask** and **Pico.css**.
*   **Flexible Input**: Upload local MP4 files or paste a **Google Drive** link.

## 🛠️ Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Palguni28/PulsePoint-AI-Hackathon.git
    cd PulsePoint-AI-Hackathon
    ```

2.  **Set up Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables**
    Create a `.env` file in the root directory and add your Gemini API Key:
    ```
    GOOGLE_API_KEY=your_api_key_here
    ```

## 🏃‍♂️ Usage

1.  **Start the Server**
    ```bash
    python src/app.py
    ```

2.  **Open in Browser**
    Go to `http://localhost:5000`

3.  **Generate Clips**
    *   Upload an MP4 video (or paste a Drive link).
    *   Click "Generate Viral Reels".
    *   Wait for the AI to process (approx. 3-5 minutes for a 10 min video).
    *   Download your clips!

## ☁️ Deployment

**Recommended: Local or Dedicated Server**
Due to the heavy processing requirements (FFmpeg video rendering, Machine Learning models for Audio/Vision), this application **cannot** be hosted on standard "Serverless" platforms like Vercel or Netlify free tiers, as they have strict timeout limits (10-60 seconds) and this pipeline takes minutes to run.

**For a Live Demo:**
We recommend running it locally or deploying to a VPS (user-managed server) like:
*   **Render** (Background Worker/Web Service with high RAM)
*   **Railway**
*   **AWS EC2 / DigitalOcean**

## 🏗️ Built With

*   **Python**: Core logic.
*   **Flask**: Web Backend.
*   **Pico.css**: Frontend Styling.
*   **OpenCV**: Face Detection & Smart Cropping.
*   **Librosa**: Audio Energy Analysis.
*   **MoviePy**: Video Editing & Rendering.
*   **Google Gemini**: Speech-to-Text & AI Transcription.
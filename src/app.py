import os
from flask import Flask, render_template, request, send_from_directory
from main import process_video

app = Flask(__name__)

# Config
BASE_DIR = os.getcwd() # Get current working directory (where python is run from)
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'inputs')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

import gdown

@app.route('/', methods=['GET', 'POST'])
def index():
    generated_videos = []
    loading = False
    
    if request.method == 'POST':
        filename = None
        filepath = None
        
        # 1. Check for File Upload
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
        # 2. Check for Google Drive Link
        elif 'drive_url' in request.form and request.form['drive_url'].strip() != '':
            url = request.form['drive_url'].strip()
            try:
                # Generate a unique name or trust gdown to detect name
                output_path = os.path.join(app.config['UPLOAD_FOLDER'], "drive_video.mp4")
                # gdown.download returns the filename
                downloaded = gdown.download(url, output_path, quiet=False, fuzzy=True)
                if downloaded:
                    filepath = downloaded
                    filename = os.path.basename(downloaded)
                else:
                    return render_template('index.html', error='Failed to download from Google Drive.')
            except Exception as e:
                return render_template('index.html', error=f'GDown Error: {str(e)}')
        
        else:
            return render_template('index.html', error='No file or link provided.')
            
        if filepath:
            # Process
            try:
                # process_video returns absolute or relative paths
                # We need to make them relative to serve them
                full_paths = process_video(filepath)
                
                # Convert to filenames for template
                generated_videos = [os.path.basename(p) for p in full_paths]
            except Exception as e:
                return render_template('index.html', error=f"Processing failed: {str(e)}")

    return render_template('index.html', videos=generated_videos)

@app.route('/outputs/<filename>')
def uploaded_file(filename):
    # For video tag (inline playback)
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

@app.route('/download/<filename>')
def download_file(filename):
    # For download button (force save)
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

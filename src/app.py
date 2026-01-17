import os
from flask import Flask, render_template, request, send_from_directory
from main import process_video

app = Flask(__name__)

# Config
UPLOAD_FOLDER = 'inputs'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    generated_videos = []
    loading = False
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')
        
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='No selected file')
            
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
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
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

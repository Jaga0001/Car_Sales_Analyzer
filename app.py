from flask import Flask, render_template, request, jsonify
import os
import json

# Import the NLP pipeline functions
from model import read_text_files, process_transcripts  # Replace with actual module name

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Process the file using the NLP pipeline
        transcripts = read_text_files(app.config['UPLOAD_FOLDER'])
        results = process_transcripts(transcripts)

        # Return the results as JSON
        return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)





from flask import Flask, render_template, request, jsonify
import os
import shutil

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
        # Clear the upload folder before saving the new file
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                return jsonify({"error": f"Failed to delete {file_path}. Reason: {str(e)}"}), 500

        # Save the new file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Process the file using the NLP pipeline
        transcripts = read_text_files(app.config['UPLOAD_FOLDER'])
        results = process_transcripts(transcripts)

        # Prepare the HTML content for the results
        html_content = '<div id="results">'
        for filename, content in results.items():
            html_content += f'<div class="key-point">'
            html_content += f'<h2>Key points extracted from {filename}</h2>'
            html_content += '<div class="content">'
            
            if "Customer Requirements" in content:
                reqs = content["Customer Requirements"]
                if reqs.get("Budget"):
                    html_content += f'<p>The customer\'s budget is {reqs["Budget"]}.</p>'
                if reqs.get("Car Type"):
                    html_content += f'<p>They are looking for a {reqs["Car Type"]} type of car.</p>'
                if reqs.get("Color"):
                    html_content += f'<p>The preferred color is {reqs["Color"]}.</p>'
                if reqs.get("Fuel Type"):
                    html_content += f'<p>They want a car with {reqs["Fuel Type"]} fuel type.</p>'
                if reqs.get("Transmission Type"):
                    html_content += f'<p>They prefer {reqs["Transmission Type"]} transmission.</p>'

            if "Customer Objections" in content:
                objections = content["Customer Objections"]
                noted_objections = [k for k, v in objections.items() if v]
                if noted_objections:
                    html_content += '<p>The customer has objections related to: ' + ', '.join(noted_objections) + '.</p>'
                else:
                    html_content += '<p>The customer has no objections noted.</p>'

            if "Company Policies Discussed" in content:
                policies = content["Company Policies Discussed"]
                discussed_policies = [k for k, v in policies.items() if v]
                if discussed_policies:
                    html_content += '<p>The following company policies were discussed: ' + ', '.join(discussed_policies) + '.</p>'
                else:
                    html_content += '<p>No company policies were discussed.</p>'

            html_content += '</div></div><br>'
        
        html_content += '</div>'

        return html_content

if __name__ == '__main__':
    app.run(debug=True)

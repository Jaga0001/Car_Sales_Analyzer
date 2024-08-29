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

        # Convert the results to sentences focusing on key points
        key_points = []
        for filename, content in results.items():
            key_points.append(f"Key points extracted from {filename}:")
            
            # Handle specific categories
            if "Customer Requirements" in content:
                reqs = content["Customer Requirements"]
                if reqs.get("Budget"):
                    key_points.append(f"The customer's budget is {reqs['Budget']}.")
                if reqs.get("Car Type"):
                    key_points.append(f"They are looking for a {reqs['Car Type']} type of car.")
                if reqs.get("Color"):
                    key_points.append(f"The preferred color is {reqs['Color']}.")
                if reqs.get("Fuel Type"):
                    key_points.append(f"They want a car with {reqs['Fuel Type']} fuel type.")
                if reqs.get("Transmission Type"):
                    key_points.append(f"They prefer {reqs['Transmission Type']} transmission.")

            if "Customer Objections" in content:
                objections = content["Customer Objections"]
                noted_objections = [k for k, v in objections.items() if v]
                if noted_objections:
                    key_points.append("The customer has objections related to: " + ", ".join(noted_objections) + ".")
                else:
                    key_points.append("The customer has no objections noted.")

            if "Company Policies Discussed" in content:
                policies = content["Company Policies Discussed"]
                discussed_policies = [k for k, v in policies.items() if v]
                if discussed_policies:
                    key_points.append("The following company policies were discussed: " + ", ".join(discussed_policies) + ".")
                else:
                    key_points.append("No company policies were discussed.")
            
            key_points.append("\n")  # Add a newline for readability

        return "<br>".join(key_points)

if __name__ == '__main__':
    app.run(debug=True)

import os
import uuid
from flask import Flask, request, send_from_directory, jsonify, url_for, render_template

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='.')

UPLOAD_FOLDER = 'uploads'
SHARE_LINKS = {}  # In-memory store for shareable links

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Serve index.html
@app.route('/')
def index():
    return render_template('index.html')

# Upload route
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{file.filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({"message": "Uploaded", "filename": filename})
    return jsonify({"error": "No file uploaded"}), 400

# List files
@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify(files)

# Download file
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

# Delete file
@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    try:
        os.remove(os.path.join(UPLOAD_FOLDER, filename))
        return jsonify({"message": "Deleted"})
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

# Create shareable link
@app.route('/share/<filename>', methods=['GET'])
def create_share_link(filename):
    token = str(uuid.uuid4())
    SHARE_LINKS[token] = filename
    return jsonify({"shareable_link": url_for('access_shared_file', token=token, _external=True)})

# Access shared file
@app.route('/shared/<token>', methods=['GET'])
def access_shared_file(token):
    filename = SHARE_LINKS.get(token)
    if filename:
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    return jsonify({"error": "Invalid or expired link"}), 404

if __name__ == '__main__':
    app.run(debug=True)

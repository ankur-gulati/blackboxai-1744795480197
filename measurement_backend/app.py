from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from utils import measure_clothes

app = Flask(__name__, static_folder='../measurement_frontend')
CORS(app)

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/measure', methods=['POST'])
def measure():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload a PNG or JPEG image'}), 400
    
    try:
        # Save the file temporarily
        upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        upload_path = os.path.join(upload_dir, file.filename)
        file.save(upload_path)
        
        # Process the image
        with open(upload_path, 'rb') as f:
            measurements = measure_clothes(f)
        
        # Clean up
        os.remove(upload_path)
        
        return jsonify(measurements)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

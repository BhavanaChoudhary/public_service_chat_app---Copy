import os
import webbrowser
from threading import Timer
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from dwani_demo import describe_image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def serve_index():
    return send_from_directory('templates', 'index.html')
@app.route('/describe-image', methods=['POST'])
def describe_image_endpoint():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    try:
        response = describe_image(filepath)
    except Exception as e:
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500
    try:
        os.remove(filepath)
    except Exception as e:
        print(f"Warning: Could not delete file {filepath}: {e}")
    description = ''
    if isinstance(response, dict) and 'answer' in response:
        description = response['answer']
    else:
        description = str(response)
    return jsonify({'description': description})

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000')

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(host='0.0.0.0', port=5000, debug=True)

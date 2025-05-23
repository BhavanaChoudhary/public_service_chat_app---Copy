import os
import webbrowser
from threading import Timer
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from dwani_demo import describe_image, text_to_speech
from flask import send_file

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

    # Generate TTS audio
    try:
        audio_file = text_to_speech(description)
    except Exception as e:
        print(f"Warning: Could not generate TTS audio: {e}")
        audio_file = None

    audio_url = '/tts-audio' if audio_file else None

    return jsonify({'description': description, 'audio_url': audio_url})

@app.route('/tts-audio')
def serve_tts_audio():
    audio_path = 'output.mp3'
    if os.path.exists(audio_path):
        return send_file(audio_path, mimetype='audio/mpeg')
    else:
        return jsonify({'error': 'Audio file not found'}), 404

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000')

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(host='0.0.0.0', port=5000, debug=True)

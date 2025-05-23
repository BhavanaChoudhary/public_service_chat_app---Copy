import os
import webbrowser
from threading import Timer
from flask import Flask, request, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename
from dwani_demo import describe_image, text_to_speech
import tempfile
import atexit

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size
app.config['TTS_FOLDER'] = 'tts_cache'

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TTS_FOLDER'], exist_ok=True)

# Cleanup function for temporary files
def cleanup():
    for root, dirs, files in os.walk(app.config['TTS_FOLDER']):
        for file in files:
            try:
                os.remove(os.path.join(root, file))
            except Exception as e:
                print(f"Error deleting file {file}: {e}")

atexit.register(cleanup)

@app.route('/')
def serve_index():
    return send_from_directory('templates', 'index.html')

# Removed get_languages endpoint as get_supported_languages is undefined and multilingual support is removed
# @app.route('/languages')
# def get_languages():
#     """Endpoint to get supported languages"""
#     return jsonify(get_supported_languages())

@app.route('/describe-image', methods=['POST'])
def describe_image_endpoint():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Get language from form data (default to Kannada)
    target_lang = request.form.get('language', 'kan_Knda')
    
    try:
        # Secure file handling
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get image description in selected language
        response = describe_image(filepath, tgt_lang=target_lang)
        
        # Standardize response format
        description = response.get('answer', str(response))
        
        # Generate TTS in the same language
        try:
            import uuid
            audio_filename = f"{uuid.uuid4()}.mp3"
            audio_path = os.path.join(app.config['TTS_FOLDER'], audio_filename)
            text_to_speech(description, file_name=audio_path)
            
            return jsonify({
                'description': description,
                'audio_url': f'/tts/{audio_filename}',
                'language': target_lang
            })
        except Exception as e:
            print(f"TTS generation error: {e}")
            return jsonify({
                'description': description,
                'language': target_lang
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        try:
            os.remove(filepath)
        except Exception as e:
            print(f"Warning: Could not delete file {filepath}: {e}")

@app.route('/tts/<filename>')
def serve_tts(filename):
    """Serve generated TTS audio files"""
    try:
        return send_file(
            os.path.join(app.config['TTS_FOLDER'], filename),
            mimetype='audio/mpeg',
            as_attachment=False
        )
    except FileNotFoundError:
        return jsonify({'error': 'Audio file not found'}), 404

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000')

from flask import request

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech_endpoint():
    data = request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    try:
        import uuid
        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_path = os.path.join(app.config['TTS_FOLDER'], audio_filename)
        text_to_speech(text, file_name=audio_path)
        return jsonify({'audio_url': f'/tts/{audio_filename}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(host='0.0.0.0', port=5000, debug=True)

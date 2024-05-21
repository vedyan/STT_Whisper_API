from flask import Flask, request, jsonify, render_template
import os
import threading
from datetime import datetime
from dotenv import load_dotenv
import whisper
import sys

# Load environment variables from .env file
load_dotenv()

# Get the port from the environment variable or use 4000 as default
port = int(os.environ.get("PORT", 4000))

app = Flask(__name__)

# Define a function to load the Whisper model
def load_whisper_model():
    return whisper.load_model("base")

# Initialize model as None
model = None

@app.route('/')
def index():
    return render_template('index.html')

# Define a function to record audio from the microphone
def record_audio(filename, duration):
    os.system(f"arecord -d {duration} -f cd -t wav {filename}")

# Lazy loading of the Whisper model
def get_model():
    global model
    if model is None:
        model = load_whisper_model()
    return model

# Function to get memory usage
def get_memory_usage():
    # Get the memory usage of the current process
    memory_usage = sys.getsizeof(model) if model else 0
    return memory_usage

# Print memory usage to terminal
def print_memory_usage():
    memory_usage = get_memory_usage()
    print(f"Memory Usage: {memory_usage} bytes")

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    try:
        audio_file = request.files['audio']
        if audio_file:
            file_name = f"audio_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
            file_path = os.path.join(app.root_path, file_name)
            audio_file.save(file_path)

        threading.Thread(target=record_audio, args=(file_path, 5)).start()
        
        # Lazy loading of the model
        model = get_model()
        
        # Check if the model is loaded
        if model is None:
            return jsonify({'error': 'Model not loaded yet. Please try again later.'}), 500
        
        # Transcribe the audio using the pre-loaded Whisper model
        result = model.transcribe(file_path)
        transcription = result["text"]

        # Delete the audio file from the local system
        os.remove(file_path)

        # Print memory usage to terminal
        print_memory_usage()

        return jsonify({'transcription': transcription})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)

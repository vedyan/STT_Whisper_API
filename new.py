from flask import Flask, request, jsonify, render_template
import os
import threading
from datetime import datetime
from dotenv import load_dotenv
import whisper

# Load environment variables from .env file
load_dotenv()

# Get the port from the environment variable or use 4000 as default
port = int(os.environ.get("PORT", 4000))

app = Flask(__name__)

# Load the Whisper model for transcription
model = whisper.load_model("base")

@app.route('/')
def index():
    return render_template('index.html')

# Define a function to record audio from the microphone
def record_audio(filename, duration):
    os.system(f"arecord -d {duration} -f cd -t wav {filename}")

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    try:
        audio_file = request.files['audio']
        if audio_file:
            file_name = f"audio_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
            file_path = os.path.join(app.root_path, file_name)
            audio_file.save(file_path)

        threading.Thread(target=record_audio, args=(file_path, 5)).start()
        # Transcribe the audio using the pre-loaded Whisper model
        result = model.transcribe(file_path)
        transcription = result["text"]

        # Delete the audio file from the local system
         # Delete the audio file from the local system
        os.remove(file_path)
        # os.remove("recorded_audio.wav")

        return jsonify({'transcription': transcription})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)

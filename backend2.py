from flask import Flask, render_template, request, jsonify
import os
import whisper
# from pydub import AudioSegment
from dotenv import load_dotenv



app = Flask(__name__)

...

# Load environment variables from .env file
load_dotenv()

# Get the port from the environment variable or use 4000 as default
port = int(os.environ.get("PORT", 4000))
...

# Load the base model
model = whisper.load_model("base")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    try:
        # Check if the 'audio' file is in the request
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'})
        
        audio_file = request.files['audio']
        audio_file.save("recorded_audio.wav")
        
        # Transcribe the audio
        result = model.transcribe("recorded_audio.wav")
        transcription = result["text"]
        return jsonify({'transcription': transcription})
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)




import json
import pyaudio
from vosk import Model, KaldiRecognizer
from pythonosc import udp_client

# Set up Vosk model
model_path = "/Users/julianayoung/vosk_models/vosk-model-small-en-us-0.15"  # Change this to your model path
model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

# Set up OSC client
osc_client = udp_client.SimpleUDPClient("127.0.0.1", 8000)  # Max/MSP IP and port

# Initialize audio input
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)

stream.start_stream()
print("Listening...")

try:
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            text = json.loads(result).get('text', '')
            if text:
                print("Recognized:", text)
                osc_client.send_message("/speech", text)  # Send recognized text to Max/MSP

except KeyboardInterrupt:
    print("Stopping...")

except Exception as e:
    print("Error:", e)

finally:
    # Cleanup
    stream.stop_stream()
    stream.close()
    p.terminate()

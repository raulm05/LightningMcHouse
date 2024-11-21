import sys
import os
import pyaudio
import vosk

folder_path = os.path.join(os.path.dirname(__file__), "model")

if not os.path.exists(folder_path):
    print("Please download a model and unpack it in the 'model' directory.")
    sys.exit(1)

model = vosk.Model(folder_path)
recognizer = vosk.KaldiRecognizer(model, 16000)

mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

while True:
    data = stream.read(4000, exception_on_overflow=False)
    if recognizer.AcceptWaveform(data):
        result = recognizer.Result()
        print(result)
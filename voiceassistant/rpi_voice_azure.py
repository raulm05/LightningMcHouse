import sys
import os
import pyaudio
import vosk
import json


from azure.iot.device import IoTHubDeviceClient, Message

CONNECTION_STRING = "HostName=icaiiiotlabrmg.azure-devices.net;DeviceId=voiceCommands;SharedAccessKey=ajbL79dL9cLnhSydsU3h3i5I7lB5AfwEP/MQk7ltcGk="
KEYWORDS = ["temperatura", "luminosidad", "distancia", "humedad"]

# Initialize Azure IoT Hub Client
client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

folder_path = os.path.join(os.path.dirname(__file__), "model")

if not os.path.exists(folder_path):
    print("Please download a model and unpack it in the 'model' directory.")
    sys.exit(1)

model = vosk.Model(folder_path)
recognizer = vosk.KaldiRecognizer(model, 16000)

mic = pyaudio.PyAudio()
stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()
try:
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            result_dict = json.loads(result)
            command_text = result_dict.get("text", "").strip()
            
            if command_text:
                print(f"Recognized command: {command_text}")
                
                for keyword in KEYWORDS:
                    if keyword in command_text:
                        print(f"Detected keyword: {keyword}")
                        azure_command_message = Message(json.dumps(keyword))
                        azure_command_message.content_encoding='utf-8'
                        azure_command_message.content_type='application/json'
                        
                        try:
                            print(f"Sending command: {keyword}")
                            client.send_message(azure_command_message)
                            print("Message sent successfully!")
                        except Exception as e:
                            print(f"Failed to send message: {e}")
                        break 
                    else:
                        print("No recognizable command detected.")
except KeyboardInterrupt:
    print("Exiting program...")
finally:
    stream.stop_stream()
    stream.close()
    mic.terminate()
    client.shutdown()                   
        
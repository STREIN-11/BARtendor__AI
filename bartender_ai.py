import cv2
import threading
import time
from datetime import datetime
from flask import Flask, request, jsonify
from openai import OpenAI
import edge_tts
import asyncio
import os
import sys
from dotenv import load_dotenv

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    env_path = os.path.join(application_path, '.env')
else:
    application_path = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(application_path, '.env')

load_dotenv(env_path)

app = Flask(__name__)
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

VOICE_FOLDER = os.path.join(application_path, "voice")
os.makedirs(VOICE_FOLDER, exist_ok=True)
print(f"Voice folder: {VOICE_FOLDER}")

conversation_history = []
camera_active = False
greeted_count = 0
last_face_count = 0
VOICE = "en-US-AvaMultilingualNeural"

def get_greeting():
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

async def generate_voice_async(text, filename="response.mp3"):
    filepath = os.path.join(VOICE_FOLDER, filename)
    clean = text.replace(",", " ").replace("!", ".").replace("...", " ").replace("  ", " ").strip()
    communicate = edge_tts.Communicate(clean, VOICE, rate="+6%", pitch="+2Hz")
    await communicate.save(filepath)
    return filepath

def generate_voice(text, filename="response.mp3"):
    return asyncio.run(generate_voice_async(text, filename))

def process_conversation(user_message):
    conversation_history.append({"role": "user", "content": user_message})
    
    system_prompt = {
        "role": "system",
        "content": "You are a friendly, flirty female bartender named Emma. Keep responses short, casual, and bar-appropriate. Use playful language and make customers feel welcome. Remember the conversation context and respond accordingly. Speak in a smooth flowing way with no commas, no ellipses, and no exclamation marks. Write as if speaking out loud naturally."
    }
    
    print(f"\nConversation history ({len(conversation_history)} messages):")
    for msg in conversation_history[-5:]:
        print(f"  {msg['role']}: {msg['content'][:50]}...")
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[system_prompt] + conversation_history
    )
    
    ai_response = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": ai_response})
    generate_voice(ai_response)
    return ai_response

def get_dynamic_greeting():
    time_greeting = get_greeting()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "system",
            "content": f"You are a friendly, flirty female bartender. Generate a single short greeting for a customer entering the bar. Include '{time_greeting}' and make it casual, welcoming, and bar-appropriate. Keep it under 20 words. No commas, no ellipses, no exclamation marks. Write as if speaking out loud naturally."
        }]
    )
    return response.choices[0].message.content

def detect_person():
    global camera_active, greeted_count, last_face_count
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    
    no_face_counter = 0
    reset_scheduled = False
    
    while camera_active:
        ret, frame = cap.read()
        if not ret:
            time.sleep(1)
            continue
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        frontal_faces = []
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
            if len(eyes) >= 2:
                frontal_faces.append((x, y, w, h))
        
        current_frontal_count = len(frontal_faces)
        
        if len(faces) > 0:
            no_face_counter = 0
            reset_scheduled = False
            
            if current_frontal_count > greeted_count:
                new_people = current_frontal_count - greeted_count
                for i in range(new_people):
                    greeted_count += 1
                    print(f"New person detected! Greeting...")
                    initial_message = get_dynamic_greeting()
                    conversation_history.append({"role": "assistant", "content": initial_message})
                    generate_voice(initial_message, "greeting.mp3")
                    print(f"Greeting: {initial_message}")
                    time.sleep(2)
        else:
            no_face_counter += 1
            if no_face_counter > 10 and not reset_scheduled:
                greeted_count = 0
                conversation_history.clear()
                reset_scheduled = True
                print("All customers left. Conversation reset.")
        
        last_face_count = len(faces)
        time.sleep(1)
    
    cap.release()

@app.route('/start', methods=['POST'])
def start_camera():
    global camera_active
    if not camera_active:
        camera_active = True
        threading.Thread(target=detect_person, daemon=True).start()
        return jsonify({"status": "Camera started"})
    return jsonify({"status": "Already running"})

@app.route('/stop', methods=['POST'])
def stop_camera():
    global camera_active
    camera_active = False
    return jsonify({"status": "Camera stopped"})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    
    ai_response = process_conversation(user_message)
    
    return jsonify({
        "response": ai_response,
        "audio_file": "response.mp3",
        "greeting": get_greeting()
    })

@app.route('/reset', methods=['POST'])
def reset():
    global conversation_history, greeted_count
    conversation_history = []
    greeted_count = 0
    return jsonify({"status": "Conversation reset"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

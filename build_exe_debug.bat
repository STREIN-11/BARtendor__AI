pyinstaller --onefile --name BartenderAI_Debug --add-data "voice;voice" --add-data ".env;." --hidden-import=edge_tts --hidden-import=openai --hidden-import=dotenv --hidden-import=cv2 --collect-all edge_tts bartender_ai.py
pause

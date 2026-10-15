import os
import sys
import re
import time
import shutil
import queue
import threading
import urllib.parse
import webbrowser
import subprocess
import datetime
import ctypes
import psutil
import requests
import pyttsx3
import speech_recognition as sr
from flask import Flask, jsonify, request
from flask_cors import CORS
import webview

# Bundled Resource Path Resolver for PyInstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if getattr(sys, 'frozen', False):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

app = Flask(__name__)
CORS(app)

# Global State Management Engine
state_lock = threading.Lock()
system_status = "PROCESSING"
mic_active = False
messages = []
message_id_counter = 0

speak_queue = queue.Queue()

# Thread-Safe Voice Synthesizer Worker
def tts_worker():
    global system_status
    engine = pyttsx3.init()
    engine.setProperty('rate', 170)
    voices = engine.getProperty('voices')
    for voice in voices:
        if "david" in voice.name.lower() or "male" in voice.name.lower() or "zira" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

    while True:
        text = speak_queue.get()
        if text is None: break
        
        with state_lock: 
            system_status = "SPEAKING"
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception: 
            pass
        
        with state_lock: 
            system_status = "PROCESSING"
        speak_queue.task_done()

threading.Thread(target=tts_worker, daemon=True).start()

def add_message(user_msg=None, jarvis_msg=None):
    global message_id_counter
    with state_lock:
        message_id_counter += 1
        item = {"id": message_id_counter}
        if user_msg: item["user"] = user_msg
        if jarvis_msg: 
            item["jarvis"] = jarvis_msg
            speak_queue.put(jarvis_msg)
        messages.append(item)

# Native Windows Virtual Key Injection (Hardware Level)
def press_key(vk_code, count=1):
    for _ in range(count):
        ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)
        time.sleep(0.05)

# UNIVERSAL INTENT RESOLUTION ENGINE (ONLINE + OFFLINE)
def execute_command(raw_text):
    text = raw_text.lower().strip()
    clean_text = re.sub(r'\b(jarvis|please|can you|could you|would you|kindly|for me|navigate|go to|take me to|open up|show me|run|start)\b', '', text).strip()

    # 1. HARDWARE MEDIA & VOLUME CONTROL (OFFLINE)
    if "volume up" in text or "increase volume" in text or "volume higher" in text:
        press_key(0xAF, 5) # VK_VOLUME_UP
        return "Increasing audio output level."
    if "volume down" in text or "decrease volume" in text or "volume lower" in text:
        press_key(0xAE, 5) # VK_VOLUME_DOWN
        return "Decreasing audio output level."
    if "mute" in text or "unmute" in text or "silence volume" in text:
        press_key(0xAD, 1) # VK_VOLUME_MUTE
        return "Toggling master audio mute."
    if any(k in text for k in ["pause music", "pause video", "play music", "play video", "pause media", "resume media"]):
        press_key(0xB3, 1) # VK_MEDIA_PLAY_PAUSE
        return "Toggling media playback."
    if "next track" in text or "next song" in text:
        press_key(0xB0, 1) # VK_MEDIA_NEXT_TRACK
        return "Skipping to next media item."
    if "previous track" in text or "previous song" in text:
        press_key(0xB1, 1) # VK_MEDIA_PREV_TRACK
        return "Returning to previous media item."

    # 2. SYSTEM POWER DIRECTIVES (OFFLINE)
    if any(k in text for k in ["lock pc", "lock computer", "lock screen", "lock workstation"]):
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return "Workstation secured. Screen locked."
    if "shutdown system" in text or "turn off pc" in text or "shutdown computer" in text:
        os.system("shutdown /s /t 10")
        return "Initiating computer shutdown sequence in 10 seconds."
    if "restart system" in text or "reboot computer" in text or "restart pc" in text:
        os.system("shutdown /r /t 10")
        return "Initiating system reboot sequence in 10 seconds."
    if "cancel shutdown" in text or "abort shutdown" in text:
        os.system("shutdown /a")
        return "System power state termination aborted."

    # 3. DATE & TIME QUERIES (OFFLINE)
    if any(k in text for k in ["time", "clock"]):
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"Current local time is {now}."
    if any(k in text for k in ["date", "day", "today"]):
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {today}."

    # 4. SYSTEM DIAGNOSTICS & HARDWARE INFO (OFFLINE)
    if any(k in text for k in ["cpu usage", "processor load", "ram usage", "memory status", "system stats"]):
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        return f"System Diagnostics: CPU utilization is at {cpu} percent. Memory allocation is at {ram} percent."

    # 5. DYNAMIC PROCESS TERMINATION (CLOSES ANY PROGRAM ON EARTH - OFFLINE)
    if any(k in text for k in ["close", "kill", "terminate", "stop", "exit"]):
        target = re.sub(r'\b(close|kill|terminate|stop|exit|app|application|program|process)\b', '', clean_text).strip()
        if not target:
            return "Specify the target application to terminate."

        terminated_count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pname = proc.info['name'].lower()
                if target in pname or pname.replace(".exe", "") in target:
                    proc.kill()
                    terminated_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        if terminated_count > 0:
            return f"Successfully terminated all processes matching '{target}' ({terminated_count} instance(s))."
        
        # Fallback to direct Windows Taskkill command
        subprocess.run(f"taskkill /F /IM {target}.exe /T", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Attempted process termination protocol on {target}."

    # 6. LOCAL WINDOWS SHELL DIRECTORIES & DRIVES (OFFLINE)
    local_nav_map = {
        ("this pc", "my pc", "my computer", "computer"): "explorer.exe shell:::{20D04FE0-3AEA-1069-A2D8-08002B30309D}",
        ("recycle bin", "trash"): "explorer.exe shell:::{645FF040-5081-101B-9F08-00AA002F954E}",
        ("control panel",): "control.exe",
        ("settings", "pc settings", "windows settings"): "start ms-settings:",
        ("task manager", "taskmgr"): "start taskmgr",
        ("command prompt", "cmd", "terminal"): "start cmd"
    }

    for key_tuple, cmd in local_nav_map.items():
        if any(k in text for k in key_tuple):
            os.system(cmd)
            return f"Opening local shell sector: {key_tuple[0].title()}."

    # DISK PARTITIONS (e.g., "C drive", "D drive")
    drive_match = re.search(r'\b([a-z])\s*(drive|disk)\b', text)
    if drive_match:
        drive_letter = drive_match.group(1).upper()
        drive_path = f"{drive_letter}:\\"
        if os.path.exists(drive_path):
            os.startfile(drive_path)
            return f"Accessing local disk partition {drive_letter}:\\"
        return f"Partition {drive_letter}:\\ was not detected on local hardware."

    # SPECIAL USER DIRECTORIES
    user_home = os.path.expanduser("~")
    special_folders = {
        ("downloads", "download folder"): os.path.join(user_home, "Downloads"),
        ("documents", "my documents"): os.path.join(user_home, "Documents"),
        ("desktop",): os.path.join(user_home, "Desktop"),
        ("pictures", "photos"): os.path.join(user_home, "Pictures"),
        ("videos", "movies"): os.path.join(user_home, "Videos"),
        ("music",): os.path.join(user_home, "Music")
    }

    for key_tuple, folder_path in special_folders.items():
        if any(k in text for k in key_tuple):
            if os.path.exists(folder_path):
                os.startfile(folder_path)
                return f"Accessing directory: {key_tuple[0].title()}."

    # 7. FILE AND FOLDER CREATION / DELETION (OFFLINE)
    if any(k in text for k in ["create folder", "make folder", "new folder", "create directory"]):
        folder_name = re.sub(r'\b(create|make|new|folder|directory|called|named)\b', '', clean_text).strip()
        if not folder_name: folder_name = "New_JARVIS_Directory"
        target_path = os.path.join(user_home, "Desktop", folder_name)
        os.makedirs(target_path, exist_ok=True)
        return f"Created directory '{folder_name}' on Desktop."

    if any(k in text for k in ["delete folder", "remove folder", "destroy folder", "delete file", "remove file"]):
        target_name = re.sub(r'\b(delete|remove|destroy|folder|file|directory|called|named)\b', '', clean_text).strip()
        if target_name:
            target_path = os.path.join(user_home, "Desktop", target_name)
            if os.path.exists(target_path):
                if os.path.isdir(target_path): shutil.rmtree(target_path)
                else: os.remove(target_path)
                return f"Purged target '{target_name}' from Desktop."
            return f"Target '{target_name}' not located on Desktop."

    # 8. YOUTUBE PLAYBACK & VIDEO SEARCH (ONLINE)
    if "youtube" in text or "play" in text or "watch" in text:
        query = re.sub(r'\b(play|on|youtube|watch|video|search|for)\b', '', clean_text).strip()
        if query:
            encoded_query = urllib.parse.quote(query)
            webbrowser.open(f"https://www.youtube.com/results?search_query={encoded_query}")
            return f"Executing YouTube media directive for '{query}'."
        else:
            webbrowser.open("https://www.youtube.com")
            return "Opening YouTube main interface."

    # 9. DIRECT URL & WEB SEARCH (ONLINE)
    if any(domain_ext in text for domain_ext in [".com", ".org", ".net", ".io", ".gov", ".edu", ".ai"]):
        url = clean_text if clean_text.startswith("http") else f"https://{clean_text}"
        webbrowser.open(url)
        return f"Navigating directly to web address: {url}"

    if any(k in text for k in ["search", "google", "look up", "browse", "find online"]):
        query = re.sub(r'\b(search|google|look|up|find|online|web|for|about|browse)\b', '', clean_text).strip()
        if query:
            webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(query)}")
            return f"Initiating web search protocol for '{query}'."

    # 10. LOCAL SOFTWARE LAUNCHING (OFFLINE)
    if any(k in text for k in ["open", "launch"]):
        app_name = clean_text.strip()
        app_launch_map = {
            "edge": "msedge",
            "microsoft edge": "msedge",
            "chrome": "chrome",
            "google chrome": "chrome",
            "notepad": "notepad",
            "calculator": "calc",
            "paint": "mspaint",
            "word": "winword",
            "excel": "excel",
            "powerpoint": "powerpnt",
            "spotify": "spotify",
            "vscode": "code",
            "code": "code"
        }
        for key, cmd in app_launch_map.items():
            if key in app_name:
                os.system(f"start {cmd}")
                return f"Launching application: {key.title()}."
        
        # Generic system start attempt for any installed app
        try:
            os.system(f"start {app_name}")
            return f"Attempting execution of '{app_name}' via Windows System Shell."
        except Exception:
            pass

    # 11. SYSTEM IDENTITY & CREDITS
    if any(k in text for k in ["who are you", "identity", "project", "signature", "creator"]):
        return "I am J.A.R.V.I.S., core operating intelligence for The Silent Exploit Base Project for learning. Signature: AR-Jatala."

    # 12. FALLBACK EXECUTION: ONLINE SEARCH & KNOWLEDGE FETCHING
    encoded_query = urllib.parse.quote(raw_text)
    webbrowser.open(f"https://www.google.com/search?q={encoded_query}")
    return f"Directive unmapped in local core database. Initiating web search for: '{raw_text}'"

# SPEECH RECOGNITION WORKER THREAD
def listening_worker():
    global system_status, mic_active
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    
    while True:
        with state_lock:
            current_mic = mic_active
            current_status = system_status

        if current_mic and current_status != "SPEAKING":
            with state_lock: system_status = "LISTENING"
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    audio = recognizer.listen(source, timeout=3, phrase_time_limit=6)
                
                with state_lock: system_status = "PROCESSING"
                text = recognizer.recognize_google(audio)
                
                if text:
                    add_message(user_msg=text)
                    response = execute_command(text)
                    add_message(jarvis_msg=response)
                    
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                pass
            except Exception:
                with state_lock: mic_active = False 
        else:
            if current_status == "LISTENING":
                with state_lock: system_status = "PROCESSING"
            time.sleep(0.3)

threading.Thread(target=listening_worker, daemon=True).start()

# REST API ENDPOINTS FOR FRONTEND UPLINK
@app.route('/')
def serve_frontend():
    html_file = resource_path('index.html')
    with open(html_file, 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/poll', methods=['GET'])
def poll():
    since_id = request.args.get('since', 0, type=int)
    with state_lock:
        new_items = [m for m in messages if m["id"] > since_id]
        current_status = system_status
    return jsonify({"status": current_status, "items": new_items})

@app.route('/api/sysinfo', methods=['GET'])
def sysinfo():
    return jsonify({
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent
    })

@app.route('/api/toggle_mic', methods=['POST'])
def toggle_mic():
    global mic_active
    with state_lock:
        mic_active = not mic_active
        current_mic = mic_active
    
    if current_mic: 
        add_message(jarvis_msg="Audio input active. All offline and online systems monitoring.")
    else: 
        add_message(jarvis_msg="Audio input deactivated.")
    
    return jsonify({"mic_active": current_mic})

def start_flask():
    app.run(host='127.0.0.1', port=5000, threaded=True, debug=False, use_reloader=False)

if __name__ == '__main__':
    add_message(jarvis_msg="JARVIS Core initialized. The Silent Exploit Base Project for learning online. Signature: AR-Jatala.")
    threading.Thread(target=start_flask, daemon=True).start()
    
    webview.create_window('JARVIS Core', 'http://127.0.0.1:5000/', width=1366, height=768, background_color="#050a10")
    webview.start()
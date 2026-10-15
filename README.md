J.A.R.V.I.S.
Standalone Desktop AI Assistant & Cyberpunk Neural HUD
System Version: v2.5    Platform: Windows    Architecture: Offline + Online
DEPLOYMENT & OPERATIONS GUIDE
A complete setup, configuration, command reference, runtime architecture, build, deployment, troubleshooting, and
security guide.
J.A.R.V.I.S. v2.5  •  Page 1
1. Project Overview
J.A.R.V.I.S. is a desktop-based AI assistant designed to provide natural-language and voice-based control of a
Windows computer.
The system combines AI-powered processing, speech recognition, text-to-speech, Windows application control,
process management, filesystem operations, system telemetry, power controls, web navigation, YouTube search,
and a cyberpunk-style graphical interface.
Offline System Control: Local commands can operate without Gemini, depending on the specific feature.
Online AI Services: Gemini and web-based features require an Internet connection.
2. System Requirements
Hardware: Windows 10/11, 4 GB RAM minimum, 8 GB recommended, dual-core processor or better, microphone,
speakers/headphones.
Software: Python 3.x, pip, PowerShell or Command Prompt. Internet is required for package installation and online
AI/web features.
3. Dependencies
Create requirements.txt in the project root:
flask
flask-cors
send2trash
psutil
requests
scikit-learn
pywebview
pyttsx3
SpeechRecognition
PyAudio
pyinstaller
pip install -r requirements.txt
# Or:
python -m pip install --upgrade pip
pip install Flask flask-cors pywebview pyttsx3 SpeechRecognition psutil PyAudio scikit-learn requests send2trash pyinstaller
4. Gemini API Configuration
J.A.R.V.I.S. uses Google's Gemini API for AI-powered processing. Never hard-code a real API key into source code
or publish it in a repository.
# Windows CMD
set GEMINI_API_KEY=your_api_key_here
# PowerShell
$env:GEMINI_API_KEY="your_api_key_here"
# Linux/macOS
export GEMINI_API_KEY="your_api_key_here"
# Verify in PowerShell
echo $env:GEMINI_API_KEY
5. Recommended Project Structure
JARVIS/
n
nnn app.py
J.A.R.V.I.S. v2.5  •  Page 2
nnn index.html
nnn requirements.txt
nnn README.md
n
nnn assets/
n   nnn images/
n   nnn sounds/
n   nnn icons/
n
nnn modules/
nnn commands.py
nnn system.py
nnn voice.py
nnn ai.py
app.py acts as the main application and command router. index.html contains the HUD. Voice, AI, and system
modules can be separated for maintainability.
6. Starting J.A.R.V.I.S.
Navigate to the project directory, install dependencies, configure the API key, then start the application:
cd path\to\JARVIS
pip install -r requirements.txt
$env:GEMINI_API_KEY="your_api_key_here"
python app.py
7. Runtime Architecture
USER / MICROPHONE
n
t
SPEECH RECOGNITION
n
t
COMMAND ROUTER (app.py)
n
nnnnnnnnnnnnn
t           
t
OFFLINE     ONLINE
SYSTEM      AI/WEB
CONTROL     SERVICES
n           
n
Apps/Files  Gemini/Search/
System      YouTube/Web
nnnnnnnnnnnnn
t
CYBERPUNK HUD
n
t
TEXT-TO-SPEECH
8. Offline Command Protocols
Application Launching: “Open Spotify”, “Launch Chrome”, “Open VS Code”, “Start Notepad”, “Open Word”, “Open
Excel”, “Open Paint”.
Process Management: “Close Edge”, “Kill Chrome”, “Terminate Spotify”, “Close Notepad”. Uses psutil or Windows
task management.
Windows Navigation: “Open This PC”, “Open Recycle Bin”, “Open Control Panel”, “Open Settings”, “Open Task
Manager”.
Directories: “Open Downloads”, “Open Documents”, “Open Desktop”, “Open Pictures”, “Open C Drive”, “Open D
Drive”.
J.A.R.V.I.S. v2.5  •  Page 3
Filesystem: “Create folder named Projects”, “Delete folder named Test”. send2trash can be used for safer
recycling.
Media: “Volume up”, “Volume down”, “Mute”, “Pause music”, “Play music”, “Next track”, “Previous track”.
Power: “Lock PC”, “Shutdown system”, “Restart system”, “Cancel shutdown”. Power commands should ideally
require confirmation.
Diagnostics: “What time is it?”, “What is today's date?”, “CPU usage”, “RAM usage”. psutil can provide telemetry.
9. Online Web Commands
YouTube: “Play quantum physics tutorial on YouTube” or “Watch lo-fi hip hop on YouTube”.
Web navigation: “Navigate to github.com” or “Open wikipedia.org”.
Search: “Search Google for cybersecurity basics” or “Look up the latest news online”.
10. Voice System
Speech-to-Text: SpeechRecognition can capture microphone input and use a supported recognition backend.
Text-to-Speech: pyttsx3 provides local speech synthesis; Windows can use SAPI5.
11. Cyberpunk HUD
The interface can use HTML, CSS and JavaScript rendered through pywebview. The HUD can display system
status, CPU/RAM telemetry, current commands, AI responses, voice state, and online/offline status.
HTML/CSS/JavaScript
n
t
Cyberpunk HUD
n
t
     pywebview
n
t
 Python Backend
n
t
 J.A.R.V.I.S. Core
12. Offline vs Online
No Internet normally required: application launching, process management, CPU/RAM monitoring, folders, local
filesystem operations, and Windows power controls.
Internet required: Gemini AI, Google/web search, YouTube search, and online information. Voice recognition
requirements depend on the selected STT backend.
13. Build the Windows EXE
Close any running instance and clean previous build artifacts:
Stop-Process -Name "JARVIS" -Force -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force *.spec -ErrorAction SilentlyContinue
python -m pip install --upgrade pyinstaller
One-file build:
python -m PyInstaller --noconsole --onefile --add-data "index.html;." --hidden-import pyttsx3.drivers.sapi5 --hidden-import speech_recognition app.py --name "JARVIS
J.A.R.V.I.S. v2.5  •  Page 4
Directory build:
python -m PyInstaller --onedir --noconsole --add-data "index.html;." --hidden-import pyttsx3.drivers.sapi5 --hidden-import speech_recognition app.py --name "JARVIS
14. Deploying the EXE
After a successful build, the executable is normally located at dist\JARVIS.exe. To copy it to the current user's
Desktop:
Move-Item -Force "dist\JARVIS.exe" "$env:USERPROFILE\Desktop\JARVIS.exe" 
15. API Key Security
Packaging Python into an EXE does not inherently protect an API key. A key embedded in the executable may be
extractable. Prefer environment variables, secure credential storage, or a backend service for production
deployments.
If a real key is exposed publicly, revoke or rotate it immediately.
16. Security Model
Because J.A.R.V.I.S. can execute system actions, AI-generated text should not be treated as unrestricted shell
commands.
Recommended flow:
User Input
fl
Speech Recognition
fl
Command Classification
fl
Allowed Command Registry
fl
Validation
fl
Optional Confirmation
fl
Execution
The AI should determine intent, while a controlled local command layer determines what actions are actually
allowed. Never allow arbitrary AI-generated shell commands to execute automatically.
17. Troubleshooting
pip not recognized: use python -m pip.
Python not recognized: install Python and ensure it is available in PATH.
PyAudio installation failure: verify your Python version and Windows architecture are compatible with the
available package.
No voice: check Windows audio output, SAPI5, pyttsx3, and speech settings.
Microphone failure: check Windows microphone permissions and the selected input device.
Gemini failure: verify the GEMINI_API_KEY environment variable and restart the application.
18. Example Interactions
USER: "JARVIS, open VS Code."
JARVIS: "Opening Visual Studio Code."
USER: "JARVIS, what's my CPU usage?"
J.A.R.V.I.S. v2.5  •  Page 5
JARVIS: "Current CPU utilization is 24 percent."
USER: "JARVIS, explain quantum computing."
fi Request is sent to Gemini fi Response returned fi HUD + voice output.
USER: "JARVIS, search Google for C++ tutorials."
fi Search query generated fi Browser opens.
19. Complete Operational Flow
USER
n
t
MICROPHONE
n
t
SPEECH RECOGNITION
n
t
COMMAND PROCESSOR
n
nnnnnnnnnnnnnnnnn
t               
t
LOCAL ENGINE   ONLINE ENGINE
n               
n
Apps/Files/     Gemini/Search/
System/Media    YouTube/Web
nnnnnnnnnnnnnnnnn
t
   RESULT / TEXT
n       
t       
n
t
     HUD   TEXT-TO-SPEECH
n
t
             USER
20. Quick Start
cd path\to\JARVIS
python -m pip install --upgrade pip
pip install -r requirements.txt
$env:GEMINI_API_KEY="YOUR_API_KEY"
python app.py
# Build EXE
python -m PyInstaller --noconsole --onefile --add-data "index.html;." --hidden-import pyttsx3.drivers.sapi5 --hidden-import speech_recognition app.py --name "JARVIS"
# Output
dist\JARVIS.exe
J.A.R.V.I.S. v2.5  •  Page 6
J.A.R.V.I.S. SYSTEM STATUS
nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn
n
          J.A.R.V.I.S. v2.5             
n
nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn
n AI ENGINE        : GEMINI               
n
n VOICE INPUT      : SPEECH RECOGNITION   
n VOICE OUTPUT     : SAPI5 / PYTTSX3      
n SYSTEM CONTROL   : PYTHON / WINDOWS     
n TELEMETRY        : PSUTIL               
n WEB INTERFACE    : PYWEBVIEW            
n FRONTEND         : HTML / CSS / JS      
n BUILD ENGINE     : PYINSTALLER          
n MODE             : OFFLINE + ONLINE     
n STATUS           : ONLINE               
n
n
n
n
n
n
n
n
n
nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn
End of J.A.R.V.I.S. Deployment & Operations Guide
J.A.R.V.I.S. v2.5  •  Page 7

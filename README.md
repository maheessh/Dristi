📌 Dristhi - Smart Assistive Bag
🚀 Empowering visually impaired individuals with AI-powered navigation, real-time object detection, health monitoring, and emergency response.


🔍 Overview
Imagine a world where navigation, safety, and real-time awareness are seamlessly integrated into a smart wearable bag—that’s Dristhi! This AI-powered assistive bag is designed to empower visually impaired users, providing:
✔ Real-time object & distance detection
✔ Voice-guided navigation
✔ Health monitoring (posture, temperature, emergency alerts)
✔ AI-powered assistance for everyday tasks

With Dristhi, visually impaired individuals can move with confidence, independence, and security.

✨ Features
🔹 👀 Real-Time Object Detection
Uses YOLOv5 + MediaPipe for detecting people, objects, and distances.
Alerts the user with voice feedback about surroundings.
🔹 🗺️ Voice-Guided Navigation
Google Maps API integration for real-time navigation.
Step-by-step voice instructions like Google Maps for the blind.
🔹 ⚕️ Health Monitoring
Posture & Temperature Tracking to ensure user well-being.
Emergency SOS alert system for critical situations.
🔹 🎤 Wake-Word Activated AI Assistant
Responds to "Hello Dristhi" and executes voice commands.
Reads out important updates and messages.
⚙️ Installation & Setup
🛠️ Prerequisites
Ensure you have the following installed:

Python 3.9+
pip package manager
Arduino connected to system
📥 Clone the Repository
bash
Copy
Edit
git clone https://github.com/yourusername/dristhi.git
cd dristhi
📦 Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
🔑 Set Up Google API Key
Get a Google Maps API Key from Google Cloud Console.
Set up the API key in your environment variables:
bash
Copy
Edit
export GOOGLE_MAPS_API_KEY="your_api_key_here"
Windows Users:
powershell
Copy
Edit
$env:GOOGLE_MAPS_API_KEY="your_api_key_here"
🚀 Usage
1️⃣ Start Object & Distance Detection
Run the AI-powered object detection system with voice assistance:

bash
Copy
Edit
python object_distance_detector.py
Detects objects and people
Announces their distance
Works without lag, thanks to multi-threading
2️⃣ Voice-Guided Navigation
Activate navigation mode with step-by-step voice guidance:

bash
Copy
Edit
python navigation.py
Uses speech recognition to detect the user’s destination.
Guides the user step by step, like Google Maps for the blind.
Provides text + voice instructions until the user reaches the destination.
3️⃣ Start UI Application
For a user-friendly interface, launch the Dristhi UI:

bash
Copy
Edit
python main.py
Start/Stop object detection via button controls.
Monitor health parameters from the Health tab.
View the real-time camera feed with object detection overlays.
🖥️ Project Structure
bash
Copy
Edit
Dristhi/
│── object_distance_detector.py  # AI-powered Object & Distance Detection
│── navigation.py                # Google Maps Voice Navigation
│── main.py                      # UI Application (Tkinter)
│── ui.py                         # UI Elements & Components
│── speech_service.py             # Voice Processing Module
│── hardware_data.py              # Arduino Health Monitoring
│── requirements.txt              # Python Dependencies
│── README.md                     # This Documentation
🤝 Contributing
Want to improve Dristhi? Contributions are welcome!
🔹 Fork the repository
🔹 Create a new branch (feature-new-idea)
🔹 Commit your changes
🔹 Open a Pull Request

Let's build technology for accessibility and empowerment!

🚀 Dristhi – Empowering Lives with AI & Smart Assistive Tech! 🚀


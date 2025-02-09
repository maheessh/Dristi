import tkinter as tk
from tkinter import ttk
import threading
import cv2
from PIL import Image, ImageTk
from tts_service import TextToSpeechService
from hardware_data import HardwareMonitor


class DristhiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dristhi - Assistive Wearable App")
        self.root.geometry("900x700")
        self.root.configure(bg="#1E1E1E")

        self.tts_service = TextToSpeechService()

        self.notebook = ttk.Notebook(root)
        self.home_tab = ttk.Frame(self.notebook)
        self.health_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.home_tab, text="Home")
        self.notebook.add(self.health_tab, text="Health")
        self.notebook.pack(expand=True, fill="both")

        self.setup_home_tab()
        self.setup_health_tab()

        self.object_detection_callback = None
        self.audio_enabled = True

        # OpenCV Camera Feed
        self.cap = cv2.VideoCapture(0)
        self.update_camera_feed()

    def setup_home_tab(self):
        """Setup UI elements for the Home tab."""
        label = tk.Label(
            self.home_tab,
            text="Dristhi - Assistive Wearable",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#1E1E1E"
        )
        label.pack(pady=15)

        control_frame = tk.Frame(self.home_tab, bg="#1E1E1E")
        control_frame.pack(pady=10, padx=20, fill=tk.X)

        self.toggle_audio_button = tk.Button(
            control_frame,
            text="Toggle Audio (ON)",
            command=self.toggle_audio,
            font=("Arial", 12, "bold"),
            bg="#28A745",
            fg="white",
            relief="raised",
            bd=3
        )
        self.toggle_audio_button.pack(pady=10, fill=tk.X)

        camera_button = tk.Button(
            control_frame,
            text="Start Object & Face Detection",
            command=self.start_object_detection,
            font=("Arial", 12, "bold"),
            bg="#FF5733",
            fg="white",
            relief="raised",
            bd=3
        )
        camera_button.pack(pady=10, fill=tk.X)

        self.camera_feed_label = tk.Label(self.home_tab)
        self.camera_feed_label.pack(pady=20)

        self.speech_label = tk.Label(
            self.home_tab,
            text="Detected: None",
            font=("Arial", 12),
            fg="#00A8E8",
            bg="#1E1E1E"
        )
        self.speech_label.pack(pady=10)

    def setup_health_tab(self):
        """Setup UI elements for the Health tab (Hardware Data)."""
        self.hardware_monitor = HardwareMonitor(self.health_tab)

    def toggle_audio(self):
        """Toggle audio announcements for object detection."""
        self.audio_enabled = not self.audio_enabled
        self.toggle_audio_button.config(text=f"Toggle Audio ({'ON' if self.audio_enabled else 'OFF'})")

    def update_camera_display(self, detected_text, distance=None):
        """Update UI with detected objects and handle optional distance."""
        display_text = f"Objects: {detected_text if detected_text else 'None'}"
    
        # ✅ Only add distance if it is not None
        if distance is not None:
            display_text += f", Distance: {distance:.2f} cm"

        self.speech_label.config(text=display_text)

    def update_camera_feed(self):
        """Continuously capture frames from OpenCV and display in Tkinter UI."""
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (400, 300))
            img = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.camera_feed_label.config(image=img)
            self.camera_feed_label.image = img

        self.root.after(500, self.update_camera_feed)

    def set_object_detection_callback(self, callback):
        self.object_detection_callback = callback

    def start_object_detection(self):
        if self.object_detection_callback:
            self.object_detection_callback()

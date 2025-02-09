import cv2
import torch
import easyocr
import pyttsx3
import threading
import time
import numpy as np
import mediapipe as mp
import tkinter as tk
from PIL import Image, ImageTk

# Initialize MediaPipe for face detection
mp_face_detection = mp.solutions.face_detection

# Constants for Distance Measurement
KNOWN_WIDTHS = {  
    "person": 40.0,  
    "cell phone": 7.0,  
    "laptop": 35.0,  
    "bottle": 8.0,  
    "face": 14.0  
}
FOCAL_LENGTH = 600  
DETECTION_INTERVAL = 8  # Run detection every 8 seconds
SMOOTHING_WINDOW_SIZE = 10  
history = []


class ObjectDistanceDetector:
    def __init__(self, update_ui_callback=None):
        """Initialize object & distance detection along with text-to-speech in a separate thread."""
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  
        
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=True)  
        self.reader = easyocr.Reader(['en'])  
        self.face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.3)  

        self.update_ui_callback = update_ui_callback  
        self.cap = None
        self.running = False  
        self.voice_queue = []  # Store detected items for voice announcement
        self.voice_thread = threading.Thread(target=self.run_voice, daemon=True)
        self.voice_thread.start()

    def calculate_distance(self, object_name, width_in_pixels):
        """Calculate distance using a pinhole camera model."""
        if object_name in KNOWN_WIDTHS and width_in_pixels > 0:
            return (KNOWN_WIDTHS[object_name] * FOCAL_LENGTH) / width_in_pixels
        return None  

    def get_smoothed_distance(self, new_distance):
        """Smooth distance using a moving average."""
        if new_distance is not None:
            history.append(new_distance)
            if len(history) > SMOOTHING_WINDOW_SIZE:
                history.pop(0)
            return np.mean(history)
        return None

    def speak(self, text):
        """Queue detected objects for speech without blocking."""
        self.voice_queue.append(text)

    def run_voice(self):
        """Run a separate thread to process and speak detected objects."""
        while True:
            if self.voice_queue:
                text = self.voice_queue.pop(0)
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            time.sleep(1)  # Prevent CPU overload

    def detect_objects_and_distance(self):
        """Detect objects and measure distances every 8 seconds in a separate thread."""
        self.cap = cv2.VideoCapture(0)  
        self.running = True

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("[ERROR] Couldn't read frame from webcam!")
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # ✅ Face Detection
            face_results = self.face_detection.process(rgb_frame)
            detected_distances = {}  

            if face_results.detections:
                for detection in face_results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape
                    bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)

                    face_width_in_pixels = bbox[2]
                    face_distance = self.calculate_distance("face", face_width_in_pixels)
                    smoothed_face_distance = self.get_smoothed_distance(face_distance)

                    detected_distances["face"] = smoothed_face_distance
                    cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (255, 0, 0), 2)
                    cv2.putText(frame, f"Face: {smoothed_face_distance:.2f} cm", (bbox[0], bbox[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            # ✅ Object Detection (YOLOv5)
            results = self.model(frame)
            detected_objects = []

            for index, row in results.pandas().xyxy[0].iterrows():
                x1, y1, x2, y2 = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
                label = row['name']

                object_width_in_pixels = x2 - x1
                object_distance = self.calculate_distance(label, object_width_in_pixels)
                smoothed_object_distance = self.get_smoothed_distance(object_distance)

                detected_distances[label] = smoothed_object_distance

                if smoothed_object_distance is not None:
                    detected_objects.append(f"{label} ({smoothed_object_distance:.2f} cm)")
                else:
                    detected_objects.append(f"{label} (Unknown distance)")

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label}: {smoothed_object_distance:.2f} cm" if smoothed_object_distance 
                            else f"{label}: Unknown",
                            (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # ✅ Speak detected objects in the background
            if detected_objects:
                detected_str = ", ".join(detected_objects)
                print(f"Detected: {detected_str}")
                self.speak(detected_str)

                if self.update_ui_callback:
                    self.update_ui_callback(detected_str)

            cv2.imshow("Object & Distance Detection", frame)  

            time.sleep(DETECTION_INTERVAL)  # Wait before detecting again

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def start(self):
        """Start object detection in a separate thread."""
        threading.Thread(target=self.detect_objects_and_distance, daemon=True).start()

    def stop(self):
        """Stop object detection."""
        self.running = False


### ✅ Tkinter UI for User-Friendly Control
class ObjectDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Object & Distance Detection")
        self.root.geometry("800x600")

        self.detector = ObjectDistanceDetector(update_ui_callback=self.update_ui)

        # ✅ UI Elements
        self.start_button = tk.Button(root, text="Start Detection", command=self.start_detection, font=("Arial", 14), bg="green", fg="white")
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop Detection", command=self.stop_detection, font=("Arial", 14), bg="red", fg="white")
        self.stop_button.pack(pady=10)

        self.status_label = tk.Label(root, text="Status: Idle", font=("Arial", 12))
        self.status_label.pack(pady=10)

        self.camera_feed_label = tk.Label(root)
        self.camera_feed_label.pack()

    def update_ui(self, detected_text):
        """Update UI with detected objects."""
        self.status_label.config(text=f"Detected: {detected_text}")

    def start_detection(self):
        """Start object & distance detection."""
        self.detector.start()
        self.status_label.config(text="Status: Running...")

    def stop_detection(self):
        """Stop detection."""
        self.detector.stop()
        self.status_label.config(text="Status: Stopped")


# ✅ Allow script to run independently
if __name__ == "__main__":
    root = tk.Tk()
    app = ObjectDetectionApp(root)
    root.mainloop()

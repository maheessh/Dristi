import cv2
import torch
import easyocr
import pyttsx3
import threading
import time
import numpy as np
import mediapipe as mp

# Initialize MediaPipe for face detection
mp_face_detection = mp.solutions.face_detection

# Constants for Distance Measurement
KNOWN_WIDTHS = {  
    "person": 40.0,  # Average shoulder width (cm)
    "cell phone": 7.0,  # Average phone width (cm)
    "laptop": 35.0,  # Average laptop width (cm)
    "bottle": 8.0,  # Average bottle width (cm)
    "face": 14.0  # Average face width (cm)
}
FOCAL_LENGTH = 600  
DETECTION_INTERVAL = 8  # Run detection every 8 seconds
SMOOTHING_WINDOW_SIZE = 10  
history = []


class ObjectDistanceDetector:
    def __init__(self, update_ui_callback=None, shared_cap=None):
        """Initialize object & distance detection along with text-to-speech."""
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Adjust speech speed
        
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=True)  # YOLOv5 model
        self.reader = easyocr.Reader(['en'])  # OCR reader for text detection
        self.face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.3)  # Face detector

        self.update_ui_callback = update_ui_callback  # Callback to update UI

        self.cap = shared_cap if shared_cap else cv2.VideoCapture(0)
        self.running = False  # Flag to control detection loop

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
        """Convert text to speech asynchronously."""
        threading.Thread(target=lambda: self._speak(text), daemon=True).start()

    def _speak(self, text):
        """Speak text."""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def detect_objects_and_distance(self):
        """Detect objects and measure distances every 8 seconds."""
        def run_detection():
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

                    # ✅ Prevent NoneType Formatting Error
                    if smoothed_object_distance is not None:
                        detected_objects.append(f"{label} ({smoothed_object_distance:.2f} cm)")
                    else:
                        detected_objects.append(f"{label} (Unknown distance)")

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{label}: {smoothed_object_distance:.2f} cm" if smoothed_object_distance 
                                else f"{label}: Unknown",
                                (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # ✅ Speak detected objects & their distances every 8 seconds
                if detected_objects:
                    detected_str = ", ".join(detected_objects)
                    print(f"Detected: {detected_str}")
                    self.speak(detected_str)

                    if self.update_ui_callback:
                        self.update_ui_callback(detected_str)

                cv2.imshow("Object & Distance Detection", frame)  

                # ✅ Wait for 8 seconds before detecting again
                time.sleep(DETECTION_INTERVAL)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.running = False
                    break

            self.cap.release()
            cv2.destroyAllWindows()

        threading.Thread(target=run_detection, daemon=True).start()

    def stop(self):
        """Stop object detection."""
        self.running = False

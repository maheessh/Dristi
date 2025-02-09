import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import threading
import time

mp_face_detection = mp.solutions.face_detection

# Constants
KNOWN_FACE_WIDTH = 14.0  # Average face width in cm
FOCAL_LENGTH = 600  # Adjust based on camera calibration
SMOOTHING_WINDOW_SIZE = 10  
face_distance_history = deque(maxlen=SMOOTHING_WINDOW_SIZE)

MOVEMENT_THRESHOLD = 10  
bbox_history = deque(maxlen=5)

class FaceDetector:
    def __init__(self, update_ui_callback=None):
        self.cap = cv2.VideoCapture(0)
        self.face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.3)
        self.running = True
        self.detected_distance = None
        self.lock = threading.Lock()
        self.update_ui_callback = update_ui_callback  # Callback to update UI
        self.thread = threading.Thread(target=self.detect_faces, daemon=True)
        self.thread.start()

    def calculate_distance(self, known_width, width_in_pixels):
        if width_in_pixels > 0:
            return (known_width * FOCAL_LENGTH) / width_in_pixels
        return None  # Prevent division by zero

    def get_smoothed_distance(self, new_distance):
        face_distance_history.append(new_distance)
        return np.mean(face_distance_history)

    def detect_faces(self):
        """Continuously detects faces and updates UI."""
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("[ERROR] Camera frame not received!")
                continue

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_results = self.face_detection.process(rgb_frame)

            detected_distance = None  # Reset detected distance
            if face_results.detections:
                for detection in face_results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape
                    bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)

                    face_width_in_pixels = bbox[2]
                    if face_width_in_pixels > 0:
                        face_distance = self.calculate_distance(KNOWN_FACE_WIDTH, face_width_in_pixels)
                        detected_distance = self.get_smoothed_distance(face_distance)
                    else:
                        print("[ERROR] Face width in pixels is 0!")

                    # Draw bounding box and display distance
                    cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (255, 0, 0), 2)
                    cv2.putText(frame, f"Distance: {face_distance:.2f} cm", (bbox[0], bbox[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                    bbox_history.append(bbox)

            # Update UI with detected distance
            if detected_distance is not None:
                print(f"[DEBUG] Detected distance: {detected_distance:.2f} cm")  # Debugging
                if self.update_ui_callback:
                    self.update_ui_callback(detected_distance)
            else:
                print("[WARNING] No face detected. UI update skipped.")

            time.sleep(0.1)  # Reduce CPU load

    def start(self):
        """Starts the face detection if not already running."""
        if not self.thread.is_alive():
            self.running = True
            self.thread = threading.Thread(target=self.detect_faces, daemon=True)
            self.thread.start()

    def stop(self):
        """Stops the face detection."""
        self.running = False
        self.cap.release()
        cv2.destroyAllWindows()

import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import datetime
import threading
import pyttsx3

mp_face_detection = mp.solutions.face_detection
KNOWN_FACE_WIDTH = 14.0  # Average face width in cm
FOCAL_LENGTH = 600  # Camera-specific focal length
SMOOTHING_WINDOW_SIZE = 10
face_distance_history = deque(maxlen=SMOOTHING_WINDOW_SIZE)

engine = pyttsx3.init()
engine.setProperty('rate', 150)

last_speech_time = datetime.datetime.now()
last_detection_state = False  # Keeps track if the last state was "no person seen"
speech_lock = threading.Lock()

# Function to handle speech in a separate thread
def speak_text(text):
    with speech_lock:
        engine.say(text)
        engine.runAndWait()

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

with mp_face_detection.FaceDetection(min_detection_confidence=0.3) as face_detection:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_results = face_detection.process(rgb_frame)
        current_time = datetime.datetime.now()
        person_detected = False

        if face_results.detections:
            for detection in face_results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = frame.shape
                bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                       int(bboxC.width * iw), int(bboxC.height * ih)

                face_width_in_pixels = bbox[2]
                if face_width_in_pixels > 0:
                    face_distance = (KNOWN_FACE_WIDTH * FOCAL_LENGTH) / face_width_in_pixels
                    smoothed_face_distance = np.mean(face_distance_history)
                    face_distance_history.append(face_distance)
                    person_detected = True

                    cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (255, 0, 0), 2)
                    cv2.putText(frame, f"Distance: {smoothed_face_distance:.2f} cm", (bbox[0], bbox[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                    if (current_time - last_speech_time).total_seconds() >= 3:
                        threading.Thread(target=speak_text, args=(f"Distance is {smoothed_face_distance:.2f} centimeters",)).start()
                        last_speech_time = current_time

        cv2.imshow("Distance Measurement", frame)

        if not person_detected:
            if not last_detection_state:  # Only say "No person seen" once
                threading.Thread(target=speak_text, args=("No person seen",)).start()
                last_detection_state = True
        else:
            last_detection_state = False

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

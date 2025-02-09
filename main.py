import tkinter as tk
import threading
from ui import DristhiApp
from object_distance_detector import ObjectDistanceDetector

def run_detection(app):
    """Start object & distance detection using shared camera feed."""
    detector = ObjectDistanceDetector(update_ui_callback=app.update_camera_display, shared_cap=app.cap)
    detector.detect_objects_and_distance()

if __name__ == "__main__":
    root = tk.Tk()
    app = DristhiApp(root)

    # Start detection thread
    detection_thread = threading.Thread(target=run_detection, args=(app,), daemon=True)
    detection_thread.start()

    root.mainloop()

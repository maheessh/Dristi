import serial
import tkinter as tk
import speech_recognition as sr
import pyttsx3
import openpyxl
import threading
import time

class HardwareMonitor:
    def __init__(self, parent):
        """Initialize hardware monitoring and UI in the Health tab."""
        self.parent = parent
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.arduino = None
        self.connected = False

        try:
            self.arduino = serial.Serial('COM5', 9600, timeout=2)
            time.sleep(2)  # Give time for Arduino to initialize
            self.connected = True
            print("Connected to Arduino.")
        except serial.SerialException:
            print("No Arduino detected. Health data will not be available.")

        self.wb = openpyxl.Workbook()
        self.sheet = self.wb.active
        self.sheet.title = "Sensor Data"
        self.sheet.append(['Roll', 'Temp', 'Posture', 'Distance', 'Button'])

        self.health_frame = tk.Frame(self.parent, bg="#1E1E1E")
        self.health_frame.pack(fill=tk.BOTH, expand=True)

        if self.connected:
            self.setup_ui()
            self.start_monitoring()
        else:
            self.show_placeholder_ui()

    def setup_ui(self):
        self.labels = {
            "Roll": tk.Label(self.health_frame, text="Roll: N/A", font=("Arial", 12), fg="white", bg="#1E1E1E"),
            "Temperature": tk.Label(self.health_frame, text="Temperature: N/A", font=("Arial", 12), fg="white", bg="#1E1E1E"),
            "Posture": tk.Label(self.health_frame, text="Posture: N/A", font=("Arial", 12), fg="white", bg="#1E1E1E"),
            "Distance": tk.Label(self.health_frame, text="Distance: N/A", font=("Arial", 12), fg="white", bg="#1E1E1E"),
            "Button": tk.Label(self.health_frame, text="Button: N/A", font=("Arial", 12), fg="white", bg="#1E1E1E"),
        }

        for label in self.labels.values():
            label.pack(pady=5)

    def show_placeholder_ui(self):
        placeholder_label = tk.Label(
            self.health_frame,
            text="No hardware data available (Arduino not detected)",
            font=("Arial", 14, "italic"),
            fg="red",
            bg="#1E1E1E"
        )
        placeholder_label.pack(pady=20)

    def speak(self, text):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Text-to-Speech Error: {e}")

    def listen_for_commands(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        while True:
            try:
                with mic as source:
                    print("Listening for commands...")
                    recognizer.adjust_for_ambient_noise(source)
                    audio = recognizer.listen(source)

                command = recognizer.recognize_google(audio).lower()
                print(f"Recognized command: {command}")

                if "body temperature" in command:
                    temp = self.labels["Temperature"].cget("text").split(": ")[1] if ": " in self.labels["Temperature"].cget("text") else "unavailable"
                    self.speak(f"Your current temperature is {temp}")

                elif "roll" in command:
                    roll = self.labels["Roll"].cget("text").split(": ")[1] if ": " in self.labels["Roll"].cget("text") else "unavailable"
                    self.speak(f"The current roll is {roll}")

                else:
                    self.speak("Sorry, I didn't understand that.")

            except sr.UnknownValueError:
                print("Could not understand the audio.")
            except sr.RequestError:
                print("Could not request results from Google Speech Recognition service.")

    def process_data(self):
        if not self.arduino:
            return

        try:
            if self.arduino.in_waiting > 0:
                data = self.arduino.readline().decode('utf-8').strip()
                print(f"Received data: {data}")

                data_parts = data.split(", ")
                if len(data_parts) < 5:
                    print("Error: Incomplete data received.")
                    return

                parsed_data = {
                    "Roll": data_parts[0].split(": ")[1] if len(data_parts) > 0 else 'N/A',
                    "Temperature": data_parts[1].split(": ")[1] if len(data_parts) > 1 else 'N/A',
                    "Posture": data_parts[2].split(": ")[1] if len(data_parts) > 2 else 'N/A',
                    "Distance": data_parts[3].split(": ")[1] if len(data_parts) > 3 else 'N/A',
                    "Button": data_parts[4].split(": ")[1] if len(data_parts) > 4 else 'N/A',
                }

                for key, value in parsed_data.items():
                    self.labels[key].config(text=f"{key}: {value}")

                self.sheet.append(list(parsed_data.values()))
                self.wb.save('sensor_data.xlsx')
                print("Data written to Excel")

        except Exception as e:
            print(f"Error processing data: {e}")

    def update_data(self):
        self.process_data()
        self.parent.after(1000, self.update_data)

    def start_monitoring(self):
        threading.Thread(target=self.listen_for_commands, daemon=True).start()
        self.update_data()

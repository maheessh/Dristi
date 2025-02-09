# Commented out distance-related processing to prevent it from appearing
import serial
import requests
import openpyxl
import tkinter as tk
import pyttsx3
from sinch import SinchClient
from serial import SerialException
from threading import Thread

sinch_client = SinchClient(
    key_id="03bdc51a-7e51-4695-a08e-3770ad2f0c7e",
    key_secret="j4q.wUFeEUEXddw4CwEPjCp3Aq",
    project_id="f0c6b6bc-428b-4c92-9208-80f18ee7ff4f"
)

class SensorDataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Sensor Data Dashboard")
        self.root.geometry("600x400")
        self.root.configure(bg="green")

        self.engine = pyttsx3.init()

        title_label = tk.Label(
            root, text="Sensor Data Monitor", font=("Helvetica", 20, "bold"),
            bg="#8d99ae", fg="white", pady=10
        )
        title_label.pack(fill=tk.X)

        self.data_frame = tk.Frame(root, bg="#edf2f4", bd=2, relief=tk.RIDGE)
        self.data_frame.place(relx=0.05, rely=0.2, relwidth=0.9, relheight=0.6)

        self.data_label = tk.Label(
            self.data_frame, text="Waiting for data...", font=("Arial", 14),
            bg="#edf2f4", anchor="w", justify=tk.LEFT
        )
        self.data_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.wb = openpyxl.Workbook()
        self.sheet = self.wb.active
        self.sheet.title = "Sensor Data"
        self.sheet.append(['Roll', 'Temp', 'Posture', 'Button'])


        self.running = True
        self.serial_thread = Thread(target=self.read_serial_data)
        self.serial_thread.start()

    def read_serial_data(self):
        try:
            arduino = serial.Serial('COM5', 9600)  # Adjust port accordingly

            while self.running:
                try:
                    if arduino.in_waiting > 0:
                        data = arduino.readline().decode('utf-8').strip()

                        # Update the label with received data
                        self.data_label.config(text=f"Received data: {data}")

                        # Parse the data
                        data_parts = data.split(", ")
                        roll = data_parts[0].split(": ")[1] if len(data_parts) > 0 else ''
                        temp = data_parts[1].split(": ")[1] if len(data_parts) > 1 else ''
                        posture = data_parts[3].split(": ")[1] if len(data_parts) > 3 else ''
                        # distance = data_parts[4].split(": ")[1] if len(data_parts) > 4 else ''  # Commented out
                        button = data_parts[5].split(": ")[1] if len(data_parts) > 5 else ''

                        # Write data to Excel
                        self.sheet.append([roll, temp, posture, button])
                        self.wb.save('sensor_data.xlsx')  # Save workbook

                        # Check for button press and send SMS
                        if button.lower() == "yes":
                            self.send_sms_alert()

                        # Check posture and change background color
                        if posture.lower() == "bad":
                            self.root.configure(bg="red")
                            self.data_label.config(text=f"Maintain posture! Data: {data}")
                            self.notify_bad_posture()
                        else:
                            self.root.configure(bg="green")

                except SerialException:
                    self.handle_connection_lost()
                    break

        except Exception as e:
            print(f"Error: {e}")

    def send_sms_alert(self):
        try:
            response = requests.get('https://ipinfo.io')
            location_data = response.json()
            latitude = f"Latitude: {location_data['loc'].split(',')[0]}"
            longitude = f"Longitude: {location_data['loc'].split(',')[1]}"
            
            message_body = f"Mahesh needs help. He is at this location: {latitude}, {longitude}"
            
            send_batch_response = sinch_client.sms.batches.send(
                body=message_body,
                to=["+12013284561"],
                from_="+12085810231",
                delivery_report="none"
            )
            print("SMS sent:", send_batch_response)

        except Exception as e:
            print(f"Error sending SMS: {e}")

    def notify_bad_posture(self):
        # Display notification and speak
        self.engine.say("Maintain posture.")
        self.engine.runAndWait()

    def handle_connection_lost(self):
        self.data_label.config(text="Connection lost")

    def on_close(self):
        self.running = False
        self.serial_thread.join()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorDataApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

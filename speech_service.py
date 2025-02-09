import speech_recognition as sr
import threading

class SpeechService:
    def __init__(self, on_wake_word_detected):
        self.speech_recognizer = sr.Recognizer()
        self.speech_recognizer.energy_threshold = 300  # Adjust for better detection
        self.speech_recognizer.dynamic_energy_threshold = True  # Auto-adjusts based on noise
        self.on_wake_word_detected = on_wake_word_detected
        self.is_listening_for_command = False  # Prevents duplicate wake word activations

        # Start listening for wake word in the background
        threading.Thread(target=self.listen_for_wake_word, daemon=True).start()

    def listen_for_wake_word(self):
        """Continuously listens for 'Hello' to activate commands."""
        while True:
            try:
                with sr.Microphone() as source:
                    print("Listening for wake word (Hello)...")
                    self.speech_recognizer.adjust_for_ambient_noise(source, duration=1)
                    audio = self.speech_recognizer.listen(source)

                    # Convert speech to text
                    text = self.speech_recognizer.recognize_google(audio).lower().strip()
                    print(f"Heard: {text}")

                    # Activate only if wake word detected
                    if "hello" in text and not self.is_listening_for_command:
                        self.is_listening_for_command = True  # Prevents multiple activations
                        print("Wake word detected!")
                        self.on_wake_word_detected()
                        self.listen_for_command()  # Now listen for the actual command

            except sr.UnknownValueError:
                continue  # Ignore and keep listening
            except sr.RequestError:
                print("Speech recognition service error.")
                break  # Stop if there's an API issue

    def listen_for_command(self):
        """Listens for a user command after activation."""
        try:
            with sr.Microphone() as source:
                print("Listening for command...")
                self.speech_recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.speech_recognizer.listen(source)

                command = self.speech_recognizer.recognize_google(audio).lower().strip()
                print(f"Command recognized: {command}")

        except sr.UnknownValueError:
            print("Could not understand. Try again.")
        except sr.RequestError:
            print("Speech recognition service error.")

        # ✅ After processing the command, return to listening for "Hello"
        self.is_listening_for_command = False  # Allows wake-word detection again

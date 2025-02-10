import os
import googlemaps
import speech_recognition as sr
import pyttsx3
import time
import re
from geopy.distance import geodesic

# ✅ Set up Google Maps API Key
GOOGLE_MAPS_API_KEY = "GOOGLE MAPS API KEY"  # 🔹 Replace with your API key
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

# ✅ Initialize Text-to-Speech Engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)  # Adjust speech speed

def speak(text):
    """Convert text to speech and ensure it plays fully before proceeding."""
    engine.say(text)
    engine.runAndWait()

def listen_for_location():
    """Capture voice input for destination and retry if unclear."""
    recognizer = sr.Recognizer()

    for _ in range(3):  # Retry up to 3 times
        with sr.Microphone() as source:
            print("Listening for destination...")
            speak("Where do you want to go?")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            location = recognizer.recognize_google(audio).strip()
            print(f"User said: {location}")

            if location:
                return location  # Return valid location

        except sr.UnknownValueError:
            speak("Sorry, I didn't understand. Please try again.")
        except sr.RequestError:
            speak("Speech service unavailable. Try again later.")
            return None

    speak("I couldn't understand your location after multiple tries.")
    return None

def get_current_location():
    """Get the user's approximate current location using Google Maps API."""
    try:
        location_data = gmaps.geolocate()
        lat, lng = location_data["location"]["lat"], location_data["location"]["lng"]
        print(f"Current GPS Location: {lat}, {lng}")
        return lat, lng
    except googlemaps.exceptions.ApiError as e:
        speak("I couldn't get your current location.")
        print(f"Google Maps API Error: {e}")
        return None

def clean_text(text):
    """Remove HTML tags from Google Maps directions."""
    return re.sub(r"<.*?>", "", text)

def get_directions(start_location, destination):
    """Fetch step-by-step walking directions from Google Maps API."""
    try:
        directions = gmaps.directions(start_location, destination, mode="walking")

        if not directions:
            speak("I couldn't find a route to your destination.")
            return []

        steps = directions[0]["legs"][0]["steps"]
        navigation_steps = []

        for step in steps:
            instructions = clean_text(step["html_instructions"])
            distance = step["distance"]["text"]
            end_location = (step["end_location"]["lat"], step["end_location"]["lng"])
            navigation_steps.append((instructions, distance, end_location))

        return navigation_steps

    except googlemaps.exceptions.ApiError as e:
        speak("There was an error retrieving directions. Check API settings.")
        print(f"Google Maps API Error: {e}")
        return []

def has_reached_step(current_location, step_location, threshold=10):
    """Check if user has reached the step location (within 10 meters)."""
    distance = geodesic(current_location, step_location).meters
    return distance < threshold

def start_navigation():
    """Start voice navigation with real-time step-by-step directions."""
    destination = listen_for_location()
    
    if not destination:
        return  # Exit if no valid location

    start_location = get_current_location()
    
    if not start_location:
        return  # Exit if unable to fetch current location

    speak(f"Navigating to {destination}.")
    navigation_steps = get_directions(start_location, destination)

    if not navigation_steps:
        speak("I couldn't find directions to your destination.")
        return

    for i, (instruction, distance, step_location) in enumerate(navigation_steps):
        print(f"Step {i+1}: {instruction} ({distance})")
        
        # ✅ Speak out the FIRST instruction immediately
        if i == 0:
            speak(instruction)

        # ✅ Wait for the user to reach the step before announcing the next one
        while True:
            current_location = get_current_location()
            if not current_location:
                return  # Exit if location fetch fails

            if has_reached_step(current_location, step_location):
                speak(instruction)
                break

            time.sleep(5)  # Wait before checking location again

    speak("You have arrived at your destination.")

# ✅ Run navigation function
if __name__ == "__main__":
    start_navigation()

from flask import Flask, request, send_file, jsonify
import requests
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename="tracking.log", level=logging.INFO)

GOOGLE_MAPS_API_KEY = "AIzaSyCaf-BPC6XNFbM7_MFJMILrcUprTg7OT7U"

def get_address_from_coordinates(latitude, longitude):
    """Fetch address from latitude and longitude using Google Maps API."""
    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={GOOGLE_MAPS_API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        if data["status"] == "OK":
            return data["results"][0]["formatted_address"]
        else:
            return "Address not found"
    except requests.exceptions.RequestException as e:
        return f"API request failed: {e}"

import random

def get_location():
    """Fetch accurate location using Google Geolocation API with better data."""
    try:
        payload = {
            "considerIp": True,  # Use IP-based location as a fallback
            "wifiAccessPoints": [
                {"macAddress": "00:25:9c:cf:1c:ac", "signalStrength": random.randint(-80, -40), "signalToNoiseRatio": random.randint(30, 80)},
                {"macAddress": "00:14:bf:3b:2f:2b", "signalStrength": random.randint(-80, -40), "signalToNoiseRatio": random.randint(30, 80)}
            ]
        }

        url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={GOOGLE_GEOLOCATION_API_KEY}"
        response = requests.post(url, json=payload)
        data = response.json()

        if "location" in data:
            latitude = data["location"]["lat"]
            longitude = data["location"]["lng"]
            accuracy = data.get("accuracy", "Unknown")
            full_address = get_address_from_coordinates(latitude, longitude)

            return {
                "latitude": latitude,
                "longitude": longitude,
                "accuracy": accuracy,
                "address": full_address
            }
        else:
            return {"error": "Could not retrieve location data"}
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

@app.route('/')
def home():
    return "Email Tracking Service is Live! Use /track to log visits."

@app.route('/track')
def track():
    try:
        location = get_location()

        # Log visitor details
        log_entry = f"Lat: {location['latitude']}, Lon: {location['longitude']}, Address: {location['address']}, Accuracy: {location['accuracy']} meters"
        logging.info(log_entry)

        # Return the tracking pixel
        return send_file("pixel.png", mimetype="image/png")

    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        return "Error: Unable to fetch geolocation data", 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return "Error: Internal Server Issue", 500

@app.route('/view-tracked')
def view_tracked():
    with open("tracking.log", "r") as log_file:
        logs = log_file.readlines()
    return "<br>".join(logs)

@app.route('/get-location')
def get_client_location():
    location = get_location()  # ✅ Call get_location() without arguments
    return jsonify(location)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
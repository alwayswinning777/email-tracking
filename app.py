from flask import Flask, request, send_file, jsonify
import requests
import logging
import random

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename="tracking.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 🔹 Replace with your actual Google API Keys
GOOGLE_GEOLOCATION_API_KEY = "AIzaSyCaf-BPC6XNFbM7_MFJMILrcUprTg7OT7U"
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
            logging.error(f"Google Maps API Error: {data}")
            return "Address not found"
    except requests.exceptions.RequestException as e:
        logging.error(f"Google Maps API request failed: {e}")
        return "Error fetching address"

def get_location():
    """Fetch accurate location using Google Geolocation API with correct Flask processing."""
    try:
        payload = {
            "considerIp": True,
            "wifiAccessPoints": [
                {"macAddress": "00:25:9c:cf:1c:ac", "signalStrength": random.randint(-80, -40), "signalToNoiseRatio": random.randint(30, 80)},
                {"macAddress": "00:14:bf:3b:2f:2b", "signalStrength": random.randint(-80, -40), "signalToNoiseRatio": random.randint(30, 80)}
            ],
            "cellTowers": [
                {"cellId": 42, "locationAreaCode": 415, "mobileCountryCode": 310, "mobileNetworkCode": 410, "signalStrength": random.randint(-80, -40)}
            ]
        }

        url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={GOOGLE_GEOLOCATION_API_KEY}"
        response = requests.post(url, json=payload)

        if response.status_code != 200:
            logging.error(f"Google API Error: {response.text}")
            return jsonify({"error": f"Google API returned status {response.status_code}"})

        data = response.json()

        if "location" in data:
            latitude = data["location"]["lat"]
            longitude = data["location"]["lng"]
            accuracy = data.get("accuracy", "Unknown")

            logging.info(f"Location found: Lat={latitude}, Lon={longitude}, Accuracy={accuracy}m")

            # ✅ Return proper JSON response
            return jsonify({
                "latitude": latitude,
                "longitude": longitude,
                "accuracy": accuracy
            })

        else:
            logging.error(f"Google API Unexpected Response: {data}")
            return jsonify({"error": "Google API returned an invalid response"})

    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        return jsonify({"error": f"API request failed: {e}"})

@app.route('/')
def home():
    return "✅ Email Tracking Service is Live! Use /track to log visits."

@app.route('/track')
def track():
    try:
        location = get_location()

        # Log visitor details
        log_entry = f"Lat: {location.json.get('latitude', 'Unknown')}, Lon: {location.json.get('longitude', 'Unknown')}, Accuracy: {location.json.get('accuracy', 'Unknown')} meters"
        logging.info(log_entry)

        # Return the tracking pixel
        return send_file("pixel.png", mimetype="image/png")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return "Error: Internal Server Issue", 500

@app.route('/view-tracked')
def view_tracked():
    try:
        with open("tracking.log", "r") as log_file:
            logs = log_file.readlines()
        return "<br>".join(logs)
    except FileNotFoundError:
        return "No tracking data available."

@app.route('/get-location')
def get_client_location():
    return get_location()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
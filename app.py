from flask import Flask, request, send_file, jsonify
import requests
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename="tracking.log", level=logging.INFO)

GOOGLE_MAPS_API_KEY = "AIzaSyAXct7fYes2RtC-Zz8BRknXZNiDQiLdE0E"

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

GOOGLE_GEOLOCATION_API_KEY = "AIzaSyAXct7fYes2RtC-Zz8BRknXZNiDQiLdE0E"

def get_location():
    """Fetch accurate location using Google Geolocation API."""
    try:
        # Make a request to Google Geolocation API
        url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={GOOGLE_GEOLOCATION_API_KEY}"
        response = requests.post(url, json={})
        data = response.json()

        if "location" in data:
            latitude = data["location"]["lat"]
            longitude = data["location"]["lng"]
            full_address = get_address_from_coordinates(latitude, longitude)

            return {
                "latitude": latitude,
                "longitude": longitude,
                "accuracy": data.get("accuracy", "Unknown"),
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
    ip = request.remote_addr
    location = get_location(ip)
    return jsonify(location)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

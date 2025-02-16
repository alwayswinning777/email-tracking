from flask import Flask, request, send_file, jsonify
import requests
import logging
import random

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename="tracking.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def get_location_google():
    """Fetch accurate location using Google Geolocation API with Wi-Fi and cell tower data."""
    try:
        payload = {
            "considerIp": True,  # Enable IP lookup as a fallback
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
            return {"error": f"Google API returned status {response.status_code}"}

        data = response.json()

        if "location" in data:
            latitude = data["location"]["lat"]
            longitude = data["location"]["lng"]
            accuracy = data.get("accuracy", "Unknown")
            address = get_address_from_coordinates(latitude, longitude)

            logging.info(f"Google API Location: Lat={latitude}, Lon={longitude}, Accuracy={accuracy}m, Address={address}")

            return {
                "latitude": latitude,
                "longitude": longitude,
                "accuracy": accuracy,
                "address": address
            }
        else:
            logging.error(f"Google API Unexpected Response: {data}")
            return {"error": "Google API returned an invalid response"}

    except requests.exceptions.RequestException as e:
        logging.error(f"Google API request failed: {e}")
        return {"error": f"Google API request failed: {e}"}

def get_location_ip():
    """Fetch location data based on IP address lookup."""
    try:
        ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
        
        if ip == "127.0.0.1" or ip.startswith("192.") or ip.startswith("10.") or ip.startswith("172."):
            return {"error": "Local network IP detected. Cannot determine public location."}

        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        data = response.json()

        if "loc" in data:
            latitude, longitude = data["loc"].split(',')
            address = get_address_from_coordinates(latitude, longitude)

            logging.info(f"IP Location: IP={ip}, Lat={latitude}, Lon={longitude}, Address={address}")

            return {
                "ip": ip,
                "latitude": latitude,
                "longitude": longitude,
                "city": data.get("city", "Unknown"),
                "region": data.get("region", "Unknown"),
                "country": data.get("country", "Unknown"),
                "address": address,
                "isp": data.get("org", "Unknown")
            }
        else:
            logging.error(f"IP Geolocation API Unexpected Response: {data}")
            return {"error": "Could not retrieve location from IP"}

    except requests.exceptions.RequestException as e:
        logging.error(f"IP API request failed: {e}")
        return {"error": f"IP API request failed: {e}"}

@app.route('/')
def home():
    return "✅ Email Tracking Service is Live! Use /track to log visits."

@app.route('/track')
def track():
    try:
        location_google = get_location_google()
        location_ip = get_location_ip()

        # Log visitor details
        log_entry = f"Google API -> Lat: {location_google.get('latitude', 'Unknown')}, Lon: {location_google.get('longitude', 'Unknown')}, Address: {location_google.get('address', 'Unknown')}, Accuracy: {location_google.get('accuracy', 'Unknown')} meters\n"
        log_entry += f"IP Lookup -> IP: {location_ip.get('ip', 'Unknown')}, Lat: {location_ip.get('latitude', 'Unknown')}, Lon: {location_ip.get('longitude', 'Unknown')}, Address: {location_ip.get('address', 'Unknown')}, ISP: {location_ip.get('isp', 'Unknown')}"
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
    """Fetch both Google API and IP-based location data and return both results."""
    location_google = get_location_google()
    location_ip = get_location_ip()
    
    return jsonify({
        "google_location": location_google,
        "ip_location": location_ip
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
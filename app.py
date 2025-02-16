from flask import Flask, request, send_file, jsonify
import requests
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename="tracking.log", level=logging.INFO)

GOOGLE_MAPS_API_KEY = "AIzaSyDqHblgE1eMNpsna71tEzPr4dadi6PjowE"

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

def get_location():
    """Fetch real client IP and use IP geolocation API."""
    try:
        # Get the real client IP from headers (Render uses reverse proxies)
        ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

        if ip == "127.0.0.1" or ip.startswith("192.") or ip.startswith("10.") or ip.startswith("172."):
            return {
                "error": "Local network IP detected. Cannot determine public location."
            }

        # Call IP Geolocation API
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        data = response.json()

        location_info = {
            "ip": ip,
            "city": data.get("city", "Unknown"),
            "region": data.get("region", "Unknown"),
            "country": data.get("country", "Unknown"),
            "latitude": data.get("loc", "0,0").split(',')[0],
            "longitude": data.get("loc", "0,0").split(',')[1],
            "isp": data.get("org", "Unknown"),
        }
        return location_info
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}

@app.route('/')
def home():
    return "Email Tracking Service is Live! Use /track to log visits."

@app.route('/track')
def track():
    try:
        # Get the real client IP (Render uses a reverse proxy)
        ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

        if ip == "127.0.0.1" or ip.startswith("192.") or ip.startswith("10.") or ip.startswith("172."):
            location = {"error": "Local network IP detected. Cannot determine public location."}
        else:
            response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
            data = response.json()

            latitude, longitude = data.get("loc", "0,0").split(',')
            full_address = get_address_from_coordinates(latitude, longitude)

            location = {
                "ip": ip,
                "city": data.get("city", "Unknown"),
                "region": data.get("region", "Unknown"),
                "country": data.get("country", "Unknown"),
                "latitude": latitude,
                "longitude": longitude,
                "isp": data.get("org", "Unknown"),
                "address": full_address
            }

        # Log the visit details
        log_entry = f"IP: {location['ip']}, City: {location['city']}, Region: {location['region']}, Country: {location['country']}, Lat: {location['latitude']}, Lon: {location['longitude']}, ISP: {location['isp']}, Address: {location['address']}"
        logging.info(log_entry)

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

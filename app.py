from flask import Flask, request, send_file, jsonify
import requests
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename="tracking.log", level=logging.INFO)

def get_location(ip):
    """Fetch location data using an IP geolocation API and handle errors properly."""
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)  # Add timeout
        data = response.json()
        
        # Handle missing 'loc' key
        loc = data.get("loc", "0,0").split(',')
        latitude, longitude = loc[0], loc[1]

        location_info = {
            "ip": ip,
            "city": data.get("city", "Unknown"),
            "region": data.get("region", "Unknown"),
            "country": data.get("country", "Unknown"),
            "latitude": latitude,
            "longitude": longitude,
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
    ip = request.remote_addr
    location = get_location(ip)
    
    # Log the visitor details
    log_entry = f"IP: {ip}, City: {location['city']}, Region: {location['region']}, Country: {location['country']}, Lat: {location['latitude']}, Lon: {location['longitude']}, ISP: {location['isp']}"
    logging.info(log_entry)
    
    return send_file("pixel.png", mimetype="image/png")

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

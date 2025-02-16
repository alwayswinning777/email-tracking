from flask import Flask, request, send_file, jsonify
import requests
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename="tracking.log", level=logging.INFO)

def get_location(ip):
    """Fetch location data using an IP geolocation API."""
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")  # Change API if needed
        data = response.json()
        
        location_info = {
            "ip": ip,
            "city": data.get("city", "Unknown"),
            "region": data.get("region", "Unknown"),
            "country": data.get("country", "Unknown"),
            "latitude": data.get("loc", "Unknown").split(',')[0],
            "longitude": data.get("loc", "Unknown").split(',')[1],
            "isp": data.get("org", "Unknown"),
        }
        return location_info
    except Exception as e:
        return {"error": str(e)}

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

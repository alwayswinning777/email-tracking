from flask import Flask, request, send_file
import logging
import requests

app = Flask(__name__)

# Set up logging
logging.basicConfig(filename="tracking.log", level=logging.INFO)

def get_location(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        data = response.json()
        return data.get("city", "Unknown"), data.get("region", "Unknown"), data.get("country", "Unknown")
    except:
        return "Unknown", "Unknown", "Unknown"

@app.route('/track')
def track():
    ip = request.remote_addr
    city, region, country = get_location(ip)
    log_entry = f"IP: {ip}, Location: {city}, {region}, {country}"
    
    logging.info(log_entry)
    print(log_entry)  # For debugging
    
    return send_file("pixel.png", mimetype="image/png")

@app.route('/view-tracked')
def view_tracked():
    with open("tracking.log", "r") as log_file:
        logs = log_file.readlines()
    return "<br>".join(logs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


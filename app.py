import os
from flask import Flask, request, render_template, redirect, url_for
import requests
import csv

# Create the Flask app
app = Flask(__name__)

# API info
API_URL = "https://plant-hardiness-zone.p.rapidapi.com/zipcodes/{}"
HEADERS = {
    "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY", ""),
    "X-RapidAPI-Host": "plant-hardiness-zone.p.rapidapi.com"
}

# hold all looked-up ZIPs and zones
session_results = []

#Get the zone from the API
def get_zone(zip_code):
    url = API_URL.format(zip_code)
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        return None  # Something went wrong

    try:
        data = response.json()
        return data.get("hardiness_zone", "Unknown")
    except:
        return None  # Couldn’t read the data

# Main page: show form, show past results, handle lookup
@app.route("/", methods=["GET", "POST"])
def home():
    zone = None
    error = None

    # If user submitted a ZIP code
    if request.method == "POST" and "lookup" in request.form:
        zip_code = request.form.get("zip")
        zone = get_zone(zip_code)

        if zone:
            # Save this result
            session_results.append({"zip": zip_code, "zone": zone})
        else:
            error = "Could not get zone for that ZIP."

    # Show the page with results and any messages
    return render_template("index.html", results=session_results, zone=zone, error=error)

# Save all results to CSV file
@app.route("/save", methods=["POST"])
def save():
    if session_results:
        with open("plant_zones.csv", "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["zip", "zone"])
            writer.writeheader()
            writer.writerows(session_results)
    return render_template("index.html", results=session_results, saved=True, error=None, zone=None)


#Run the app
if __name__ == "__main__":
    app.run(debug=True)


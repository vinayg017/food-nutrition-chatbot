import os
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Your API keys
USDA_API_KEY = '2gLlm0zQzSdwdrTNU0dd8Wr7TBzqomHJP0Rn7nBq'  # <-- paste your USDA key here
GOOGLE_MAPS_API_KEY = 'AIzaSyCxKM0h_5wWpcJ9ENYtIXLbYwVbVPAzPd8'  # <-- paste your Google Maps key here

# Route for home page
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle food search
@app.route('/search', methods=['POST'])
def search():
    food_name = request.form['food']
    
    location = request.form['location']

    # Fetch nutrition data
    nutrition_data = get_nutrition_data(food_name)

    # Fetch nearby places
    places_data = get_places_data(food_name, location)

    return render_template('index.html', food=food_name, nutrition=nutrition_data, places=places_data)

def get_nutrition_data(food_name):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_name}&api_key={USDA_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data['foods']:
        food = data['foods'][0]
        nutrients = {}
        for nutrient in food['foodNutrients']:
            nutrients[nutrient['nutrientName']] = nutrient['value']
        return nutrients
    else:
        return None

def get_places_data(food_name, location):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={food_name}+near+{location}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    data = response.json()

    places = []
    if data.get('results'):
        for place in data['results'][:5]:  # Limit to 5 places
            places.append({
                'name': place.get('name'),
                'address': place.get('formatted_address')
            })
    return places

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        food_name = request.form["food"]
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")

        print(f"Food: {food_name}, Location: Latitude={latitude}, Longitude={longitude}")

        # Fetch nutrition info and optionally nearby places using lat/lon

        return render_template("index.html", food=food_name)  # or send nutrition data

    return render_template("index.html")
@app.route("/location", methods=["POST"])
def get_location():
    data = request.get_json()
    lat = data.get("latitude")
    lon = data.get("longitude")

    if not lat or not lon:
        return jsonify({"status": "error", "message": "Missing coordinates"}), 400

    # Google Places API request
    api_key = "AIzaSyCxKM0h_5wWpcJ9ENYtIXLbYwVbVPAzPd8"  # Replace with your actual Google Maps API key
    url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={lat},{lon}&radius=1500&type=restaurant&key={api_key}"
    )

    response = requests.get(url)
    if response.status_code == 200:
        places_data = response.json()
        nearby_places = [
            place["name"] for place in places_data.get("results", [])[:5]
        ]
        return jsonify({"status": "success", "places": nearby_places})
    else:
        return jsonify({"status": "error", "message": "Google API request failed"}), 500



import os
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# API keys
USDA_API_KEY = '2gLlm0zQzSdwdrTNU0dd8Wr7TBzqomHJP0Rn7nBq'
GOOGLE_MAPS_API_KEY = 'AIzaSyCxKM0h_5wWpcJ9ENYtIXLbYwVbVPAzPd8'

# Route for home page
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle food search based on city input
@app.route('/search', methods=['POST'])
def search():
    food_name = request.form['food']
    location = request.form['location']

    # Fetch nutrition data
    nutrition_data = get_nutrition_data(food_name)

    # Fetch nearby places based on city/location
    places_data = get_places_data(food_name, location)

    return render_template('index.html', food=food_name, nutrition=nutrition_data, places=places_data)

def get_nutrition_data(food_name):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_name}&api_key={USDA_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data.get('foods'):
        food = data['foods'][0]
        nutrients = {}
        for nutrient in food.get('foodNutrients', []):
            nutrients[nutrient.get('nutrientName')] = nutrient.get('value', 0)
        return nutrients
    else:
        return None

def get_places_data(food_name, location):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={food_name}+near+{location}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    data = response.json()

    places = []
    if data.get('results'):
        for place in data['results'][:5]:
            places.append({
                'name': place.get('name'),
                'address': place.get('formatted_address')
            })
    return places

# New endpoint to support geolocation-based nearby search
@app.route("/nearby", methods=["POST"])
def nearby_places():
    data = request.get_json()
    lat = data.get("lat")
    lon = data.get("lon")

    if not lat or not lon:
        return jsonify([])

    url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={lat},{lon}&radius=1500&type=restaurant&keyword=food&key={GOOGLE_MAPS_API_KEY}"
    )

    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get("results", [])
        names = [place.get("name") for place in results[:5]]
        return jsonify(names)
    else:
        return jsonify([])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

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

    print(f"User search: food='{food_name}', location='{location}'")

    # Fetch nutrition data
    nutrition_data = get_nutrition_data(food_name)

    # Fetch nearby places based on city/location
    places_data = get_places_data(food_name, location)

    return render_template('index.html', food=food_name, nutrition=nutrition_data, places=places_data)

def get_nutrition_data(food_name):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_name}&api_key={USDA_API_KEY}"
    response = requests.get(url)
    data = response.json()

    # Nutrient-to-unit mapping
    nutrient_units = {
        "Protein": "g",
        "Total lipid (fat)": "g",
        "Carbohydrate, by difference": "g",
        "Energy": "kcal",
        "Total Sugars": "g",
        "Fiber, total dietary": "g",
        "Calcium, Ca": "mg",
        "Iron, Fe": "mg",
        "Sodium, Na": "mg",
        "Vitamin A, IU": "IU",
        "Vitamin C, total ascorbic acid": "mg",
        "Cholesterol": "mg",
        "Fatty acids, total trans": "g",
        "Fatty acids, total saturated": "g",
        "Fatty acids, total monounsaturated": "g",
        "Fatty acids, total polyunsaturated": "g"
    }

    if data.get('foods'):
        food = data['foods'][0]
        nutrients = {}
        for nutrient in food.get('foodNutrients', []):
            name = nutrient.get('nutrientName')
            value = nutrient.get('value', 0)

            # Add unit if available
            unit = nutrient_units.get(name, "")
            if unit:
                nutrients[name] = f"{value} {unit}"
            else:
                nutrients[name] = f"{value}"

        return nutrients
    else:
        return None


def get_places_data(food_name, location):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={food_name}+near+{location}&key={GOOGLE_MAPS_API_KEY}"
    print(f"Requesting places data from: {url}")

    response = requests.get(url)
    print(f"Places API response status: {response.status_code}")
    data = response.json()
    print(f"Places API response data: {data}")

    places = []
    if data.get('results'):
        for place in data['results'][:5]:
            places.append({
                'name': place.get('name'),
                'address': place.get('formatted_address')
            })
    else:
        print("No nearby places found.")
    return places

# New endpoint to support geolocation-based nearby search
@app.route("/nearby", methods=["POST"])
def nearby_places():
    data = request.get_json()
    lat = data.get("lat")
    lon = data.get("lon")

    print(f"Received geolocation data: lat={lat}, lon={lon}")

    if not lat or not lon:
        print("Latitude or longitude not provided.")
        return jsonify([])

    url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        f"?location={lat},{lon}&radius=1500&type=restaurant&keyword=food&key={GOOGLE_MAPS_API_KEY}"
    )
    print(f"Requesting nearby places data from: {url}")

    response = requests.get(url)
    print(f"Nearby Places API response status: {response.status_code}")
    if response.status_code == 200:
        results = response.json().get("results", [])
        print(f"Nearby Places API response data: {results}")
        names = [place.get("name") for place in results[:5]]
        return jsonify(names)
    else:
        print("Nearby Places API request failed.")
        return jsonify([])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

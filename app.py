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

if __name__ == '__main__':
    app.run(debug=True)

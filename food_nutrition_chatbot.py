import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Replace with your actual USDA API Key
API_KEY = "2gLlm0zQzSdwdrTNU0dd8Wr7TBzqomHJP0Rn7nBq"
BASE_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

@app.route('/get_nutrition', methods=['GET'])
def get_nutrition():
    food_name = request.args.get('food')
    if not food_name:
        return jsonify({"error": "Please provide a food name."}), 400

    params = {
        "query": food_name,
        "api_key": API_KEY
    }
    
    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch data from USDA API."}), 500
    
    data = response.json()
    if "foods" not in data or len(data["foods"]) == 0:
        return jsonify({"error": "No nutrition data found for the given food."}), 404
    
    food_info = data["foods"][0]  # Take the first result
    nutrients = {nutrient["nutrientName"]: nutrient["value"] for nutrient in food_info["foodNutrients"]}

    return jsonify({
        "food": food_name,
        "description": food_info["description"],
        "nutrients": nutrients
    })

if __name__ == '__main__':
    app.run(debug=True)

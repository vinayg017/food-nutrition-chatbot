import os
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# API keys
USDA_API_KEY = '2gLlm0zQzSdwdrTNU0dd8Wr7TBzqomHJP0Rn7nBq'
GOOGLE_MAPS_API_KEY = 'AIzaSyCxKM0h_5wWpcJ9ENYtIXLbYwVbVPAzPd8'

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html', username=session.get('username'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash('Signup successful. Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.')
        finally:
            conn.close()
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/guest')
def guest():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('home'))

@app.route('/search', methods=['POST'])
def search():
    food_name = request.form['food']
    nutrition_data = get_nutrition_data(food_name)
    return render_template('index.html', food=food_name, nutrition=nutrition_data, username=session.get('username'))

def get_nutrition_data(food_name):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={food_name}&api_key={USDA_API_KEY}"
    response = requests.get(url)
    data = response.json()

    nutrient_units = {
        "Protein": "g", "Total lipid (fat)": "g", "Carbohydrate, by difference": "g", "Energy": "kcal",
        "Total Sugars": "g", "Fiber, total dietary": "g", "Calcium, Ca": "mg", "Iron, Fe": "mg",
        "Sodium, Na": "mg", "Vitamin A, IU": "IU", "Vitamin C, total ascorbic acid": "mg", "Cholesterol": "mg",
        "Fatty acids, total trans": "g", "Fatty acids, total saturated": "g", 
        "Fatty acids, total monounsaturated": "g", "Fatty acids, total polyunsaturated": "g"
    }

    if data.get('foods'):
        food = data['foods'][0]
        nutrients = {}
        for nutrient in food.get('foodNutrients', []):
            name = nutrient.get('nutrientName')
            value = nutrient.get('value', 0)
            unit = nutrient_units.get(name, "")
            nutrients[name] = f"{value} {unit}" if unit else f"{value}"
        return nutrients
    return None

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
    return jsonify([])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

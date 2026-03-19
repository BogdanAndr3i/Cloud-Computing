from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

app = Flask(__name__)
CORS(app)

TEAMS_BASE  = "http://localhost:8000"
PILOTS_BASE = "http://localhost:8001"
RACES_BASE  = "http://localhost:8002"


def proxy_get(url):
    try:
        r = requests.get(url, timeout=5)
        return jsonify(r.json()), r.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({"error": f"Service at {url} is not running."}), 503

def proxy_post(url, body):
    try:
        r = requests.post(url, json=body, timeout=5)
        return jsonify(r.json()), r.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({"error": f"Service at {url} is not running."}), 503

def proxy_put(url, body):
    try:
        r = requests.put(url, json=body, timeout=5)
        return jsonify(r.json()), r.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({"error": f"Service at {url} is not running."}), 503

def proxy_patch(url, body):
    try:
        r = requests.patch(url, json=body, timeout=5)
        return jsonify(r.json()), r.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({"error": f"Service at {url} is not running."}), 503

def proxy_delete(url):
    try:
        r = requests.delete(url, timeout=5)
        return jsonify(r.json()), r.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({"error": f"Service at {url} is not running."}), 503


@app.route("/api/teams", methods=["GET"])
def get_teams():
    return proxy_get(f"{TEAMS_BASE}/teams")

@app.route("/api/teams/<int:team_id>", methods=["GET"])
def get_team(team_id):
    return proxy_get(f"{TEAMS_BASE}/teams/{team_id}")

@app.route("/api/teams", methods=["POST"])
def create_team():
    return proxy_post(f"{TEAMS_BASE}/teams", request.get_json())

@app.route("/api/teams/<int:team_id>", methods=["PUT"])
def update_team(team_id):
    return proxy_put(f"{TEAMS_BASE}/teams/{team_id}", request.get_json())

@app.route("/api/teams/<int:team_id>", methods=["PATCH"])
def patch_team(team_id):
    return proxy_patch(f"{TEAMS_BASE}/teams/{team_id}", request.get_json())

@app.route("/api/teams/<int:team_id>", methods=["DELETE"])
def delete_team(team_id):
    return proxy_delete(f"{TEAMS_BASE}/teams/{team_id}")


@app.route("/api/pilots", methods=["GET"])
def get_pilots():
    return proxy_get(f"{PILOTS_BASE}/pilots")

@app.route("/api/pilots/<int:pilot_id>", methods=["GET"])
def get_pilot(pilot_id):
    return proxy_get(f"{PILOTS_BASE}/pilots/{pilot_id}")

@app.route("/api/pilots", methods=["POST"])
def create_pilot():
    return proxy_post(f"{PILOTS_BASE}/pilots", request.get_json())

@app.route("/api/pilots/<int:pilot_id>", methods=["PUT"])
def update_pilot(pilot_id):
    return proxy_put(f"{PILOTS_BASE}/pilots/{pilot_id}", request.get_json())

@app.route("/api/pilots/<int:pilot_id>", methods=["PATCH"])
def patch_pilot(pilot_id):
    return proxy_patch(f"{PILOTS_BASE}/pilots/{pilot_id}", request.get_json())

@app.route("/api/pilots/<int:pilot_id>", methods=["DELETE"])
def delete_pilot(pilot_id):
    return proxy_delete(f"{PILOTS_BASE}/pilots/{pilot_id}")


@app.route("/api/races", methods=["GET"])
def get_races():
    return proxy_get(f"{RACES_BASE}/races")

@app.route("/api/races/<int:race_id>", methods=["GET"])
def get_race(race_id):
    return proxy_get(f"{RACES_BASE}/races/{race_id}")

@app.route("/api/races", methods=["POST"])
def create_race():
    return proxy_post(f"{RACES_BASE}/races", request.get_json())

@app.route("/api/races/<int:race_id>", methods=["PUT"])
def update_race(race_id):
    return proxy_put(f"{RACES_BASE}/races/{race_id}", request.get_json())

@app.route("/api/races/<int:race_id>", methods=["PATCH"])
def patch_race(race_id):
    return proxy_patch(f"{RACES_BASE}/races/{race_id}", request.get_json())

@app.route("/api/races/<int:race_id>", methods=["DELETE"])
def delete_race(race_id):
    return proxy_delete(f"{RACES_BASE}/races/{race_id}")


@app.route("/api/dashboard", methods=["GET"])
def get_dashboard():
    try:
        teams  = requests.get(f"{TEAMS_BASE}/teams",   timeout=5).json()
        pilots = requests.get(f"{PILOTS_BASE}/pilots", timeout=5).json()
        races  = requests.get(f"{RACES_BASE}/races",   timeout=5).json()
        return jsonify({
            "teams":  teams,
            "pilots": pilots,
            "races":  races,
            "stats": {
                "total_teams":  len(teams),
                "total_pilots": len(pilots),
                "total_races":  len(races),
            }
        }), 200
    except requests.exceptions.ConnectionError as e:
        return jsonify({"error": "One or more services are not running.", "detail": str(e)}), 503


@app.route("/api/weather", methods=["GET"])
def get_weather():
    city = request.args.get("city", "Monaco")
    if not WEATHER_API_KEY:
        return jsonify({"error": "WEATHER_API_KEY missing from .env"}), 500
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
        r = requests.get(url, params=params, timeout=5)
        data = r.json()
        if r.status_code == 401:
            return jsonify({"error": "Invalid API key."}), 401
        if r.status_code == 404:
            return jsonify({"error": f"City '{city}' not found."}), 404
        rain = data.get("rain", {})
        rain_chance = round(data.get("pop", 0) * 100) if "pop" in data else (100 if rain else 0)
        return jsonify({
            "city": data["name"],
            "country": data["sys"]["country"],
            "temp": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": round(data["wind"]["speed"] * 3.6),
            "pressure": data["main"]["pressure"],
            "icon": data["weather"][0]["icon"],
            "rain_chance": rain_chance
        }), 200
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Could not connect to OpenWeatherMap."}), 503


if __name__ == "__main__":
    app.run(port=5000, debug=True)

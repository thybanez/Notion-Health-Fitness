from flask import Flask, request, jsonify
import os
from notion_client import Client
from datetime import datetime

app = Flask(__name__)

# Notion API Setup
notion = Client(auth=os.environ["NOTION_API_KEY"])
FOOD_LOG_DB_ID = os.environ["FOOD_LOG_DB_ID"]
WORKOUT_LOG_DB_ID = os.environ["WORKOUT_LOG_DB_ID"]
DAILY_LOG_DB_ID = os.environ["DAILY_LOG_DB_ID"]

# Utility: Create or get Daily Log entry
def get_or_create_daily_log_page(date_str):
    response = notion.databases.query({
        "database_id": DAILY_LOG_DB_ID,
        "filter": {
            "property": "Log Date",
            "date": {"equals": date_str}
        }
    })
    results = response.get("results")
    if results:
        return results[0]["id"]
    else:
        new_page = notion.pages.create({
            "parent": {"database_id": DAILY_LOG_DB_ID},
            "properties": {
                "Log Date": {"date": {"start": date_str}}
            }
        })
        return new_page["id"]

# Create food entry
def create_food_entry(data):
    date_str = data["date"]
    daily_log_id = get_or_create_daily_log_page(date_str)

    notion.pages.create({
        "parent": {"database_id": FOOD_LOG_DB_ID},
        "properties": {
            "Date": {"date": {"start": date_str}},
            "Meal": {"select": {"name": data["meal"]}},
            "Food Description": {"rich_text": [{"text": {"content": data["description"]}}]},
            "Calories (kcal)": {"number": data["calories"]},
            "Protein (g)": {"number": data["protein"]},
            "Carbs (g)": {"number": data["carbs"]},
            "Fat (g)": {"number": data["fat"]},
            "Total Sugar (g)": {"number": data["sugar"]},
            "High Sugar?": {"checkbox": data["high_sugar"]},
            "Cholesterol Risk": {"select": {"name": data["cholesterol_risk"]}},
            "Date (Daily Log)": {"relation": [{"id": daily_log_id}]}
        }
    })

# Create workout entry
def create_workout_entry(data):
    date_str = data["date"]
    daily_log_id = get_or_create_daily_log_page(date_str)

    notion.pages.create({
        "parent": {"database_id": WORKOUT_LOG_DB_ID},
        "properties": {
            "Date": {"date": {"start": date_str}},
            "Type": {"select": {"name": data["type"]}},
            "Duration (min)": {"number": data["duration"]},
            "Calories Burned (kcal)": {"number": data["calories_burned"]},
            "RPE (1-10)": {"number": data["rpe"]},
            "Description": {"rich_text": [{"text": {"content": data["description"]}}]},
            "Date (Daily Log)": {"relation": [{"id": daily_log_id}]}
        }
    })

@app.route("/", methods=["GET"])
def home():
    return "✅ Notion logging service is running!"

@app.route("/log", methods=["POST"])
def log_entry():
    data = request.get_json()

    try:
        if data["type"] == "food":
            create_food_entry(data)
            return jsonify({"status": "success", "message": "Food entry logged"})
        elif data["type"] == "workout":
            create_workout_entry(data)
            return jsonify({"status": "success", "message": "Workout entry logged"})
        else:
            return jsonify({"status": "error", "message": "Invalid entry type"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/log/food", methods=["POST"])
def log_food_entry():
    data = request.get_json()
    print("🔎 Incoming payload:", data)
    
    try:
        create_food_entry(data)
        return jsonify({"status": "success", "message": "Food entry logged"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/log/workout", methods=["POST"])
def log_workout_entry():
    data = request.get_json()
    try:
        create_workout_entry(data)
        return jsonify({"status": "success", "message": "Workout entry logged"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


from flask import Flask, request, jsonify
import os
from notion_client import Client

app = Flask(__name__)

# Notion API Setup
notion = Client(auth=os.environ["NOTION_API_KEY"])
FOOD_LOG_DB_ID = os.environ["FOOD_LOG_DB_ID"]
WORKOUT_LOG_DB_ID = os.environ["WORKOUT_LOG_DB_ID"]
DAILY_LOG_DB_ID = os.environ["DAILY_LOG_DB_ID"]
GYM_LOG_DB_ID = os.environ["GYM_LOG_DB_ID"]  # New gym log database

# Utility: Create or get Daily Log entry
def get_or_create_daily_log_page(date_str):
    resp = notion.databases.query(
        database_id=DAILY_LOG_DB_ID,
        filter={
            "property": "Log Date",
            "date": {"equals": date_str}
        }
    )
    results = resp.get("results", [])
    if results:
        return results[0]["id"]
    new_page = notion.pages.create(
        parent={"database_id": DAILY_LOG_DB_ID},
        properties={
            "Log Date": {"date": {"start": date_str}}
        }
    )
    return new_page["id"]

# Create a food entry
def create_food_entry(data):
    date_str      = data["date"]
    daily_log_id  = get_or_create_daily_log_page(date_str)

    notion.pages.create(
        parent={"database_id": FOOD_LOG_DB_ID},
        properties={
            "Date":             {"date":      {"start": date_str}},
            "Meal":             {"select":    {"name": data["meal"]}},
            "Food Description": {
                "rich_text": [{"text": {"content": data["description"]}}]
            },
            "Calories (kcal)":  {"number":    data["calories"]},
            "Protein (g)":      {"number":    data["protein"]},
            "Carbs (g)":        {"number":    data["carbs"]},
            "Fat (g)":          {"number":    data["fat"]},
            "Total Sugar (g)":  {"number":    data["sugar"]},
            "High Sugar?":      {"checkbox":  data["high_sugar"]},
            "Cholesterol Risk": {"select":    {"name": data["cholesterol_risk"]}},
            "Date (Daily Log)": {"relation":  [{"id": daily_log_id}]}
        }
    )

# Create a workout entry
def create_workout_entry(data):
    date_str      = data["date"]
    daily_log_id  = get_or_create_daily_log_page(date_str)

    notion.pages.create(
        parent={"database_id": WORKOUT_LOG_DB_ID},
        properties={
            "Date":               {"date":      {"start": date_str}},
            "Workout Type":       {"select":    {"name": data["workout_type"]}},
            "Duration (min)":     {"number":    data["duration"]},
            "Calories Burned (kcal)": {"number": data["calories_burned"]},
            "RPE (1-10)":         {"number":    data["rpe"]},
            "Description": {
                "rich_text": [{"text": {"content": data["description"]}}]
            },
            "Date (Daily Log)":   {"relation":  [{"id": daily_log_id}]}
        }
    )

# Create a gym (exercise) entry
def create_gym_log_entry(data):
    date_str = data["date"]
    properties = {
        "Date": {"date": {"start": date_str}},
        "Exercise": {"title": [{"text": {"content": data["exercise"]}}]},
        "Weight": {"rich_text": [{"text": {"content": str(data.get("weight", ""))}}]},
        "Reps / Time": {"rich_text": [{"text": {"content": data.get("reps_time", "")}}]},
        "Sets": {"number": data.get("sets", 0)},
        "Type": {"select": {"name": data.get("type", "Strength")}},
        "Notes": {"rich_text": [{"text": {"content": data.get("notes", "")}}]}
    }
    # Optional: add session relation if provided
    session_id = data.get("session_id")
    if session_id:
        properties["Session"] = {"relation": [{"id": session_id}]}
    notion.pages.create(
        parent={"database_id": GYM_LOG_DB_ID},
        properties=properties
    )

@app.route("/", methods=["GET"])
def home():
    return "✅ Notion logging service is running!"

# General log endpoint
@app.route("/log", methods=["POST"])
def log_entry():
    data = request.get_json()
    try:
        t = data.get("type")
        if t == "food":
            create_food_entry(data)
        elif t == "workout":
            create_workout_entry(data)
        elif t == "gym":
            create_gym_log_entry(data)
        else:
            return jsonify({"status": "error", "message": "Invalid entry type"}), 400
        return jsonify({"status": "success", "message": "Entry logged"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Dedicated food log endpoint
@app.route("/log/food", methods=["POST"])
def log_food_endpoint():
    data = request.get_json()
    try:
        create_food_entry(data)
        return jsonify({"status": "success", "message": "Food entry logged"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Dedicated workout log endpoint
@app.route("/log/workout", methods=["POST"])
def log_workout_endpoint():
    data = request.get_json()
    try:
        create_workout_entry(data)
        return jsonify({"status": "success", "message": "Workout entry logged"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Dedicated gym log endpoint
@app.route("/log/gym", methods=["POST"])
def log_gym_entry():
    data = request.get_json()
    try:
        create_gym_log_entry(data)
        return jsonify({"status": "success", "message": "Gym entry logged"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Fetch food entries in a date range
@app.route("/entries/food", methods=["POST"])
def get_food_entries():
    data = request.get_json()
    start = data["start_date"]
    end   = data["end_date"]
    resp = notion.databases.query(
        database_id=FOOD_LOG_DB_ID,
        filter={
            "property": "Date",
            "date": {
                "on_or_after": start,
                "on_or_before": end
            }
        }
    )
    entries = []
    for page in resp.get("results", []):
        p = page["properties"]
        entries.append({
            "date":             p["Date"]["date"]["start"],
            "meal":             p["Meal"]["select"]["name"],
            "description":      "".join(rt["plain_text"] for rt in p["Food Description"]["rich_text"]),
            "calories":         p["Calories (kcal)"]["number"],
            "protein":          p["Protein (g)"]["number"],
            "carbs":            p["Carbs (g)"]["number"],
            "fat":              p["Fat (g)"]["number"],
            "sugar":            p["Total Sugar (g)"]["number"],
            "high_sugar":       p["High Sugar?"]["checkbox"],
            "cholesterol_risk": p["Cholesterol Risk"]["select"]["name"]
        })
    return jsonify(entries), 200

# Fetch workout entries in a date range
@app.route("/entries/workout", methods=["POST"])
def get_workout_entries():
    data = request.get_json()
    start = data["start_date"]
    end   = data["end_date"]
    resp = notion.databases.query(
        database_id=WORKOUT_LOG_DB_ID,
        filter={
            "property": "Date",
            "date": {
                "on_or_after": start,
                "on_or_before": end
            }
        }
    )
    entries = []
    for page in resp.get("results", []):
        p = page["properties"]
        entries.append({
            "date":            p["Date"]["date"]["start"],
            "workout_type":    p["Workout Type"]["select"]["name"],
            "duration":        p["Duration (min)"]["number"],
            "calories_burned": p["Calories Burned (kcal)"]["number"],
            "rpe":             p["RPE (1-10)"]["number"],
            "description":     "".join(rt["plain_text"] for rt in p["Description"]["rich_text"])
        })
    return jsonify(entries), 200

# Fetch gym (exercise) entries in a date range
@app.route("/entries/gym", methods=["POST"])
def get_gym_entries():
    data = request.get_json()
    start = data["start_date"]
    end = data["end_date"]
    resp = notion.databases.query(
        database_id=GYM_LOG_DB_ID,
        filter={
            "property": "Date",
            "date": {
                "on_or_after": start,
                "on_or_before": end
            }
        }
    )
    entries = []
    for page in resp.get("results", []):
        p = page["properties"]
        entries.append({
            "date":           p["Date"]["date"]["start"],
            "exercise":       "".join(t["plain_text"] for t in p["Exercise"]["title"]),
            "weight":         "".join(rt["plain_text"] for rt in p["Weight"]["rich_text"]),
            "reps_time":      "".join(rt["plain_text"] for rt in p["Reps / Time"]["rich_text"]),
            "sets":           p["Sets"]["number"],
            "type":           p["Type"]["select"]["name"],
            "notes":          "".join(rt["plain_text"] for rt in p["Notes"]["rich_text"]),
            "session_id":     p["Session"]["relation"][0]["id"] if p.get("Session") and p["Session"].get("relation") else None
        })
    return jsonify(entries), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

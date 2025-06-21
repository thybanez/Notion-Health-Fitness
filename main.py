import os
from notion_client import Client
from datetime import datetime

# Notion API credentials
NOTION_API_KEY = os.environ["NOTION_API_KEY"]
FOOD_LOG_DB_ID = os.environ["FOOD_LOG_DB_ID"]
DAILY_LOG_DB_ID = os.environ["DAILY_LOG_DB_ID"]
WORKOUT_LOG_DB_ID = os.environ["WORKOUT_LOG_DB_ID"]

notion = Client(auth=NOTION_API_KEY)

# Get or create a Daily Log entry by date
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

# Create a food entry
def create_food_entry(date_str, meal, description, calories, protein, carbs, fat, sugar, high_sugar, cholesterol_risk):
    try:
        daily_log_id = get_or_create_daily_log_page(date_str)

        notion.pages.create({
            "parent": {"database_id": FOOD_LOG_DB_ID},
            "properties": {
                "Date": {"date": {"start": date_str}},
                "Meal": {"select": {"name": meal}},
                "Food Description": {"rich_text": [{"text": {"content": description}}]},
                "Calories (kcal)": {"number": calories},
                "Protein (g)": {"number": protein},
                "Carbs (g)": {"number": carbs},
                "Fat (g)": {"number": fat},
                "Total Sugar (g)": {"number": sugar},
                "High Sugar?": {"checkbox": high_sugar},
                "Cholesterol Risk": {"select": {"name": cholesterol_risk}},
                "Date (Daily Log)": {"relation": [{"id": daily_log_id}]}
            }
        })
        print(f"✅ Logged: {meal} on {date_str}")

    except Exception as e:
        print(f"❌ Food entry failed: {e}")

# Create a workout entry
def create_workout_entry(date_str, workout_type, duration_minutes, description="", calories_burned=None, rpe=None):
    try:
        daily_log_id = get_or_create_daily_log_page(date_str)

        properties = {
            "Date": {"date": {"start": date_str}},
            "Type": {"select": {"name": workout_type}},
            "Duration (min)": {"number": duration_minutes},
            "Description": {"rich_text": [{"text": {"content": description}}]},
            "Date (Daily Log)": {"relation": [{"id": daily_log_id}]}
        }

        if calories_burned is not None:
            properties["Calories Burned (kcal)"] = {"number": calories_burned}
        if rpe is not None:
            properties["RPE (1-10)"] = {"number": rpe}

        notion.pages.create({
            "parent": {"database_id": WORKOUT_LOG_DB_ID},
            "properties": properties
        })

        print(f"✅ Workout logged for {date_str}: {workout_type}")

    except Exception as e:
        print(f"❌ Workout entry failed: {e}")

# Main trigger
def main():
    print("🔄 Ready to receive data entries via ChatGPT.")

if __name__ == "__main__":
    main()

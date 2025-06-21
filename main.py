import os
import argparse
from notion_client import Client
from datetime import datetime

# Notion API credentials
NOTION_API_KEY = os.environ["NOTION_API_KEY"]
FOOD_LOG_DB_ID = os.environ["FOOD_LOG_DB_ID"]
DAILY_LOG_DB_ID = os.environ["DAILY_LOG_DB_ID"]

notion = Client(auth=NOTION_API_KEY)

# 🔎 Helper: Get page ID from Daily Log based on date
def get_daily_log_page_id(date_str):
    response = notion.databases.query(
        {
            "database_id": DAILY_LOG_DB_ID,
            "filter": {
                "property": "Log Date",
                "date": {
                    "equals": date_str
                }
            }
        }
    )
    results = response.get("results")
    if results:
        return results[0]["id"]
    else:
        raise Exception(f"No Daily Log found for {date_str}")

# 🧾 Create a new food log entry
def create_food_entry(date_str, meal_type, description, calories, protein, carbs, fat, sugar, high_sugar, cholesterol_risk):
    try:
        daily_log_id = get_daily_log_page_id(date_str)

        notion.pages.create(
            {
                "parent": {"database_id": FOOD_LOG_DB_ID},
                "properties": {
                    "Date": {"date": {"start": date_str}},
                    "Meal": {"select": {"name": meal_type}},
                    "Food Description": {
                        "rich_text": [{"text": {"content": description}}]
                    },
                    "Calories (kcal)": {"number": calories},
                    "Protein (g)": {"number": protein},
                    "Carbs (g)": {"number": carbs},
                    "Fat (g)": {"number": fat},
                    "Total Sugar (g)": {"number": sugar},
                    "High Sugar?": {"checkbox": high_sugar},
                    "Cholesterol Risk": {"select": {"name": cholesterol_risk}},
                    "Date (Daily Log)": {
                        "relation": [{"id": daily_log_id}]
                    }
                }
            }
        )
        print(f"✅ Food entry for {meal_type} on {date_str} created successfully.")

    except Exception as e:
        print(f"❌ Failed to create food entry: {e}")

# 🚀 Run your daily automation entry
def main():
    # Example daily entry (can be replaced with live inputs later)
    create_food_entry(
        date_str="2025-06-21",
        meal_type="Lunch",
        description="Fish soup with rice (clear broth, greens, sliced fish)",
        calories=420,
        protein=30,
        carbs=55,
        fat=8,
        sugar=3,
        high_sugar=False,
        cholesterol_risk="None"
    )

# 📦 One-time historical entries
def run_backfill_entries():
    entries = [
        {
            "date_str": "2025-06-20",
            "meal_type": "Lunch",
            "description": "Mixed veg rice: 1 bowl rice, cabbage, tofu, chicken cutlet",
            "calories": 820,
            "protein": 37,
            "carbs": 74,
            "fat": 39.5,
            "sugar": 8,
            "high_sugar": False,
            "cholesterol_risk": "Fried, Egg-based"
        },
        {
            "date_str": "2025-06-21",
            "meal_type": "Lunch",
            "description": "Fish soup with rice (clear broth, greens, sliced fish)",
            "calories": 420,
            "protein": 30,
            "carbs": 55,
            "fat": 8,
            "sugar": 3,
            "high_sugar": False,
            "cholesterol_risk": "None"
        },
        {
            "date_str": "2025-06-21",
            "meal_type": "Drinks",
            "description": "Coconut water",
            "calories": 46,
            "protein": 0.2,
            "carbs": 11,
            "fat": 0,
            "sugar": 9,
            "high_sugar": False,
            "cholesterol_risk": "None"
        }
    ]

    for entry in entries:
        create_food_entry(**entry)

# 🏁 Entrypoint
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--backfill", action="store_true", help="Run backfill entries instead of daily entry")
    args = parser.parse_args()

    if args.backfill:
        print("🚀 Running backfill entries...")
        run_backfill_entries()
    else:
        print("📌 Running main daily entry...")
        main()

import os
from notion_client import Client
from datetime import datetime
import sys

# Notion API credentials
NOTION_API_KEY = os.environ["NOTION_API_KEY"]
FOOD_LOG_DB_ID = os.environ["FOOD_LOG_DB_ID"]
DAILY_LOG_DB_ID = os.environ["DAILY_LOG_DB_ID"]

notion = Client(auth=NOTION_API_KEY)

# Create or find the Daily Log entry
def get_or_create_daily_log(date_str):
    try:
        response = notion.databases.query(
            database_id=DAILY_LOG_DB_ID,
            filter={
                "property": "Log Date",
                "date": {
                    "equals": date_str
                }
            }
        )
        results = response.get("results")
        if results:
            return results[0]["id"]

        # If not found, create new Daily Log
        new_page = notion.pages.create(
            parent={"database_id": DAILY_LOG_DB_ID},
            properties={
                "Log Date": {"date": {"start": date_str}}
            }
        )
        return new_page["id"]

    except Exception as e:
        print(f"❌ Error with Daily Log on {date_str}: {e}")
        raise

# Create food entry
def create_food_entry(date_str, meal_type, description, calories, protein, carbs, fat, sugar, high_sugar, cholesterol_risk):
    try:
        daily_log_id = get_or_create_daily_log(date_str)

        notion.pages.create(
            parent={"database_id": FOOD_LOG_DB_ID},
            properties={
                "Date": {"date": {"start": date_str}},
                "Meal": {"select": {"name": meal_type}},
                "Food Description": {
                    "rich_text": [{"text": {"content": description}}]
                },
                "Calories": {"number": calories},
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
        )
        print(f"✅ Logged {meal_type} on {date_str}: {description}")

    except Exception as e:
        print(f"❌ Failed to log {meal_type} on {date_str}: {e}")

# Main function to backfill data
def main():
    entries = [
        {
            "date": "2025-06-20",
            "meal_type": "Breakfast",
            "description": "Ya Kun Kaya Butter Toast Set (2 slices toast, 2 soft boiled eggs, kopi C siew dai)",
            "calories": 460,
            "protein": 13,
            "carbs": 45,
            "fat": 22,
            "sugar": 13,
            "high_sugar": True,
            "cholesterol_risk": "Egg-based"
        },
        {
            "date": "2025-06-20",
            "meal_type": "Lunch",
            "description": "Mixed veg rice: 1 bowl rice, cabbage, tofu, chicken cutlet",
            "calories": 820,
            "protein": 37,
            "carbs": 74,
            "fat": 39.5,
            "sugar": 8,
            "high_sugar": False,
            "cholesterol_risk": "Fried"
        },
        {
            "date": "2025-06-20",
            "meal_type": "Dessert",
            "description": "McDonald's ChocoCone and small iced lemon tea",
            "calories": 260,
            "protein": 3,
            "carbs": 37,
            "fat": 8,
            "sugar": 27,
            "high_sugar": True,
            "cholesterol_risk": "Sugar-heavy"
        },
        {
            "date": "2025-06-20",
            "meal_type": "Drinks",
            "description": "Yakult Apple (100ml) and Rickshaw Jasmine Tea",
            "calories": 75,
            "protein": 1,
            "carbs": 17,
            "fat": 0,
            "sugar": 15,
            "high_sugar": True,
            "cholesterol_risk": "None"
        },
        {
            "date": "2025-06-21",
            "meal_type": "Breakfast",
            "description": "1 hot latte (espresso + 6oz milk), 1 slice pandan bread",
            "calories": 170,
            "protein": 6,
            "carbs": 22,
            "fat": 5,
            "sugar": 8,
            "high_sugar": False,
            "cholesterol_risk": "None"
        },
        {
            "date": "2025-06-21",
            "meal_type": "Drinks",
            "description": "Huel Black Cookies & Cream with 250ml Meiji fresh milk",
            "calories": 300,
            "protein": 30,
            "carbs": 16,
            "fat": 11,
            "sugar": 4,
            "high_sugar": False,
            "cholesterol_risk": "None"
        },
        {
            "date": "2025-06-21",
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
            "date": "2025-06-21",
            "meal_type": "Drinks",
            "description": "Fresh Coconut Water",
            "calories": 60,
            "protein": 1,
            "carbs": 14,
            "fat": 0,
            "sugar": 13,
            "high_sugar": True,
            "cholesterol_risk": "None"
        },
    ]

    for e in entries:
        create_food_entry(
            e["date"], e["meal_type"], e["description"],
            e["calories"], e["protein"], e["carbs"], e["fat"],
            e["sugar"], e["high_sugar"], e["cholesterol_risk"]
        )
    
    print("🎉 Backfill complete!")
    sys.exit()

if __name__ == "__main__":
    main()

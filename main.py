import os
from notion_client import Client
from datetime import datetime

# Notion API credentials
NOTION_API_KEY = os.environ["NOTION_API_KEY"]
FOOD_LOG_DB_ID = os.environ["FOOD_LOG_DB_ID"]
DAILY_LOG_DB_ID = os.environ["DAILY_LOG_DB_ID"]

notion = Client(auth=NOTION_API_KEY)

# Helper: Get page ID from Daily Log based on date
def get_daily_log_page_id(date_str):
    response = notion.databases.query(
        **{
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

# Create new food entry
def create_food_entry(date_str, meal_type, description, calories, protein, carbs, fat, sugar, high_sugar, cholesterol_risk):
    try:
        daily_log_id = get_daily_log_page_id(date_str)

        notion.pages.create(
            **{
                "parent": {"database_id": FOOD_LOG_DB_ID},
                "properties": {
                    "Date": {"date": {"start": date_str}},
                    "Meal Type": {"select": {"name": meal_type}},
                    "Food Description": {
                        "rich_text": [{"text": {"content": description}}]
                    },
                    "Calories (kcal)": {"number": calories},
                    "Protein (g)": {"number": protein},
                    "Carbohydrates (g)": {"number": carbs},
                    "Fat (g)": {"number": fat},
                    "Total Sugar (g)": {"number": sugar},
                    "High Sugar?": {"checkbox": high_sugar},
                    "Cholesterol Risk": {"select": {"name": cholesterol_risk}},
                    "Related Daily Log": {
                        "relation": [{"id": daily_log_id}]
                    }
                }
            }
        )
        print(f"✅ Food entry for {meal_type} on {date_str} created successfully.")

    except Exception as e:
        print(f"❌ Failed to create food entry: {e}")

# 🧪 Test with 1 meal – Fish Soup with Rice
def main():
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

if __name__ == "__main__":
    main()

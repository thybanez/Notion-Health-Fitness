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
    response = notion.databases.query(
        database_id=DAILY_LOG_DB_ID,
        filter={
            "property": "Log Date",
            "date": {"equals": date_str}
        }
    )
    results = response.get("results")
    if results:
        return results[0]["id"]
    else:
        new_page = notion.pages.create(
            parent={"database_id": DAILY_LOG_DB_ID},
            properties={
                "Log Date": {"date": {"start": date_str}}
            }
        )
        return new_page["id"]

# Create a food entry
def create_food_entry(date_str, meal, description, calories, protein, carbs, fat, sugar, high_sugar, cholesterol_risk):
    try:
        daily_log_id = get_or_create_daily_log_page(date_str)

        notion.pages.create(
            parent={"database_id": FOOD_LOG_DB_ID},
            properties={
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
        )
        print(f"✅ Logged: {meal} on {date_str}")

    except Exception as e:
        print(f"❌ Food entry failed: {e}")

# Create a workout entry
def create_workout_entry(date_str, workout_type, duration_minutes, notes=""):
    try:
        daily_log_id = get_or_create_daily_log_page(date_str)

        notion.pages.create(
            parent={"database_id": WORKOUT_LOG_DB_ID},
            properties={
                "Date": {"date": {"start": date_str}},
                "Type": {"select": {"name": workout_type}},
                "Duration (mins)": {"number": duration_minutes},
                "Notes": {"rich_text": [{"text": {"content": notes}}]},
                "Date (Daily Log)": {"relation": [{"id": daily_log_id}]}
            }
        )
        print(f"✅ Workout logged for {date_str}: {workout_type}")

    except Exception as e:
        print(f"❌ Workout entry failed: {e}")

# TEST SECTION (Clear once working)
def main():
    create_food_entry(
        date_str="2025-06-20",
        meal="Breakfast",
        description="Ya Kun Kaya Butter Toast Set with large Kopi C Siew Dai",
        calories=420,
        protein=10,
        carbs=50,
        fat=20,
        sugar=12,
        high_sugar=True,
        cholesterol_risk="Egg-based"
    )

    create_food_entry(
        date_str="2025-06-20",
        meal="Lunch",
        description="Mixed vegetable rice: 1 bowl rice, cabbage, tofu, chicken cutlet",
        calories=820,
        protein=37,
        carbs=74,
        fat=39.5,
        sugar=8,
        high_sugar=False,
        cholesterol_risk="Fried, Egg-based"
    )

    create_food_entry(
        date_str="2025-06-20",
        meal="Dessert",
        description="Chococone from McDonald's and 1 small Ice Lemon Tea",
        calories=310,
        protein=4,
        carbs=42,
        fat=14,
        sugar=31,
        high_sugar=True,
        cholesterol_risk="None"
    )

    create_workout_entry(
        date_str="2025-06-21",
        workout_type="Tennis",
        duration_minutes=60,
        notes="1 hr tennis session in the morning"
    )

if __name__ == "__main__":
    main()

import os
from notion_client import Client
from datetime import datetime

# Load environment variables
NOTION_SECRET = os.getenv("NOTION_SECRET")
DAILY_LOG_DB_ID = os.getenv("DAILY_LOG_DB_ID")
FOOD_LOG_DB_ID = os.getenv("FOOD_LOG_DB_ID")
WORKOUT_LOG_DB_ID = os.getenv("WORKOUT_LOG_DB_ID")

notion = Client(auth=NOTION_SECRET)

def create_food_entry(date, meal, description, calories, protein, fat, carbs, cholesterol_flag):
    notion.pages.create(
        parent={"database_id": FOOD_LOG_DB_ID},
        properties={
            "Date (Daily Log)": {"date": {"start": date}},
            "Meal": {"select": {"name": meal}},
            "Food Description": {"title": [{"text": {"content": description}}]},
            "Calories": {"number": calories},
            "Protein (g)": {"number": protein},
            "Fat (g)": {"number": fat},
            "Carbs (g)": {"number": carbs},
            "⚠️ Cholesterol Risk": {"rich_text": [{"text": {"content": cholesterol_flag}}]}
        }
    )

def create_workout_entry(date, type_, description, duration, calories_burned, rpe):
    notion.pages.create(
        parent={"database_id": WORKOUT_LOG_DB_ID},
        properties={
            "Date (Daily Log)": {"date": {"start": date}},
            "Type": {"select": {"name": type_}},
            "Description": {"title": [{"text": {"content": description}}]},
            "Duration (min)": {"number": duration},
            "Calories Burned": {"number": calories_burned},
            "RPE (1–10)": {"number": rpe}
        }
    )

def main():
    # Sample food log backfill: June 20
    create_food_entry("2025-06-20", "Lunch", "Mixed veg rice: 1 bowl rice, cabbage, tofu, chicken cutlet", 820, 37, 39.5, 74, "Fried, Egg-based")
    create_food_entry("2025-06-20", "Snack", "Apple-flavoured Yakult", 60, 1, 0, 13, "")
    create_food_entry("2025-06-20", "Dinner", "Seafood risotto", 580, 35, 12, 60, "")

    # Sample workout: June 21
    create_workout_entry("2025-06-21", "Sports", "1 hour tennis lesson", 60, 450, 7)

if __name__ == "__main__":
    main()

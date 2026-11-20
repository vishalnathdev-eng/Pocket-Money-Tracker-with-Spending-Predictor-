"""Pocket Money Tracker with Spending Predictor
Course: Computational Thinking and Programming (2026CSAE100)

Beginner-friendly console application using functions, lists, tuples, loops,
conditionals, bubble sort, CSV file handling, and simple data analysis.
"""

import csv
from pathlib import Path

# ------------------------------
# PROJECT DATA AND FILE LOCATIONS
# ------------------------------
CATEGORIES = ("Food", "Travel", "Books", "Entertainment", "Other")
CATEGORY_LIMITS = [1000, 600, 500, 400, 400]
DEFAULT_POCKET_MONEY = 3000
DAYS_IN_MONTH = 30

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPENSES_FILE = DATA_DIR / "expenses.csv"
SETTINGS_FILE = DATA_DIR / "settings.csv"

# Every expense is stored as [category, amount, day_of_month].
expenses = []
# A one-item list allows the value to be updated inside functions.
pocket_money = [DEFAULT_POCKET_MONEY]

# Starting sample records are provided for the first demonstration.
# Remove these sample rows from data/expenses.csv when you want a fresh tracker.
SAMPLE_EXPENSES = [
    ["Food", 120, 1],
    ["Travel", 60, 2],
    ["Books", 250, 3],
    ["Food", 90, 4],
    ["Entertainment", 200, 6],
    ["Food", 150, 8],
    ["Travel", 80, 9],
    ["Other", 50, 10],
    ["Entertainment", 300, 10],
]


# ------------------------------
# CSV FILE HANDLING
# ------------------------------
def save_expenses():
    """Save all expense records to the CSV file. Return True on success."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with EXPENSES_FILE.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["category", "amount", "day"])
            writer.writerows(expenses)
        return True
    except OSError as error:
        print("Could not save expenses:", error)
        return False


def load_expenses():
    """Load valid expense rows from CSV; create a sample file if none exists."""
    global expenses
    expenses = []

    if not EXPENSES_FILE.exists():
        expenses = [row.copy() for row in SAMPLE_EXPENSES]
        if save_expenses():
            print("Sample expense data created in data/expenses.csv.")
        return

    try:
        with EXPENSES_FILE.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            required = {"category", "amount", "day"}
            if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                print("Warning: CSV headings are missing or incorrect. Starting with no expenses.")
                return

            skipped = 0
            for row in reader:
                try:
                    category = row["category"].strip()
                    amount = int(row["amount"])
                    day = int(row["day"])
                    if category not in CATEGORIES or not (1 <= amount <= 100000) or not (1 <= day <= DAYS_IN_MONTH):
                        skipped += 1
                        continue
                    expenses.append([category, amount, day])
                except (TypeError, ValueError, AttributeError):
                    skipped += 1

            if skipped:
                print("Warning:", skipped, "invalid CSV row(s) were skipped.")
            print("Loaded", len(expenses), "expense record(s).")
    except (OSError, csv.Error) as error:
        print("Could not read expenses file:", error)


def save_settings():
    """Save the monthly pocket-money amount in a small CSV settings file."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with SETTINGS_FILE.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["setting", "value"])
            writer.writerow(["pocket_money", pocket_money[0]])
        return True
    except OSError as error:
        print("Could not save settings:", error)
        return False


def load_settings():
    """Load the saved monthly pocket-money amount, or use the default."""
    pocket_money[0] = DEFAULT_POCKET_MONEY
    if not SETTINGS_FILE.exists():
        save_settings()
        return

    try:
        with SETTINGS_FILE.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row.get("setting") == "pocket_money":
                    value = int(row.get("value", ""))
                    if 1 <= value <= 100000:
                        pocket_money[0] = value
                    else:
                        print("Warning: saved pocket money is outside the valid range. Default used.")
                    return
    except (OSError, csv.Error, TypeError, ValueError) as error:
        print("Could not read settings file. Default pocket money used:", error)


# ------------------------------
# INPUT VALIDATION
# ------------------------------
def get_number(message, low, high):
    """Keep asking until the user enters a whole number in the given range."""
    while True:
        text = input(message).strip()
        if text.isdigit():
            number = int(text)
            if low <= number <= high:
                return number
            print("Please enter a number from", low, "to", high)
        else:
            print("Invalid input. Enter a whole number.")


# ------------------------------
# CALCULATION AND RANKING
# ------------------------------
def total_spent():
    total = 0
    for expense in expenses:
        total += expense[1]
    return total


def category_spent(category):
    total = 0
    for expense in expenses:
        if expense[0] == category:
            total += expense[1]
    return total


def last_day():
    latest = 0
    for expense in expenses:
        if expense[2] > latest:
            latest = expense[2]
    return latest


def make_ranking():
    """Return (amount, category, limit) tuples, highest spending first."""
    ranking = []
    for index in range(len(CATEGORIES)):
        category = CATEGORIES[index]
        ranking.append((category_spent(category), category, CATEGORY_LIMITS[index]))

    # Bubble sort: swap adjacent entries when the left amount is smaller.
    for i in range(len(ranking)):
        for j in range(len(ranking) - 1 - i):
            if ranking[j][0] < ranking[j + 1][0]:
                ranking[j], ranking[j + 1] = ranking[j + 1], ranking[j]
    return ranking


# ------------------------------
# MENU FEATURES
# ------------------------------
def add_expense():
    print("\nExpense categories:")
    for index, category in enumerate(CATEGORIES, start=1):
        print(str(index) + ". " + category)

    pick = get_number("Choose category number: ", 1, len(CATEGORIES))
    category = CATEGORIES[pick - 1]
    amount = get_number("Amount spent in Rs. (1-100000): ", 1, 100000)
    day = get_number("Day of the month (1-30): ", 1, DAYS_IN_MONTH)

    expenses.append([category, amount, day])
    print("Expense added.")
    save_expenses()

    spent = category_spent(category)
    limit = CATEGORY_LIMITS[pick - 1]
    if spent > limit:
        print("WARNING: You crossed the", category, "limit! Spent Rs.", spent, "of Rs.", limit)
    else:
        print(category, "spending is within its limit (Rs.", spent, "of Rs.", limit, ").")


def view_expenses():
    if not expenses:
        print("No expenses yet.")
        return

    print("\nNo. | Category       | Amount | Day")
    print("-" * 43)
    for number, expense in enumerate(expenses, start=1):
        print(f"{number:>3} | {expense[0]:<14} | Rs. {expense[1]:>5} | {expense[2]:>2}")
    print("-" * 43)
    print("Total spent: Rs.", total_spent())


def show_summary():
    if not expenses:
        print("No expenses yet.")
        return

    spent_total = total_spent()
    money_left = pocket_money[0] - spent_total
    print("\nPocket money : Rs.", pocket_money[0])
    print("Total spent  : Rs.", spent_total)
    print("Money left   : Rs.", money_left)
    print("\nCategories ranked by spending:")

    ranking = make_ranking()
    for rank, item in enumerate(ranking, start=1):
        amount, category, limit = item
        share = (amount / spent_total * 100) if spent_total else 0
        status = "OVER LIMIT" if amount > limit else "OK"
        print(f"{rank}. {category}: Rs. {amount} ({share:.1f}% of spending, limit Rs. {limit}) {status}")

    print("\nHighest spending category:", ranking[0][1])


def show_prediction():
    if not expenses:
        print("No expenses yet.")
        return

    spent = total_spent()
    money_left = pocket_money[0] - spent
    days_passed = last_day()
    days_remaining = DAYS_IN_MONTH - days_passed
    daily_average = spent / days_passed if days_passed else 0

    print("\nDays passed so far      :", days_passed)
    print("Average spending per day: Rs.", round(daily_average, 1))
    print("Money left              : Rs.", money_left)

    if money_left <= 0:
        print("You have used all your pocket money!")
    elif days_remaining <= 0:
        print("The month is over. Money left: Rs.", money_left)
    elif daily_average <= 0:
        print("Not enough spending data to calculate a prediction.")
    else:
        days_will_last = money_left / daily_average
        safe_daily = money_left / days_remaining
        if days_will_last >= days_remaining:
            print("You are ON TRACK. Your money is predicted to last till the end of the month.")
        else:
            print("WARNING: At this speed your money may last only about", round(days_will_last, 1), "more days.")
            print("There are", days_remaining, "days left in the month.")
            print("Suggested maximum spending: Rs.", round(safe_daily, 1), "per day.")


def change_pocket_money():
    pocket_money[0] = get_number("Enter new monthly pocket money in Rs. (1-100000): ", 1, 100000)
    if save_settings():
        print("Pocket money updated and saved.")
    else:
        print("Pocket money updated for this session, but could not be saved.")


def show_bar_chart():
    """Display a text bar chart scaled to the highest category amount."""
    if not expenses:
        print("No expenses to display.")
        return

    values = [(category, category_spent(category)) for category in CATEGORIES]
    highest = max((amount for _, amount in values), default=0)
    print("\nSPENDING BY CATEGORY")
    print("# represents the relative amount spent; longest bar is 30 characters.\n")
    for category, amount in values:
        bar_length = round((amount / highest) * 30) if highest else 0
        bar = "#" * bar_length
        print(f"{category:<15} {bar:<30} Rs. {amount}")


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    load_settings()
    load_expenses()

    while True:
        print("\n===== Pocket Money Tracker =====")
        print("1. Add an expense")
        print("2. View all expenses")
        print("3. Category summary and ranking")
        print("4. Spending prediction and advice")
        print("5. Change monthly pocket money")
        print("6. Category spending bar chart")
        print("0. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            show_summary()
        elif choice == "4":
            show_prediction()
        elif choice == "5":
            change_pocket_money()
        elif choice == "6":
            show_bar_chart()
        elif choice == "0":
            print("Goodbye! Your expense data is stored in data/expenses.csv.")
            break
        else:
            print("Invalid choice. Enter a number from the menu.")


if __name__ == "__main__":
    main()

import calendar
import re
import sqlite3
from datetime import datetime

import requests
from bs4 import BeautifulSoup


class Logger:
    """Log all the request and return some stats based on them"""

    def __init__(self, database_name):
        """Class constructor"""

        # Database where everything is stored
        self.DATABASE = database_name

        with sqlite3.connect(self.DATABASE) as conn:
            c = conn.cursor()

            # Create the table on first run
            query = (
                "CREATE TABLE IF NOT EXISTS request("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "date DATE,"
                "place TEXT,"
                "meal TEXT)"
            )
            c.execute(query)
            conn.commit()

    def log_request(self, place, meal):
        """Insert request in the database"""

        with sqlite3.connect(self.DATABASE) as conn:
            cursor = conn.cursor()

            # Get current date
            now = datetime.now()
            date = now.strftime("%Y-%m-%d %H:%M:%S")
            data = (date, place, meal)

            # Insert request
            query = "INSERT INTO request(date, place, meal) VALUES(?, ?, ?)"
            cursor.execute(query, data)
            conn.commit()

    def get_stats(self):
        # Get today's date
        now = datetime.now()
        month = now.month
        year = now.year

        results = {
            "total": 0,
            "requests": {
                year: {
                    month: {}
                }
            }
        }

        # Initialize all days of the month with 0
        month_days = calendar.monthrange(year, month)[1]
        for day in range(1, month_days + 1):
            results["requests"][year][month][day] = 0

        with sqlite3.connect(self.DATABASE) as conn:
            cursor = conn.cursor()

            # Count total amount of requests
            cursor.execute("SELECT count(*) FROM request")
            results["total"] = cursor.fetchone()[0]

            # Aggregate requests for the current month in a single query
            month_str = f"{year}-{month:02d}"
            cursor.execute(
                "SELECT CAST(strftime('%d', date) AS INTEGER), count(*) "
                "FROM request WHERE strftime('%Y-%m', date) = ? "
                "GROUP BY 1",
                (month_str,)
            )

            month_total = 0
            for day, count in cursor.fetchall():
                results["requests"][year][month][day] = count
                month_total += count

            results["requests"][year][month]["total"] = month_total

        return results


def get_menu(place, date, meal):
    """
    Return the menu in JSON format
    """
    # Prepare data structure
    data = {
        "menu": {
            "first": [],
            "second": [],
            "side": [],
            "fruit": [],
        },
        "empty": True,
        "error": False,
        "meal": meal,
        "place": place,
    }

    # Convert date to the right format
    date = date.replace("-", "_")
    date = date.split("_")[2] + "_" + date.split("_")[0] + "_" + date.split("_")[1]

    place_upper = place.upper()
    place = place.capitalize()

    # Request the raw data
    try:
        r = requests.get(
            f"https://menu.erdis.it/MENSA_{place_upper}/Menu_Del_Giorno_{date}_{place}.html",
            timeout=10,
        )
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("> Connection error...")
        data["error"] = True
        return data

    # Parse HTML
    soup = BeautifulSoup(r.text, "html.parser")
    trs = soup.find_all("tr")

    # Retrive soups
    soups = {}

    for tr in trs:
        if "Pranzo" in str(tr.find("td")):
            soups["pranzo"] = tr
        elif "Cena" in str(tr.find("td")):
            soups["cena"] = tr

    target = ""

    # Pattern to exclude allergens and other garbage
    pattern = re.compile("[^A-z ]")

    # Exclude what we don't need
    wanted = ["primo", "secondo", "contorno", "frutta", "salumi e formaggi"]
    not_wanted = ["pranzo", "cena", "non disponibili"]
    menus = {
        "pranzo": {
            "primo": [],
            "secondo": [],
            "contorno": [],
            "frutta": [],
            "salumi e formaggi": [],
        },
        "cena": {
            "primo": [],
            "secondo": [],
            "contorno": [],
            "frutta": [],
            "salumi e formaggi": [],
        },
    }

    # Search for what we need
    for soup in soups:
        for td in soups[soup].find_all("td")[1:]:
            text = td.text.strip().lower()

            if text in wanted:
                target = text
            elif text not in not_wanted and target != "":
                # Remove all non alphabetic characters
                text = pattern.sub("", text)

                # Remove some unwanted stuff :)
                text = text.replace("erdis", "")

                # Clean the text
                text = text.capitalize().strip()

                if text:
                    menus[soup][target].append(text)
            elif "cena" in text:
                break

    # Get desired menu
    if meal == "lunch":
        data["menu"]["first"] = menus["pranzo"]["primo"]
        data["menu"]["second"] = menus["pranzo"]["secondo"]
        data["menu"]["side"] = menus["pranzo"]["contorno"]
        data["menu"]["fruit"] = menus["pranzo"]["frutta"]
        data["menu"]["cheese"] = menus["pranzo"]["salumi e formaggi"]
    elif meal == "dinner":
        data["menu"]["first"] = menus["cena"]["primo"]
        data["menu"]["second"] = menus["cena"]["secondo"]
        data["menu"]["side"] = menus["cena"]["contorno"]
        data["menu"]["fruit"] = menus["cena"]["frutta"]
        data["menu"]["cheese"] = menus["cena"]["salumi e formaggi"]

    # Check if the menu is empty
    for key in data["menu"]:
        if data["menu"][key]:
            data["empty"] = False

    # Return the JSON menu
    return data

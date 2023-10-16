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
        month = datetime.now().month
        year = datetime.now().year

        results = {}

        with sqlite3.connect(self.DATABASE) as conn:
            cursor = conn.cursor()

            # Count total amount of requests
            query = "SELECT count(*) FROM request"
            cursor.execute(query)
            results["total"] = cursor.fetchone()[0]

            results["requests"] = {}

            results["requests"][year] = {}

            # Total requests in the current month
            month_total = 0

            # Struct to store the data
            results["requests"][year][month] = {}

            # Check how many days are in current month
            month_days = calendar.monthrange(int(year), month)[1] + 1

            # Loop through month days
            for day in range(1, month_days):
                # Prepare data for query
                curr_month = str(month).zfill(2)
                next_day = str(day + 1).zfill(2)
                today = str(day).zfill(2)
                data = (
                    "{0}-{1}-{2}".format(year, curr_month, today),
                    "{0}-{1}-{2}".format(year, curr_month, next_day),
                )

                # Create query to get requests in given day
                query = "SELECT count(*) FROM request WHERE " "date BETWEEN ? AND ?"
                cursor.execute(query, data)

                # Put the result in the dict
                req = cursor.fetchone()[0]
                results["requests"][year][month][day] = req

                # Sum the requests
                month_total += req

                # Store the total in the result
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

    place = place.capitalize()

    # Request the raw data
    try:
        r = requests.get(
            f"https://www.erdis.it/menu/Mensa_{place}/Menu_Del_Giorno_{date}_{place}.html"
        )
    except requests.exceptions.ConnectionError:
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

    # Pattern to exclude allergens
    pattern = re.compile("([a-z]+)")

    # Exclude what we don't need
    wanted = ["primo", "secondo", "contorno", "frutta"]
    not_wanted = ["pranzo", "cena", "non disponibili"]
    menus = {
        "pranzo": {
            "primo": [],
            "secondo": [],
            "contorno": [],
            "frutta": [],
        },
        "cena": {
            "primo": [],
            "secondo": [],
            "contorno": [],
            "frutta": [],
        },
    }

    # Search for what we need
    for soup in soups:
        for td in soups[soup].find_all("td")[1:]:
            text = td.text.strip().lower()

            if text in wanted:
                target = text
            elif pattern.match(text) and text not in not_wanted and target != "":
                menus[soup][target].append(text.capitalize())
            elif "cena" in text:
                break

    # Get desired menu
    if meal == "lunch":
        data["menu"]["first"] = menus["pranzo"]["primo"]
        data["menu"]["second"] = menus["pranzo"]["secondo"]
        data["menu"]["side"] = menus["pranzo"]["contorno"]
        data["menu"]["fruit"] = menus["pranzo"]["frutta"]
    elif meal == "dinner":
        data["menu"]["first"] = menus["cena"]["primo"]
        data["menu"]["second"] = menus["cena"]["secondo"]
        data["menu"]["side"] = menus["cena"]["contorno"]
        data["menu"]["fruit"] = menus["cena"]["frutta"]

    # Check if the menu is empty
    for key in data["menu"]:
        if data["menu"][key]:
            data["empty"] = False

    # Return the JSON menu
    return data

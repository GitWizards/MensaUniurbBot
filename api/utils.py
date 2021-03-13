import calendar
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
                'CREATE TABLE IF NOT EXISTS request('
                'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                'date DATE,'
                'place TEXT,'
                'meal TEXT)'
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
            query = 'INSERT INTO request(date, place, meal) VALUES(?, ?, ?)'
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
            query = 'SELECT count(*) FROM request'
            cursor.execute(query)
            results['total'] = cursor.fetchone()[0]

            results['requests'] = {}


            # Total requests in the current year
            year_total = 0

            results['requests'][year] = {}

            # Total requests in the current month
            month_total = 0

            # Struct to store the data
            results['requests'][year][month] = {}

            # Check how many days are in current month
            month_days = calendar.monthrange(int(year), month)[1] + 1

            # Loop through month days
            for day in range(1, month_days):
                # Prepare data for query
                curr_month = str(month).zfill(2)
                next_day = str(day+1).zfill(2)
                today = str(day).zfill(2)
                data = (
                    "{0}-{1}-{2}".format(year, curr_month, today),
                    "{0}-{1}-{2}".format(year, curr_month, next_day)
                )

                # Create query to get requests in given day
                query = ('SELECT count(*) FROM request WHERE '
                         'date BETWEEN ? AND ?')
                cursor.execute(query, data)

                # Put the result in the dict
                req = cursor.fetchone()[0]
                results['requests'][year][month][day] = req

                # Sum the requests
                month_total += req

                # Store the total in the result
                results['requests'][year][month]["total"] = month_total

        return results

    def get_full_stats(self):
        results = {}

        with sqlite3.connect(self.DATABASE) as conn:
            cursor = conn.cursor()

            # Count total amount of requests
            query = 'SELECT count(*) FROM request'
            cursor.execute(query)
            results['total'] = cursor.fetchone()[0]

            # Get first request date
            query = "SELECT date FROM request ORDER BY date ASC LIMIT 1"
            cursor.execute(query)
            results['first_request'] = cursor.fetchone()[0]

            # Get last request date
            query = "SELECT date FROM request ORDER BY date DESC LIMIT 1"
            cursor.execute(query)
            results['last_request'] = cursor.fetchone()[0]

            results['requests'] = {}

            # Get all years with requests
            query = "SELECT strftime('%Y', date) FROM request GROUP BY strftime('%Y-%m', date)"
            cursor.execute(query)

            # Loop through years
            for year in cursor.fetchall():
                # Total requests in the current year
                year_total = 0

                # Remove tuple from result
                year = year[0]

                results['requests'][year] = {}

                # Loop through months
                for month in range(1, 13):
                    # Total requests in the current month
                    month_total = 0

                    # Struct to store the data
                    results['requests'][year][month] = {}

                    # Check how many days are in current month
                    month_days = calendar.monthrange(int(year), month)[1] + 1

                    # Loop through month days
                    for day in range(1, month_days):
                        # Prepare data for query
                        curr_month = str(month).zfill(2)
                        next_day = str(day+1).zfill(2)
                        today = str(day).zfill(2)
                        data = (
                            "{0}-{1}-{2}".format(year, curr_month, today),
                            "{0}-{1}-{2}".format(year, curr_month, next_day)
                        )

                        # Create query to get requests in given day
                        query = ('SELECT count(*) FROM request WHERE '
                                 'date BETWEEN ? AND ?')
                        cursor.execute(query, data)

                        # Put the result in the dict
                        req = cursor.fetchone()[0]
                        results['requests'][year][month][day] = req

                        # Sum the requests
                        month_total += req

                    # Store the total in the result
                    results['requests'][year][month]["total"] = month_total

                    # Sum the year's requests
                    year_total += month_total

                # Store the total in the result
                results['requests'][year]["total"] = year_total

        return results

def get_menu(place, date, meal):
    """
    Return the menu in JSON format
    """
    # Convert date to the right format
    date = date.replace('-', '/')

    # Request the raw data
    r = requests.post("http://menu.ersurb.it/menum/menu.asp", data={
        'mensa': place,
        'da': date,
        'a': date
    })

    # Prepare data structure
    data = {}
    data['place'] = place
    data['meal'] = meal
    data['date'] = datetime.now().isoformat()
    data['empty'] = True
    data['menu'] = {}
    data['menu']['first'] = []
    data['menu']['second'] = []
    data['menu']['side'] = []
    data['menu']['fruit'] = []

    # Parse HTML
    soup = BeautifulSoup(r.text, 'html.parser')

    # Some working variables
    prev = '0'
    dinner = False

    # Parse all entries
    for link in soup.find_all('a')[1:]:
        # Clean HTML
        app = link.get('onclick').replace('showModal', '')

        # Get ID
        plate_id = app.split()[1]
        plate_id = plate_id.replace('"', '').replace(',', '')

        # Get name
        name = app.split(', ')[2]
        name = name.replace('"', '').replace(');', '')

        # Remove useless characters
        name = name.replace('*', 'X')

        # Capitalize entries
        name = name.capitalize()

        # Check if we are searching for a lunch menu
        if meal == 'lunch':
            # Check if we finished
            if prev == '40' and plate_id == '10':
                # Stop checking, next plate is from dinner block
                # At this point we are sure that the set is not empty
                break
            else:
                prev = plate_id

            # Put the dish in right position
            if plate_id == '10':
                data['menu']['first'].append(name)
            elif plate_id == '20':
                data['menu']['second'].append(name)
            elif plate_id == '30':
                data['menu']['side'].append(name)
            elif plate_id == '40':
                data['menu']['fruit'].append(name)

        # Check if we are searching for a dinner menu
        elif meal == 'dinner':
            # Check if we can start
            if prev == '40' and plate_id == '10':
                # We are sure that the set is not empty
                dinner = True
            else:
                prev = plate_id

            if dinner:
                # Put the dish in right position
                if plate_id == '10':
                    data['menu']['first'].append(name)
                elif plate_id == '20':
                    data['menu']['second'].append(name)
                elif plate_id == '30':
                    data['menu']['side'].append(name)
                elif plate_id == '40':
                    data['menu']['fruit'].append(name)

    for meal in data['menu']:
        if data['menu'][meal] != []:
            data['empty'] = False

    # Return the JSON menu
    return data

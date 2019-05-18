"""
This module manage all the queries to store users/requests
It uses sqlite3 as database
"""
import sqlite3
from datetime import datetime


class DBManager:
    """Manage all the queries to store users/requests"""

    def __init__(self, database_name):
        """Class constructor"""

        # Database where everything is stored
        self.DB_NAME = database_name

        # Open DB
        conn = sqlite3.connect(self.DB_NAME)
        c = conn.cursor()

        # Create tables
        query = ('CREATE TABLE IF NOT EXISTS user('
                 'chat_id integer primary key,'
                 'username text,'
                 'name text)')
        c.execute(query)

        query = ('CREATE TABLE IF NOT EXISTS request('
                 'id integer primary key autoincrement,'
                 'date date,'
                 'action text)')
        c.execute(query)

        # Close connection
        conn.commit()
        conn.close()

    def register_user(self, chat_id, username, name):
        """Register user in the database"""

        # Open connection
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()

        try:
            # Insert user
            query = ('INSERT INTO user(chat_id, name, username) '
                     'VALUES("{0}", "{1}", "{2}")'.format(chat_id,
                                                          name,
                                                          username))
            cursor.execute(query)
            conn.commit()
        except sqlite3.IntegrityError:
            return 0
        finally:
            # Close connection
            conn.close()
        return 1

    def log_request(self, request):
        """Store the request in the database"""

        # Open connection
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()

        # Get current date
        now = datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")

        # Insert request
        query = ('INSERT INTO request(date, action) '
                 'VALUES("{0}", "{1}")'.format(date, request))
        cursor.execute(query)
        conn.commit()

        # Close connection
        conn.close()

    def get_username(self, chat_id):
        """Return the username (or name if missing) on the corresponding chat_id"""

        # Open connection
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()

        # Get username
        query = 'SELECT username FROM user WHERE chat_id="{0}"'.format(chat_id)
        cursor.execute(query)
        username = cursor.fetchone()[0]

        # If user don't have an username get his name
        if username == "":
            query = 'SELECT name FROM user WHERE chat_id="{0}"'.format(chat_id)
            cursor.execute(query)
            username = cursor.fetchone()[0]
        # Otherwise add '@' to the username for easier access in telegram
        else:
            username = '@' + username

        # Close connection
        conn.close()
        return username

    def get_user_list(self):
        """Return the list of user's chat_ids"""

        # Open connection
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()

        users = []
        # Get users and add them to list
        for user in cursor.execute('SELECT chat_id FROM user'):
            users.append(user[0])

        # Close connection
        conn.close()
        return users

    def get_total_requests(self):
        """Return the total number of requests"""

        # Open connection
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()

        # Count request
        query = 'SELECT count(*) FROM request'
        cursor.execute(query)
        total_requests = cursor.fetchone()[0]

        # Close connection
        conn.close()
        return total_requests

    def get_total_users(self):
        """Return total number of users"""

        # Open connection
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()

        # Count users
        query = 'SELECT count(*) FROM user'
        cursor.execute(query)
        total_users = cursor.fetchone()[0]

        # Close connection
        conn.close()
        return total_users

    def get_requests_in_day(self, date):
        """Return the number of request in given date(YYYY-MM-DD)"""

        # Open connection
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()

        # Get requests in date
        query = ('SELECT count(*) FROM request WHERE date BETWEEN "{0} 00:00:00" '
                 'AND "{0} 23:59:59"'.format(date))
        cursor.execute(query)
        day_uses = cursor.fetchone()[0]

        # Close connection
        conn.close()
        return day_uses

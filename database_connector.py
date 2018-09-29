"""
Here are defined all the functions to interact with the database
"""

import sqlite3
from datetime import datetime

class DatabaseConnector:
    # Constructor
    def __init__(self, database_name):
        # Database where all requests are stored
        self.DB_NAME = database_name

    # todo init database if dont exists
    def register_user(self, chat_id, username, name):
        """
        Register given user to receive news and statistics
        """
        # Open connection to DB
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()

        try:
            query = ('INSERT INTO user(chat_id, name, username, notification, language) '
                     'VALUES("{0}", "{1}", "{2}", "on", "it_IT.UTF-8")'.format(chat_id, name, username))
            cursor.execute(query)
            conn.commit()
        except sqlite3.IntegrityError:
            return 0
        finally:
            # Close connection to DB
            conn.close()
        return 1

    def update_user(self, chat_id, username, full_name):
        """
        Update name and username of missing users
        """
        # Open connection to DB
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()

        try:
            query = ('UPDATE user '
                     'SET username = "{0}", name = "{1}" '
                     'WHERE chat_id = "{2}"'.format(username, full_name, chat_id))
            cursor.execute(query)
            conn.commit()
        except sqlite3.IntegrityError:
            return 0
        finally:
            # Close connection to DB
            conn.close()
        return 1

    def register_request(self, chat_id, request):
        """
        Store in database request made by users
        """
        # Open connection to DB
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()

        # Get current date
        now = datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")

        # Get ID
        query = ('SELECT id FROM action WHERE name == "%s"' % request)
        cursor.execute(query)
        action_id = cursor.fetchone()[0]

        query = ('INSERT INTO request(date, user, action) '
                 'VALUES("{0}", "{1}", "{2}")'.format(date, chat_id, action_id))

        cursor.execute(query)
        conn.commit()

        # Close connection to DB
        conn.close()
        return 1

    def get_username(self, chat_id):
        """
        Return the username from users chat_id
        """
        # Open connection to DB
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()

        # Get username
        query = 'SELECT username FROM user WHERE chat_id = "{0}"'.format(
            chat_id)
        cursor.execute(query)
        username = cursor.fetchone()[0]

        if username == "":
            query = 'SELECT name FROM user WHERE chat_id = "{0}"'.format(
                chat_id)
            cursor.execute(query)
            username = cursor.fetchone()[0]
        else:
            username = '@' + username

        # Close connection to DB
        conn.close()
        return username

    def get_user_list(self):
        """
        Return the list of registred users chat_id
        """
        users = []

        # Open connection to DB
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()

        for user in cursor.execute('SELECT chat_id FROM user'):
            users.append(user[0])

        # Close connection to DB
        conn.close()
        return users

    def get_total_requests(self):
        """
        Get total number of requests made by users
        """
        # Open connection to DB
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()

        query = 'SELECT count(*) FROM request'
        cursor.execute(query)
        total_requests = cursor.fetchone()[0]

        # Close connection to DB
        conn.close()
        return total_requests

    def get_total_users(self):
        """
        Get total number of registered users
        """
        # Open connection to DB
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()

        query = 'SELECT count(*) FROM user'
        cursor.execute(query)
        total_users = cursor.fetchone()[0]

        # Close connection to DB
        conn.close()
        return total_users

    def get_use_in_day(self, date):
        """
        Return the number of request in given DATE (YYYY-MM-DD)
        """
        # Open connection to DB
        conn = sqlite3.connect(self.DB_NAME)
        cursor = conn.cursor()

        query = 'SELECT count(*) FROM request WHERE date BETWEEN "{0} 00:00:00" AND "{0} 23:59:59"'.format(
            date)
        cursor.execute(query)
        day_uses = cursor.fetchone()[0]

        # Close connection to DB
        conn.close()
        return day_uses
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from flask import Flask
from flask_restful import Resource, Api

# Init flask
app = Flask(__name__)
api = Api(app)

PORT = 9543

def get_menu(place, meal, date):
    """
    Return the menu from ERSU page in JSON format
    """
    # Request the raw information from ERSU
    r = requests.post("http://menu.ersurb.it/menum/menu.asp",
                      data={'mensa': place, 'da': date, 'a': date})

    # Prepare some containers for all these data
    data = {}
    data['place'] = place
    data['meal'] = meal
    data['date'] = datetime.now().isoformat()
    data['not_empty'] = False

    data['menu'] = {}
    data['menu']['first'] = []
    data['menu']['second'] = []
    data['menu']['side'] = []
    data['menu']['fruit'] = []

    # Parse the html
    soup = BeautifulSoup(r.text, 'html.parser')

    # Some working variables
    prev_id = '0'
    state_dinner = False

    # Parse all food entries :P
    for link in soup.find_all('a')[1:]:
        # Clean out some HTML
        app = link.get('onclick').replace('showModal', '')

        # Get ID
        idi = app.split()[1]
        idi = idi.replace('"', '').replace(',', '')

        # Get name
        name = app.split(', ')[2]
        name = name.replace('"', '').replace(');', '')

        # Remove useless chars
        name = name.replace('*', 'X')

        # Capitalized entries
        name = name.capitalize()

        # Check if we are searching for a lunch menu
        if meal == 'lunch':
            # Check if we finished working
            if prev_id == '40' and idi == '10':
                # We are sure that the set is not empty
                data['not_empty'] = True

                # Stop searching, next stuff is dinner
                break
            else:
                prev_id = idi

            # Put dish in right position
            if idi == '10':
                data['menu']['first'].append(name)
            elif idi == '20':
                data['menu']['second'].append(name)
            elif idi == '30':
                data['menu']['side'].append(name)
            elif idi == '40':
                data['menu']['fruit'].append(name)

        # Check if we are searching for a dinner menu
        elif meal == 'dinner':
            # Check if we can start working
            if prev_id == '40' and idi == '10':
                # We are sure that the set is not empty
                data['not_empty'] = True

                state_dinner = True
            else:
                prev_id = idi

            if state_dinner:
                # Put dish in right position
                if idi == '10':
                    data['menu']['first'].append(name)
                elif idi == '20':
                    data['menu']['second'].append(name)
                elif idi == '30':
                    data['menu']['side'].append(name)
                elif idi == '40':
                    data['menu']['fruit'].append(name)

    # Return the JSON menu
    return data


class Duca(Resource):
    def get(self, meal, date):
        # We can't use slashes in links so we replace them
        date = date.replace('-', '/')

        return get_menu('duca', meal, date)


class CibusDuca(Resource):
    def get(self, meal, date):
        # We can't use slashes in links so we replace them
        date = date.replace('-', '/')

        return get_menu('cibus', meal, date)


class Tridente(Resource):
    def get(self, meal, date):
        # We can't use slashes in links so we replace them
        date = date.replace('-', '/')

        return get_menu('tridente', meal, date)


class CibusTridente(Resource):
    def get(self, meal, date):
        # We can't use slashes in links so we replace them
        date = date.replace('-', '/')

        return get_menu('cibustr', meal, date)


class Sogesta(Resource):
    def get(self, meal, date):
        # We can't use slashes in links so we replace them
        date = date.replace('-', '/')

        return get_menu('sogesta', meal, date)


# Routes configuration
api.add_resource(Duca, '/duca/<meal>/<date>')
api.add_resource(CibusDuca, '/cibusduca/<meal>/<date>')
api.add_resource(Tridente, '/tridente/<meal>/<date>')
api.add_resource(CibusTridente, '/cibustr/<meal>/<date>')
api.add_resource(Sogesta, '/sogesta/<meal>/<date>')


# Run this sh*t
if __name__ == '__main__':
    app.run(port=PORT)

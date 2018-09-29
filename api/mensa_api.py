from datetime import datetime

import requests
from bs4 import BeautifulSoup
from flask import Flask
from flask_restful import Resource, Api

# Init flask
app = Flask(__name__)
api = Api(app)

PORT = 9543

def get_menu(place, date, meal):
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
    def get(self, date, meal):
        # We can't use slashes in links so we replace them
        date = date.replace('-', '/')

        return get_menu('duca', date, meal)


class CibusDuca(Resource):
    def get(self, date):
        # We can't use slashes in links so we replace them
        date = date.replace('-', '/')

        return get_menu('cibus', date, 'lunch')


class Tridente(Resource):
    def get(self, date, meal):
        # We can't use slashes in links so we replace them
        date = date.replace('-', '/')

        return get_menu('tridente', date, meal)


class CibusTridente(Resource):
    def get(self, date, meal):
        # We can't use slashes in links so we replace them
        date = date.replace('-', '/')

        return get_menu('cibustr', date, 'lunch')


class Sogesta(Resource):
    def get(self, date, meal):
        # We can't use slashes in links so we replace them
        date = date.replace('-', '/')

        return get_menu('sogesta', date, meal)


# Routes configuration
api.add_resource(Duca, '/duca/<date>/<meal>')
api.add_resource(CibusDuca, '/cibusduca/<date>')
api.add_resource(Tridente, '/tridente/<date>/<meal>')
api.add_resource(CibusTridente, '/cibustr/<date>')
api.add_resource(Sogesta, '/sogesta/<date>/<meal>')


# Run this sh*t
if __name__ == '__main__':
    app.run(port=PORT)

from datetime import datetime

import requests
from bs4 import BeautifulSoup
from flask import Flask
from flask_restful import Resource, Api


def get_menu(place, date, meal):
    """
    Return the menu in JSON format
    """
    # Request the raw data
    r = requests.post("http://menu.ersurb.it/menum/menu.asp", data={
        'mensa': place,
        'da': date,
        'a': date
    })

    # Prepare structure for data
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
    prev = '0'
    dinner = False

    # Parse all food entries :P
    for link in soup.find_all('a')[1:]:
        # Clean out some HTML
        app = link.get('onclick').replace('showModal', '')

        # Get plate ID
        plate_id = app.split()[1]
        plate_id = plate_id.replace('"', '').replace(',', '')

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
            if prev == '40' and plate_id == '10':
                # Stop checking, next plate is from dinner block
                # At this point we are sure that the set is not empty
                data['not_empty'] = True
                break
            else:
                prev = plate_id

            # Put dish in right position
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
            # Check if we can start working
            if prev == '40' and plate_id == '10':
                # We are sure that the set is not empty
                data['not_empty'] = True

                dinner = True
            else:
                prev = plate_id

            if dinner:
                # Put dish in right position
                if plate_id == '10':
                    data['menu']['first'].append(name)
                elif plate_id == '20':
                    data['menu']['second'].append(name)
                elif plate_id == '30':
                    data['menu']['side'].append(name)
                elif plate_id == '40':
                    data['menu']['fruit'].append(name)

    # Return the JSON menu
    return data


class Duca(Resource):
    def get(self, date, meal):
        # Replace slashes with dashes
        date = date.replace('-', '/')

        return get_menu('duca', date, meal)


class CibusDuca(Resource):
    def get(self, date):
        # Replace slashes with dashes
        date = date.replace('-', '/')

        return get_menu('cibus', date, 'lunch')


class Tridente(Resource):
    def get(self, date, meal):
        # Replace slashes with dashes
        date = date.replace('-', '/')

        return get_menu('tridente', date, meal)


class CibusTridente(Resource):
    def get(self, date, meal):
        # Replace slashes with dashes
        date = date.replace('-', '/')

        return get_menu('cibustr', date, 'lunch')


class Sogesta(Resource):
    def get(self, date, meal):
        # Replace slashes with dashes
        date = date.replace('-', '/')

        return get_menu('sogesta', date, meal)


if __name__ == '__main__':
    # Init flask
    app = Flask(__name__)
    api = Api(app)

    # Config port
    PORT = 9543

    # Routes configuration
    api.add_resource(Duca, '/duca/<date>/<meal>')
    api.add_resource(Tridente, '/tridente/<date>/<meal>')

    # Disabled routes
    # api.add_resource(CibusDuca, '/cibusduca/<date>')
    # api.add_resource(CibusTridente, '/cibustr/<date>')
    # api.add_resource(Sogesta, '/sogesta/<date>/<meal>')

    # Start API
    app.run(host='0.0.0.0', port=PORT)

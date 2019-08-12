from datetime import datetime

import requests
from bs4 import BeautifulSoup
from flask import Flask
from flask_restful import Api, Resource

from logger import Logger


class Duca(Resource):
    def get(self, date, meal):
        logger.log_request('duca', meal)
        return get_menu('duca', date, meal)


class Tridente(Resource):
    def get(self, date, meal):
        logger.log_request('tridente', meal)
        return get_menu('tridente', date, meal)


class RequestStats(Resource):
    def get(self):
        logger.log_request('stats', '-')
        return logger.get_stats()
       

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
    data['not_empty'] = False
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
                data['not_empty'] = True
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
                data['not_empty'] = True
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

    # Return the JSON menu
    return data


if __name__ == '__main__':
    # Init database
    logger = Logger("mensa_requests.db")

    # Init flask
    app = Flask(__name__)
    api = Api(app)

    # Config port
    PORT = 9543

    # Routes configuration
    api.add_resource(Duca, '/duca/<date>/<meal>')
    api.add_resource(Tridente, '/tridente/<date>/<meal>')
    api.add_resource(RequestStats, '/stats/')

    # Start API
    app.run(host='0.0.0.0', port=PORT)

import os

from flask import Flask
from flask_restful import Api, Resource
from waitress import serve

from utils import Logger, get_menu


class Duca(Resource):
    def get(self, date, meal):
        logger.log_request("duca", meal)
        return get_menu("duca", date, meal)


class Tridente(Resource):
    def get(self, date, meal):
        logger.log_request("tridente", meal)
        return get_menu("tridente", date, meal)


class RIP(Resource):
    def get(self):
        logger.log_request("RIP", "-")
        return


class RequestStats(Resource):
    def get(self):
        return logger.get_stats()


if __name__ == "__main__":
    # Load env variables
    DEBUG = os.environ["DEBUG"]

    # Init flask
    app = Flask(__name__)
    api = Api(app)

    # Routes configuration
    api.add_resource(Duca, "/duca/<date>/<meal>")
    api.add_resource(Tridente, "/tridente/<date>/<meal>")
    api.add_resource(RequestStats, "/stats/")
    api.add_resource(RIP, "/rip")

    # Init database
    logger = Logger("mensa_requests.db")

    if DEBUG:
        print("Starting API (Debug mode)")
        app.run(host="0.0.0.0", port=9543)
    else:
        print("Starting API")
        serve(app, host="0.0.0.0", port=9543)

# Mensa Uniurb API #

Simple API written in Flask scrap data from the Erdis menu webpage.
Every request is logged to generate some statistic data.

## Usage ##

You can access all data using:
    `X.X.X.X:9543/<kitchen>/<date>/<moment>`

* `kitchen`: `duca` or `tridente`
* `date`: date in format MM-DD-YYYY
* `moment`: `lunch` or `dinner`

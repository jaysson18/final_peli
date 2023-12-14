from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from geopy import distance
import json
import random

import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    port=3306,
    database='flight_game',
    user='root',
    password='rico',
    autocommit=True

)





class Vihu:
    def __init__(self):
        self.sijainti = None
        self.visited_airports = set()


class Hyvis:
    def __init__(self):
        self.sijainti = None
        self.nimi = None


# get all goals

class Kentat:
    def __init__(self):
        self.all_airports = None
        self.määränpää = None
        self.lämpötila = 0


# oliot
pahis = Vihu()
hyvis = Hyvis()
kentät = Kentat()


# select 30 airports for the game
def get_airports():
    sql = "SELECT airport.iso_country, airport.ident, airport.name AS airport_name, airport.type, airport.latitude_deg, airport.longitude_deg, country.name AS country_name"
    sql += " FROM airport"
    sql += " JOIN country ON airport.iso_country = country.iso_country"
    sql += " WHERE airport.continent = 'EU'"
    sql += " AND airport.type = 'large_airport'"
    sql += " AND airport.iso_country != 'RU'"
    sql += " ORDER BY RAND()"
    sql += " LIMIT 30;"

    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def calculate_distance():
    return distance.distance((hyvis.sijainti['latitude_deg'], hyvis.sijainti['longitude_deg']),
                             (kentät.määränpää['latitude_deg'], kentät.määränpää['longitude_deg'])).km


app = Flask(__name__)
CORS(app)


@app.route('/start', methods=["POST"])
def start():
    vastaus = get_airports()
    kentät.all_airports = vastaus
    hyvis.sijainti = random.choice(vastaus)
    pahis.sijainti = random.choice(vastaus)
    kentät.lämpötila = 0

    response = {
        "lentokentat": kentät.all_airports,
        "pahis_sijainti": pahis.sijainti,
        "hyvis_sijainti": hyvis.sijainti
    }

    jsonify(response)
    return response


@app.route('/directionalhint', methods=['GET'])
def directionalhint():
    herolat = hyvis.sijainti['latitude_deg']
    herolong = hyvis.sijainti['longitude_deg']
    lat_diff = pahis.sijainti['latitude_deg'] - herolat
    lon_diff = pahis.sijainti['longitude_deg'] - herolong

    if lat_diff > 0 and lon_diff > 0:
        vastaus = "The villain is to the North-East of you."
        response = jsonify(vastaus)
        return response
    elif lat_diff < 0 and lon_diff > 0:
        vastaus = "The villain is to the South-East of you."
        response = jsonify(vastaus)
        return response
    elif lat_diff > 0 and lon_diff < 0:
        vastaus = "The villain is to the North-West of you."
        response = jsonify(vastaus)
        return response
    elif lat_diff < 0 and lon_diff < 0:
        vastaus = "The villain is to the South-West of you."
        response = jsonify(vastaus)
        return response
    else:
        vastaus = "You're very close to the villain!"
        response = jsonify(vastaus)
        return response


@app.route('/flyTo/<ident>')
def flyTo(ident):
    sql = "SELECT airport.iso_country, airport.ident, airport.name AS airport_name, airport.type, airport.latitude_deg, airport.longitude_deg, country.name AS country_name"
    sql += " FROM airport"
    sql += " JOIN country ON airport.iso_country = country.iso_country"
    sql += " WHERE airport.continent = 'EU'"
    sql += " AND airport.type = 'large_airport'"
    sql += " AND airport.ident = %s"  # Käytä paikkamerkkiä

    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (ident,))  # Välitä ident turvallisesti
    result = cursor.fetchall()
    kentät.määränpää = result[0]

    kuljettumatka = calculate_distance()  # lasketaan matka kahden pisteen välillä

    temperature_change = 0.05 * (kuljettumatka // 100)
    kentät.lämpötila += temperature_change

    hyvis.sijainti = result[0] if result else hyvis.sijainti  # sijainti päivitetään vasta matkan laskemisen jälkeen
    return jsonify({'kuljettumatka': kuljettumatka, 'uusi_lämpötila': kentät.lämpötila})

@app.route('/updateTemperature/<int:temperatureChange>')
def updateTemperature(temperatureChange):
    kentät.lämpötila += temperatureChange
    print(kentät.lämpötila)



@app.route('/isGameOver')
def isGameOver():
    game_over = False
    condition = None

    if hyvis.sijainti == pahis.sijainti:
        response = {
            "game": "over",
            "condition": "win-catched"
        }
        jsonify(response)
        return response

    elif kentät.lämpötila == 6:
        response = {
            "game": "over",
            "condition": "lost-temp"
        }
        jsonify(response)
        return response

    response = {
        "game": "over" if game_over else "ongoing",
        "condition": condition
    }
    jsonify(response)
    return response


@app.route('/update_data')
def update_data():
    response = {
        "lentokentat": kentät.all_airports,
        "pahis_sijainti": pahis.sijainti,
        "hyvis_sijainti": hyvis.sijainti
    }

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)


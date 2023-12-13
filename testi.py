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
v_visited_airports = set()
villain_location = None

def villain_moves_rounds(player_airports):
    global villain_location, v_visited_airports

    if not player_airports:
        print("No airports found in the database.")
        return

    # Step 2: Randomly select an initial airport for the villain
    villain_location = random.choice(player_airports)
    v_visited_airports.add(villain_location['ident'])
    print(f"Villain is on the run")
    return villain_location




from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from geopy import distance
import json
import random


import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    port=3306,
    database="flight_game",
    user='root',
    password='rico',
    autocommit=True


)

vastaus = get_airports()
pahis_sijainti = villain_moves_rounds(vastaus)

print(pahis_sijainti)
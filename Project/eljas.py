import config
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from geopy import distance
import json
import random


import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    port=3306,
    database='c_peli',
    user='root',
    password='exel80jajop',
    autocommit=True


)
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


# Global variable for climate temperature
climate_temperature = 0
class Game:

    def __init__(self, conn, cur_airport, p_name):
        self.game_over = False
        self.win = False
        self.all_airports = self.get_airports()
        self.villain_visited_airports = set()
        self.villain_location = None
        self.climate_temperature = 0
        self.g_id = 0
        self.conn = conn
        self.cur_airport = cur_airport
        self.p_name = p_name

        sql = "INSERT INTO game (location, screen_name) VALUES (%s, %s);"
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, (cur_airport, p_name))
        self.g_id = cursor.lastrowid


        self.villain_moves_rounds(self.all_airports)
        # start_airport ident
        current_airport = self.all_airports[0]['ident']

        # game id
        game_id = self.create_game(self.current_airport, p_name, self.all_airports)

    def get_airports(self):
        sql = """
        SELECT airport.iso_country, airport.ident, airport.name AS airport_name, airport.type, airport.latitude_deg, airport.longitude_deg, country.name AS country_name
        FROM airport
        JOIN country ON airport.iso_country = country.iso_country
        WHERE airport.continent = 'EU' 
        AND airport.type = 'large_airport'
        AND airport.iso_country != 'RU'
        ORDER BY RAND()
        LIMIT 30;
        """

        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    def get_airport_info(self, icao):
        sql = f'''SELECT airport.iso_country, ident, airport.name AS airport_name, type, latitude_deg, longitude_deg, country.name AS country_name
        FROM airport
        JOIN country ON airport.iso_country = country.iso_country
        WHERE ident = %s'''
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(sql, (icao,))
        result = cursor.fetchone()
        if 'airport_name' not in result or 'country_name' not in result:
            raise KeyError("Missing keys 'airport_name' and/or 'country_name' in the database result.")

        return result

    def calculate_distance(self, current, target):
        start = self.get_airport_info(current)
        end = self.get_airport_info(target)
        return distance.distance((start['latitude_deg'], start['longitude_deg']),
                                 (end['latitude_deg'], end['longitude_deg'])).km

    # get airports in range
    def airports_in_range(self, icao, a_ports):
        airports_with_country = []
        for airport in a_ports:
            airport_info = self.get_airport_info(airport['ident'])
            airports_with_country.append({
                'ident': airport['ident'],
                'name': airport['airport_name'],
                'distance': self.calculate_distance(icao, airport['ident']),
                'country': airport_info['country_name']
            })
        return airports_with_country

    def villain_moves_rounds(self, player_airports):

        if not player_airports:
            print("No airports found in the database.")
            return

        # Step 2: Randomly select an initial airport for the villain
        self.villain_location = random.choice(player_airports)
        self.villain_visited_airports.add(self.villain_location['ident'])
        print(f"Villain is on the run")

    def villain_movement(self):

        # Calculate distances from the villain's current location to all airports
        distances = []
        for airport in self.all_airports:
            if airport['ident'] != self.villain_location['ident'] and airport['ident'] not in self.villain_visited_airports:
                etäisyys = self.calculate_distance(self.villain_location['ident'], airport['ident'])
                distances.append((airport, etäisyys))

        # Sort the airports by distance (in ascending order)
        distances.sort(key=lambda x: x[1])

        # Select the three closest unvisited airports (excluding the current one)
        closest_unvisited_airports = [airport for airport in distances if
                                      airport[0]['ident'] not in self.villain_visited_airports][:3]

        if closest_unvisited_airports:
            # Choose one of the closest unvisited airports randomly
            chosen_airport = random.choice(closest_unvisited_airports)[0]

            # Update the villain's location to the chosen airport
            if chosen_airport != self.current_airport:
                villain_location = chosen_airport

                # Mark the chosen airport as visited
                self.villain_visited_airports.add(self.villain_location['ident'])

            # print("Villain is now in", villain_location)
        else:
            print("The villain has visited all available airports.")

    #def generate_directional_hints(self, player_airport, villain_airport):
     #   lat_diff = self.villain_airport['latitude_deg'] - self.player_airport['latitude_deg']
      #  lon_diff = self.villain_airport['longitude_deg'] - self.player_airport['longitude_deg']

       # if lat_diff > 0 and lon_diff > 0:
        #    return "The villain is to the North-East of you."
        #elif lat_diff < 0 and lon_diff > 0:
         #   return "The villain is to the South-East of you."
        #elif lat_diff > 0 and lon_diff < 0:
         #   return "The villain is to the North-West of you."
        #elif lat_diff < 0 and lon_diff < 0:
         #   return "The villain is to the South-West of you."
        #else:
         #   return "You're very close to the villain!"


# tick
    def update_game(self):
        # get current airport info
        airport = self.get_airport_info(self.current_airport)
        # show game status
        print(f'''You are at {airport['airport_name']}.''')
        print('You have unlimited range.')
        print(f"Climate temperature is now +{self.climate_temperature}C.")
        # pause
        input('\033[32mPress Enter to continue...\033[0m')

        hint = self.generate_directional_hints(self.get_airport_info(self.current_airport), self.villain_location)
        print(f"Hint: {hint}")

        # show airports in range. if none, game over
        airports = self.airports_in_range(self.current_airport, self.all_airports)
        airports.sort(key=lambda airport: self.calculate_distance(self.current_airport, airport['ident']))
        print(f'''\033[34mThere are {len(airports)} airports in range: \033[0m''')
        if len(airports) == 0:
            print('You are out of range.')
            game_over = True
        else:
            print(f'''Airports: ''')
            for i, airport in enumerate(airports, start=1):
                ap_distance = self.calculate_distance(self.current_airport, airport['ident'])
                print(f'''{i}. {airport['name']}, Country: {airport['country']},  distance: {ap_distance:.0f}km''')

            print(f"Climate temperature is now +{self.climate_temperature}")
            print(f"Hint: {hint}")
            dest = int(input('Enter the number of the airport you want to fly to: '))
            if dest >= 1 and dest <= len(airports):
                selected_distance = airports[dest - 1]
                dest = selected_distance['ident']
                selected_distance = self.calculate_distance(self.current_airport, dest)
                current_airport = dest

            # Update the climate temperature for every 100km flown
            while selected_distance >= 100:
                self.climate_temperature += 0.05
                selected_distance -= 100

                # Check if the climate temperature has reached a critical point
                if self.climate_temperature >= 6:
                    print(f"Climate temperature is now +{self.climate_temperature:.2f}C!")
                    print("The world has exploded, and you are doomed!")
                    self.game_over = True
                    break

            # check if the player's current airport matches the villain's location
            if self.current_airport == self.villain_location['ident']:
                print("You found the villain!")
                self.win = True
                self.game_over = True
            else:
                self.villain_movement()

            # check if the villain has reached a certain location
# get all goals


# FUNCTIONS

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


app = Flask(__name__)
CORS(app)

@app.route('/start', methods= ["POST"])
def start():
    vastaus = get_airports()
    pahis_sijainti = villain_moves_rounds(vastaus)
    response = {
        "lentokentat": vastaus,
        "pahis_sijainti": pahis_sijainti
    }
    jsonify(response)
    return response


@app.route('/dircetionalhint/<herolat>/<herolong>', methods = ['GET'])
def directionalhint(herolat, herolong, villlat, villlong):
    lat_diff = villlat - herolat
    lon_diff = villlong - herolong

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



if __name__ == '__main__':
    app.run(debug=True)


# create new game
"""def create_game(cur_airport, p_name, a_ports):
    sql = "INSERT INTO game (location, screen_name) VALUES (%s, %s);"
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (cur_airport, p_name))
    g_id = cursor.lastrowid

    # add goals

    return g_id


# get airport info
def get_airport_info(icao):
    sql = f'''SELECT airport.iso_country, ident, airport.name AS airport_name, type, latitude_deg, longitude_deg, country.name AS country_name
FROM airport
JOIN country ON airport.iso_country = country.iso_country
WHERE ident = %s'''
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, (icao,))
    result = cursor.fetchone()
    if 'airport_name' not in result or 'country_name' not in result:
        raise KeyError("Missing keys 'airport_name' and/or 'country_name' in the database result.")

    return result


# check if airport has a goal

# calculate distance between two airports
def calculate_distance(current, target):
    start = get_airport_info(current)
    end = get_airport_info(target)
    return distance.distance((start['latitude_deg'], start['longitude_deg']),
                             (end['latitude_deg'], end['longitude_deg'])).km


# get airports in range
def airports_in_range(icao, a_ports):
    airports_with_country = []
    for airport in a_ports:
        airport_info = get_airport_info(airport['ident'])
        airports_with_country.append({
            'ident': airport['ident'],
            'name': airport['airport_name'],
            'distance': calculate_distance(icao, airport['ident']),
            'country': airport_info['country_name']
        })
    return airports_with_country


# villain of the game

villain_location = None
all_airports = get_airports()
v_visited_airports = set()


def villain_moves_rounds(player_airports):
    global villain_location, v_visited_airports

    if not player_airports:
        print("No airports found in the database.")
        return

    # Step 2: Randomly select an initial airport for the villain
    initial_airport = random.choice(player_airports)
    villain_location = initial_airport
    v_visited_airports.add(villain_location['ident'])
    print(f"Villain is on the run")


def villain_movement():
    global villain_location

    # Calculate distances from the villain's current location to all airports
    etäisyydet = []
    for airport in all_airports:
        if airport['ident'] != villain_location['ident'] and airport['ident'] not in v_visited_airports:
            etäisyys = calculate_distance(villain_location['ident'], airport['ident'])
            etäisyydet.append((airport, etäisyys))

    etäisyydet.sort(key=lambda x: x[1])

    # Select the three closest unvisited airports (excluding the current one)
    closest_unvisited_airports = [airport for airport in etäisyydet if airport[0]['ident'] not in v_visited_airports][
                                 :3]

    if closest_unvisited_airports:
        # Choose one of the closest unvisited airports randomly
        chosen_airport = random.choice(closest_unvisited_airports)[0]

        # Update the villain's location to the chosen airport
        if chosen_airport != current_airport:
            villain_location = chosen_airport

            # Mark the chosen airport as visited
            v_visited_airports.add(villain_location['ident'])


    else:
        print("The villain has visited all available airports.")


def generate_directional_hints(player_airport, villain_airport):
    lat_diff = villain_airport['latitude_deg'] - player_airport['latitude_deg']
    lon_diff = villain_airport['longitude_deg'] - player_airport['longitude_deg']

    if lat_diff > 0 and lon_diff > 0:
        return "The villain is to the North-East of you."
    elif lat_diff < 0 and lon_diff > 0:
        return "The villain is to the South-East of you."
    elif lat_diff > 0 and lon_diff < 0:
        return "The villain is to the North-West of you."
    elif lat_diff < 0 and lon_diff < 0:
        return "The villain is to the South-West of you."
    else:
        return "You're very close to the villain!"


# game starts
# ask to show the story
storyDialog = input('Do you want to read the background story? (Y/N): ')
if storyDialog == 'Y' or storyDialog == "y":
    # print wrapped string line by line
    for line in story.getStory():
        print(line)

# GAME SETTINGS
print('When you are ready to start, ')
player = input('Type your player name: ')
# boolean for game over and win
game_over = False
win = False

# all airports
all_airports = get_airports()
villain_moves_rounds(all_airports)
# start_airport ident
start_airport = all_airports[0]['ident']

# current airport
current_airport = start_airport

# game id
game_id = create_game(current_airport, player, all_airports)

# GAME LOOP
while not game_over:
    # get current airport info
    airport = get_airport_info(current_airport)
    # show game status
    print(f'''You are at {airport['airport_name']}.''')
    print('You have unlimited range.')
    print(f"Climate temperature is now +{climate_temperature}C.")
    # pause
    input('\033[32mPress Enter to continue...\033[0m')

    hint = generate_directional_hints(get_airport_info(current_airport), villain_location)
    print(f"Hint: {hint}")

    # show airports in range. if none, game over
    airports = airports_in_range(current_airport, all_airports)
    airports.sort(key=lambda airport: calculate_distance(current_airport, airport['ident']))
    print(f'''\033[34mThere are {len(airports)} airports in range: \033[0m''')
    if len(airports) == 0:
        print('You are out of range.')
        game_over = True
    else:
        print(f'''Airports: ''')
        for i, airport in enumerate(airports, start=1):
            ap_distance = calculate_distance(current_airport, airport['ident'])
            print(f'''{i}. {airport['name']}, Country: {airport['country']},  distance: {ap_distance:.0f}km''')

        print(f"Climate temperature is now +{climate_temperature}")
        print(f"Hint: {hint}")
        dest = int(input('Enter the number of the airport you want to fly to: '))
        if dest >= 1 and dest <= len(airports):
            selected_distance = airports[dest - 1]
            dest = selected_distance['ident']
            selected_distance = calculate_distance(current_airport, dest)
            current_airport = dest

        # Update the climate temperature for every 100km flown
        while selected_distance >= 100:
            climate_temperature += 0.05
            selected_distance -= 100

            # Check if the climate temperature has reached a critical point
            if climate_temperature >= 6:
                print(f"Climate temperature is now +{climate_temperature:.2f}C!")
                print("The world has exploded, and you are doomed!")
                game_over = True
                break

        # check if the player's current airport matches the villain's location
        if current_airport == villain_location['ident']:
            print("You found the villain!")
            win = True
            game_over = True
        else:
            villain_movement()

        # check if the villain has reached a certain location

# show game result
print(
    f'''{f'Good job {player}! You chased down the BBC. Climate temperature rose +{climate_temperature:.2f}C, but thanks to you reclaming the climate stabilizer and turning it back on everything is back to normal. Great job!' if win else f'You lost! Better luck next time {player}. The villain location is:  {villain_location["airport_name"]} :('}''')

"""

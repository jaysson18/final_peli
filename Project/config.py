import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    port=3306,
    database='flight_game',
    user='root',
    password='rico',
    autocommit=True
)
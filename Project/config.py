import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    port=3306,
    database='c_peli',
    user='root',
    password='exel80jajop',
    autocommit=True
)

#Importando Libreria mysql.connector para conectar Python con MySQL
import mysql.connector

class Database():
    def __init__(self):
        self.connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='proveedores'
    )
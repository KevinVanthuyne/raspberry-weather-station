import sqlite3

class Database:
    """ Database for storing all weather readings """

    def __init__(self, db_file):
        self.db_file = db_file

    def create_connection(self):
        """ Create a connection to the database
            Preferably open and close a connection for every query,
            not keep the connection open the entire class lifetime """
        try:
            connection = sqlite3.connect(self.db_file)
            return connection
        except Error as e:
            print(e)

        return None

    def add_reading(self, reading):
        connection = self.create_connection()

        query =  '''INSERT INTO reading (date, time, weather_time, outside_temp, inside_temp, inside_humid)
                    VALUES (?, ?, ?, ?, ?, ?);'''
        cursor = connection.cursor()
        cursor.execute(query, reading)

        connection.close()

    def get_all_readings(self):
        connection = self.create_connection()
        cursor = connection.cursor()

        for row in cursor.execute('SELECT * from reading'):
            print(row)

        connection.close()

# DEBUG
if __name__ == '__main__':
    db = Database('weatherdata.db')
    db.get_all_readings()

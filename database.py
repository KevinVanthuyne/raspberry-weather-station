import sqlite3

class Database:
    """ Class to interact with SQLite database for storing all weather readings.
        Database needs to contain a table 'reading' """

    def __init__(self, db_file):
        self.db_file = db_file  # name of the database file

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
        with self.create_connection() as conn:
            query =  '''INSERT INTO reading (date, time, weather_time, outside_temp, inside_temp, inside_humid)
                        VALUES (?, ?, ?, ?, ?, ?);'''
            cursor = conn.cursor()
            cursor.execute(query, reading)

            print("Reading {} added to database".format(cursor.lastrowid))

    def get_all_readings(self):
        with self.create_connection() as conn:
            cursor = conn.cursor()

            for row in cursor.execute('SELECT * from reading'):
                print(row)

    def create_table(self):
        """ Creates a 'reading' table in the database according to
            the necessary input """
        # TODO
        pass

# DEBUG
if __name__ == '__main__':
    db = Database('weatherdata.db')
    db.get_all_readings()

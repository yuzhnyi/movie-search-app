print("DBMC loaded successfully")
import mysql.connector
from datetime import datetime

class DBManager:
    # Initialize DBManager with configuration
    def __init__(self, config):
        self.config = config

    # Connect to the database
    def connect(self):
        try:
            connection = mysql.connector.connect(**self.config)
            if connection.is_connected():
                print(f"Connected to database: {self.config['database']}")
            return connection
        except mysql.connector.Error as err:
            print(f"Error connecting to database: {err}")
            return None

    # Execute SELECT queries
    def execute_query(self, query, params=None):
        connection = self.connect()
        if connection is None:
            return None
        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            connection.commit()
            return results
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
            return None
        finally:
            cursor.close()
            connection.close()

    # Execute non-SELECT queries (INSERT, UPDATE, DELETE)
    def execute_non_select_query(self, query, params=None):
        connection = self.connect()
        if connection is None:
            return
        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
        finally:
            cursor.close()
            connection.close()

# EXAMPLE CONFIGURATIONS — replace with your own credentials
film_db_config = {
    'host': 'your_film_db_host',
    'user': 'your_film_db_user',
    'password': 'your_password',
    'database': 'sakila'
}

user_db_config = {
    'host': 'your_user_db_host',
    'user': 'your_user_db_user',
    'password': 'your_password',
    'database': 'your_user_database'
}

film_db_manager = DBManager(film_db_config)
user_db_manager = DBManager(user_db_config)

if __name__ == '__main__':
    print("Testing database connection...")
    try:
        connection = film_db_manager.connect()
        if connection:
            print("Connected to film database successfully!")
            connection.close()
        else:
            print("Failed to connect to film database.")
        
        user_connection = user_db_manager.connect()
        if user_connection:
            print("Connected to user database successfully!")
            user_connection.close()
        else:
            print("Failed to connect to user database.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        input("Press Enter to exit...")

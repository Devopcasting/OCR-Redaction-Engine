"""
EstablishDBConnection: A class to easblish a connection to MongoDB.

Methods:
--------
establish_connection():
    Attempts to connect to the MongoDB database and logs the connection status.

Example Usage:
--------------
db_connection = EstablishDBConnection()
client = db_connection.establish_connection()
if client:
    # Proceed with your database operations
else:
    print("Failed to connect to the database.")
"""

import pymongo
from pymongo.errors import ConnectionFailure
from ocrr_logger.ocrrlogger import OCRRLogger

class EstablishDBConnection:
    def __init__(self):
        """
        Initializes the EstablishDBConnection class by setting up the logger and the MongoDB connection string.
        """
        # Set up the logger using the OCRRLogger configuration
        # Instantiate the OCRRLogger class
        logger_config = OCRRLogger()

        # Get the configured logger instance
        self.logger = logger_config.configure_logger() 

        # MongoDB connection string
        self.connection_string = "mongodb://localhost:27017"

    def establish_connection(self):
        """
        Establishes a connection to the MongoDB database.

        Returns:
        --------
        pymongo.MongoClient or None
            Returns a MongoClient instance if the connection is successful, otherwise returns None.
        """
        try:
            # Attempt to create a MongoClient instance and ping the database to ensure connection is established
            client = pymongo.MongoClient(self.connection_string)

            # Ping the MongoDB server to verify the connection
            client.admin.command('ping')

            self.logger.info("| Successfully connected to MongoDB")
            return client
        except ConnectionFailure as e:
            # Log an error message if connection to MongoDB fails due to a connection failure
            self.logger.error(f"| Failed to connect to MongoDB: {e}")
            return None
        except Exception as e:
            # Log an error message if an unexpected exception occurs
            self.logger.error(f"| Failed to connect to MongoDB: {e}")
            return None
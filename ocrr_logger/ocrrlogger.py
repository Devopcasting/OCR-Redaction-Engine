"""
OCRRLogger: A class to configure logging for the OCRR Engine application.

This class handles the creation and configuration of a logger that writes logs to a specified file.
It reads the log file path from a configuration file and ensures the log directory exists before creating
a file handler. The class also includes methods to check for existing file handlers to prevent duplicate
logging entries. Exception handling is implemented to manage potential errors in file and configuration operations.

Key functionalities:
- Initialize logger with specified log file name and log level.
- Configure logger with a file handler and formatter.
- Read log path from a configuration file.
- Check for existing file handlers and create the log file if it does not exist.

Example usage:
    logger_config = OCRRLogger()
    logger = logger_config.configure_logger()
    logger.info("This is a log message.")
"""

import logging
import configparser
import os

class OCRRLogger:
    def __init__(self, log_file='ocrr.log', log_level=logging.INFO) -> None:
        """
        Initialize the OCRRLogger instance.
        
        :param log_file: Name of the log file (default: 'ocrr.log').
        :param log_level: Logging level (default: logging.INFO).
        """
        # Construct the full path to the log file
        self.log_file = os.path.join(self._get_log_path(), log_file)
        self.log_level = log_level

    def configure_logger(self) -> logging.Logger:
        """ 
        Configure and return a logger instance with a file handler.
        :return: Configured logger.
        """
        # Create a logger with a specific name
        logger = logging.getLogger('OCRR')
        logger.setLevel(self.log_level)

        # Check if the logger already has a file handler for the specified log file
        if not self._file_handler_exits(logger):
            try:
                # Ensure the log directory exists
                os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

                # Create a file handler for logging
                file_handler = logging.FileHandler(self.log_file)
                file_handler.setLevel(self.log_level)

                # Define a logginf format
                formatter = logging.Formatter('%(process)d %(asctime)s %(levelname)s %(message)s')
                file_handler.setFormatter(formatter)

                # Add the file handler to the logger
                logger.addHandler(file_handler)
            except Exception as e:
                # Log any exceptions during file handler creation
                logger.error(f"| Failed to create file handler: {e}")

        return logger

    def _get_log_path(self) -> str:
        """
        Retrieve the log path from a configuration file.
        
        :return: Log path specified in the configuration file or current working directory.
        """
        config = configparser.ConfigParser(allow_no_value=True)
        try:
            # Read configuration file
            config.read(r'C:\Program Files\OCRR\settings\configuration.ini')

            # Return the log path if specified in the configuration file
            if 'Logging' in config and 'path' in config['Logging']:
                return config['Logging']['path']
            else:
                return os.getcwd()
        except Exception as e:
            # Print an error message if configuration reading fails
            print(f"Error reading configuration file: {e}")
            return os.getcwd()
    
    def _file_handler_exits(self, logger) -> bool:
        """
        Check if a file handler for the specified log file already exists in the logger.
        
        :param logger: Logger instance.
        :return: True if a file handler exists, False otherwise.
        """
        if not os.path.isfile(self.log_file):
            try:
                # Create the log file if it does not exist
                open(self.log_file, 'w').close()
            except Exception as e:
                # Log any exceptions during file creation
                logger.error(f"| Failed to create log file: {e}")
            return False
        
        # Check if any of the existing handler in the logger is for the log file
        return any(isinstance(handler, logging.FileHandler) and handler.baseFilename == self.log_file for handler in logger.handlers)

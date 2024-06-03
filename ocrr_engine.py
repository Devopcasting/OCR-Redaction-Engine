import sys
import configparser
import queue
from concurrent.futures import ThreadPoolExecutor
from ocrr_logger.ocrrlogger import OCRRLogger
from database.connection import EstablishDBConnection
from in_progress.process_in_progress_status import ProcessInProgressStatusDocuments
from process_documents.process_queue_documents import ProcessQueueDocuments

class OCRREngine:
    def __init__(self):
        # Read configuration settings from configuration.ini file
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(r'C:\Program Files\OCRR\settings\configuration.ini')

        # Retrieve paths for document upload and OCR workspace from configuration
        self.document_upload_path = config['Paths']['upload']
        self.ocrr_workspace_path = config['Paths']['workspace']

        # Configure logger
        logger_config = OCRRLogger()
        self.logger = logger_config.configure_logger()

        # Initialize database connection
        self._initialize_db_connection()
        
        # Initialize queue for 'IN_PROGRESS' documents
        self.in_progress_queue = queue.Queue()
        self.logger.info(f"| Queue initialized for 'IN_PROGRESS' documents.")

    def _initialize_db_connection(self):
        try:
            # Establish connection to MongoDB
            db_client = EstablishDBConnection().establish_connection()

            if db_client is not None:
                # Check if 'ocrrworkspace' database exists
                db_name_list = db_client.list_database_names()
                if 'ocrrworkspace' in db_name_list:
                    # Check if 'ocrr' collection exists in 'ocrrworkspace' database. If it exists, clean all the documents in ocrr collection.
                    db_collection_list = db_client['ocrrworkspace'].list_collection_names()
                    if 'ocrr' in db_collection_list:
                        db_client['ocrrworkspace']['ocrr'].delete_many({})
                        self.logger.info(f"| Cleaned all documents in 'ocrr' collection.")
                else:
                    # If it doesn't exist, create 'ocrrworkspace' database with collection 'ocrr'
                    db_client['ocrrworkspace'].create_collection('ocrr')
                    self.logger.info(f"| Created new 'ocrrworkspace' database with collection 'ocrr'.")

                # Update the status of documents from 'IN_QUEUE' to 'IN_PROGRESS' in the 'fileDetails' collection
                db_client['upload']['fileDetails'].update_many({'status': 'IN_QUEUE'}, {'$set': {'status': 'IN_PROGRESS'}})
                self.logger.info(f"| Updated document status from 'IN_QUEUE' to 'IN_PROGRESS'.")
                # Close the DB connection
                db_client.close()
            else:
                self.logger.error(f"| Failed to connect to MongoDB.")
                sys.exit(1)
        except Exception as e:
            # Log error if database initialization fails
            self.logger.error(f"| Failed to initialize MongoDB: {e}")
            sys.exit(1)

    def query_in_progress_status_documents(self):
        filter_in_progress_status_doc = ProcessInProgressStatusDocuments(self.document_upload_path, self.ocrr_workspace_path, self.in_progress_queue, self.logger)
        filter_in_progress_status_doc.query_in_progress_status_documents()
    
    def process_queue_documents(self):
        process_queue_doc = ProcessQueueDocuments(self.in_progress_queue, self.document_upload_path, self.ocrr_workspace_path, self.logger)
        process_queue_doc.process_queue_document()

def main():
    try:
        engine = OCRREngine()
        engine.logger.info(f"| OCR engine initialized successfully.")
        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(engine.query_in_progress_status_documents)
            executor.submit(engine.process_queue_documents)
    except Exception as e:
        engine.logger.error(f"| Failed to initialize OCR engine: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
"""
    ProcessInProgressStatusDocuments class to process documents with 'IN_PROGRESS' status, validate them, 
    move them to a queue for further processing, update their status in 
    the database, and trigger webhooks as necessary.

    Attributes:
        doc_upload_path (str): The base path where documents are uploaded.
        doc_in_progress_status_queue (object): Queue to hold documents in 'IN_PROGRESS' status.
        logger (object): Logger for logging messages and errors.

    Example Usage:
        logger = setup_logger()
        queue = Queue()
        processor = ProcessInProgressStatusDocuments('/path/to/uploads', queue, logger)
        processor.query_in_progress_status_documents()
"""

import sys
import os
from time import sleep
from database.connection import EstablishDBConnection
from webhook.post_trigger import WebhookPostTrigger

class ProcessInProgressStatusDocuments:
    def __init__(self, doc_upload_path: str, ocrr_workspace_path: str, doc_in_progress_status_queue: object, logger: object) -> None:
        self.doc_upload_path = doc_upload_path
        self.ocrr_workspace_path = ocrr_workspace_path
        self.doc_in_progress_status_queue = doc_in_progress_status_queue
        self.logger = logger
        
        self.db_client = None
        self.collection_filedetails = None
        self.collection_ocrr = None
        self.collection_webhooks = None


    def _initialize_db_connection(self):
        try:
            # Establish connection to MongoDB
            self.db_client = EstablishDBConnection().establish_connection()

            if self.db_client is not None:
                self.collection_filedetails = self.db_client['upload']['fileDetails']
                self.collection_webhooks = self.db_client['upload']['webhooks']
                self.collection_ocrr = self.db_client['ocrrworkspace']['ocrr']
            else:
                self.logger.error(f"| Failed to connect to MongoDB.")
                sys.exit(1)
        except Exception as e:
            self.logger.error(f"| Failed to initialize MongoDB while Processing 'IN_PROGRESS' status documents: {e}")
            sys.exit(1)

    def query_in_progress_status_documents(self):
        try:
            # Initialize database connection
            self._initialize_db_connection()
            while True:
                documents = self.collection_filedetails.find({'status': 'IN_PROGRESS'})
                for document in documents:
                    document_path = f"{self.doc_upload_path}{'\\'.join(document['uploadDir'].split('/'))}"
                    # Check if document path exists and document extension is valid
                    if self._check_document_path(document_path) and self._check_document_extension(document['fileExtension'].lower()):
                        self._insert_in_progress_status_document_to_queue(document)
                    else:
                        self._update_status_to_invalid_document(document['taskId'], document['uploadDir'])
                        self._webhook_post_request(document['taskid'])
                sleep(5)      
        except Exception as e:
            self.logger.error(f"| Failed to initialize database connection while Processing 'IN_PROGRESS' status documents: {e}")
            sys.exit(1)
    
    def _check_document_path(self, document_path: str) -> bool:
        # Check if document path exists
        if os.path.exists(document_path):
            return True
        else:
            return False
    
    def _check_document_extension(self, document_extension: str) -> bool:
        # Check if document extension is valid
        if document_extension in ['jpg', 'jpeg', 'tiff']:
            return True
        else:
            return False
    
    def _insert_in_progress_status_document_to_queue(self, document: dict):
        # Insert a valid document to the 'IN_PROGRESS' queue and update its status in the database
        try:
            document_info = {
                "taskId": document['taskId'],
                "path": f"{self.doc_upload_path}{'\\'.join(document['uploadDir'].split('/'))}",
                "status": document['status'],
                "clientId": document['clientId'],
                "taskResult": "",
                "uploadDir": document['uploadDir'],
                "renamedDoc": self._rename_document(document['uploadDir']),
                "document_name": list(filter(None, document['uploadDir'].split("/")))[-1],
                "roomName": list(filter(None, document['uploadDir'].split("/")))[0],
                "roomId": list(filter(None, document['uploadDir'].split("/")))[1],
                "redactedPath": os.path.join(f"{self.doc_upload_path}\{list(filter(None, document['uploadDir'].split("/")))[0]}\{list(filter(None, document['uploadDir'].split("/")))[1]}", "Redacted"),
                "ocrrworkspace_doc_path": os.path.join(self.ocrr_workspace_path, self._rename_document(document['uploadDir']))
            }
            self.collection_ocrr.insert_one(document_info)
            self.doc_in_progress_status_queue.put(document_info)
            self.collection_filedetails.update_one({"taskId": document['taskId']}, {"$set": {"status": "IN_QUEUE"}})
            self.logger.info(f"| Added document to 'IN_PROGRESS' queue: {document['fileName']}")
            return True
        except Exception as e:
            self.logger.error(f"| Failed to insert document to 'IN_PROGRESS' queue: {e}")
            return False
    
    def _rename_document(self, upload_dir: str) -> str:
        # Split the upload directory
        split_upload_dir = list(filter(None, upload_dir.split('/')))
        room_name = split_upload_dir[0]
        room_id = split_upload_dir[1]
        document_name = split_upload_dir[2]
        seprator = "+"
        return f"{room_name}{seprator}{room_id}{seprator}{document_name}"

    def _update_status_to_invalid_document(self, taskid: str, filepath: str):
        # Update the status of the document to 'INVALID_DOCUMENT' in the database if invalid
        try:
            update_query = {"$set": {"status": "INVALID_DOCUMENT", "taskResult": "Invalid Document"}}
            self.collection_filedetails.update_one({"taskId": taskid}, update_query)
            self.logger.info(f"| Updated status to 'INVALID_DOCUMENT' for document: {filepath}")
        except Exception as e:
            self.logger.error(f"| Failed to update status to 'INVALID_DOCUMENT' for document: {filepath}: {e}")
            sys.exit(1)
    
    def _webhook_post_request(self, taskid: str):
        # Send a webhook request for the task with the specified task ID
        try:
            # Prepare the payload data for the webhook request
            webhook_data = self.collection_filedetails.find_one({"taskId": taskid})
            if webhook_data is not None:
                payload = {
                    "taskId": taskid,
                    "status": webhook_data['status'],
                    "taskResult": webhook_data['taskResult'],
                    "clientId": webhook_data['clientId'],
                    "uploadDir": webhook_data['uploadDir']
                }
                # Get the URL from collection webhooks
                webhook_url = self.collection_webhooks.find_one({"clientId": webhook_data['clientId']})
                if webhook_url is not None:
                    webhook_url = webhook_url['url']
                    # Send the webhook request
                    if WebhookPostTrigger(webhook_url, payload).send_post():
                        self.logger.info(f"| Webhook request sent successfully for task: {taskid}")
                    else:
                        self.logger.error(f"| Failed to send webhook request for task: {taskid}")
                        sys.exit(1)
        except Exception as e:
            self.logger.error(f"| Failed to send webhook request for task: {taskid}: {e}")
            sys.exit(1)
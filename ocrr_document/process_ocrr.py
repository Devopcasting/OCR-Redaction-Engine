from database.connection import EstablishDBConnection
from document_identification.identify_doc import DocumentIdentification
from documents.cdsl.document_coordinates import CDSLDocumentInfo
from prepare_xml.redacted import WriteRedactedDocumentXML
import os

class ProcessDocumentOCRR:
    def __init__(self, docuemnt_info: dict, logger: object, redaction_level: int) -> None:
        self.document_info = docuemnt_info
        self.logger = logger
        self.redaction_level = redaction_level
        self.db_client = None

    def _initialize_db_connection(self):
        try:
            # Establish connection to MongoDB
            self.db_client = EstablishDBConnection().establish_connection()
        except Exception as e:
            self.logger.error(f"| Error in initializing DB connection: {e}")
            raise e
        
    def start_ocrr(self):
        try:
            self.logger.info("| Starting OCRR Process")
            identified_document = DocumentIdentification(self.document_info['ocrrworkspace_doc_path'], self.logger)
            idefntified_document_list = [
                (identified_document.identify_document_type("CDSL"), "CDSL", self._cdsl_ocrr_process)
            ]
            document_identified = False
            for document_status, document_type, document_process in idefntified_document_list:
                if document_status:
                    self.logger.info(f"| Document Identified as {document_type}")
                    document_process()
                    document_identified = True
                    break
            # Document Un-identified
            if not document_identified:
                self.logger.info(f"| Document Un-identified for task id: {self.document_info['taskId']}")
            
            # Remove document from the OCRR workspace
            self._remove_document_from_ocrr_workspace(self.document_info['ocrrworkspace_doc_path'])
            # Remove document from ocrrworkspace database ocrr collection
            self._remove_document_from_ocrr_workspace_collection_ocrr(self.document_info['taskId'])
            self.logger.info(f"| OCRR Process completed for: {self.document_info['taskId']}")
        except Exception as e:
            self.logger.error(f"| Error in OCRR Process: {e}")
            raise e
    
    # Write XML for coordinates
    def _write_xml(self, status: str, coordinate_data: list, message: str):
        if status == "REDACTED":
            self.logger.info("| Writing XML for coordinates")
            write_xml_coordinates = WriteRedactedDocumentXML(self.document_info['redactedPath'], self.document_info['document_name'], coordinate_data, self.logger)
            write_xml_coordinates.write_xml()
            self.logger.info(f"| XML Coordinate ready for {self.document_info['document_name']}")
            write_xml_coordinates.write_redacted_data()
            self.logger.info(f"| Redacted data ready for {self.document_info['document_name']}")
            # Update the document status in the database
            self._update_document_status(self.document_info['taskId'], "REDACTED", message)

    # OCRR Process CDSL Document
    def _cdsl_ocrr_process(self):
        self.logger.info("| Starting OCRR Process for CDSL Document")
        result = CDSLDocumentInfo(self.document_info['ocrrworkspace_doc_path'], self.logger, self.redaction_level).collect_document_info()
        # Write XML for coordinates
        self._write_xml(result['status'], result['data'], result['message'])
    
    # Update the document status in the database
    def _update_document_status(self, taskid: str, status: str, message: str):
        try:
            # Initialize the database connection
            self._initialize_db_connection()
            self.logger.info("| Updating document status in the database")
            database_name = "upload"
            collection_name = "fileDetails"
            database = self.db_client[database_name]
            collection = database[collection_name]
            taskid_filter = {"taskId": taskid}
            update = {"$set": {"status": status, "taskResult": message}}
            collection.update_one(taskid_filter, update)
            return True
        except Exception as e:
            self.logger.error(f"| Error in updating document status in the database: {e}")
            return False
    
    # Remove document from the OCRR workspace
    def _remove_document_from_ocrr_workspace(self, document_path: str) -> bool:
        try:
            self.logger.info(f"| Removing document from the OCRR workspace: {document_path}")
            os.remove(document_path)
            return True
        except Exception as e:
            self.logger.error(f"| Error in removing document from the OCRR workspace: {e}")
            return False
    
    # Remove document from the OCRR workspace collection ocrr
    def _remove_document_from_ocrr_workspace_collection_ocrr(self, taskid: str) -> bool:
        try:
            self.logger.info(f"| Removing document from the OCRR workspace ocrr collection: {taskid}")
            database_name = "ocrrworkspace"
            collection_name = "ocrr"
            database = self.db_client[database_name]
            collection = database[collection_name]
            taskid_filter = {"taskId": taskid}
            collection.delete_one(taskid_filter)
            return True
        except Exception as e:
            self.logger.error(f"| Error in removing document from the OCRR workspace collection: {e}")
            return False
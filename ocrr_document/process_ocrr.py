from database.connection import EstablishDBConnection
from document_identification.identify_doc import DocumentIdentification
from documents.cdsl.document_coordinates import CDSLDocumentInfo
from documents.e_pancard.document_coordinates import EPancardDocumentInfo
from documents.pancard.document_coordinates import PancardDocumentInfo
from documents.e_aadhaar.document_coordinates import EAadhaarDocumentInfo
from documents.aadhaar.document_coordinates import AadhaarDocumentInfo
from prepare_xml.redacted import WriteRedactedDocumentXML
from prepare_xml.rejected import WriteRejectedDocumentXML
from prepare_xml.rejected_doc_coordinates import GetRejectedDocumentCoordinates
from webhook.post_trigger import WebhookPostTrigger
import os
import sys

class ProcessDocumentOCRR:
    def __init__(self, docuemnt_info: dict, logger: object, redaction_level: int) -> None:
        self.document_info = docuemnt_info
        self.logger = logger
        self.redaction_level = redaction_level
        
        self.db_client = None
        self.collection_filedetails = None
        self.collection_ocrr = None
        self.collection_webhooks = None

        self.document_types = ["CDSL", "E-PANCARD", "PANCARD", "E-AADHAAR", "AADHAAR"]
        self.document_type_ocrr_methods = {
                "CDSL": self._cdsl_ocrr_process,
                "E-PANCARD": self._e_pancard_ocrr_process,
                "PANCARD": self._pancard_ocrr_process,
                "E-AADHAAR": self._e_aadhaar_ocrr_process,
                "AADHAAR": self._aadhaar_ocrr_process
            }

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
        except Exception as e:
            self.logger.error(f"| Failed to initialize MongoDB while Processing 'IN_PROGRESS' status documents: {e}")
    
    def start_ocrr(self):
        try:
            self.logger.info("| Starting OCRR Process")
            # Initialize DocumentIdentification
            identified_document = DocumentIdentification(self.document_info['ocrrworkspace_doc_path'], self.logger)
            
            # Set Flag for Docuemnt Identified
            document_identified = False
            
            # Loop through document types and identify the document type
            for document_type in self.document_types:
                document_status = identified_document.identify_document_type(document_type)
                if document_status:
                    self.logger.info(f"| Document Identified as {document_type}")
                    # Process the document
                    docuemnt_process = self.document_type_ocrr_methods[f"{document_type}"]
                    docuemnt_process()
                    # Set the Flag
                    document_identified = True
            
            # Check if document is un-identified
            if not document_identified:
                self.logger.info(f"| Document Un-identified for task id: {self.document_info['taskId']}")
                self._write_xml_rejected_status("Document Un-identified")
            # Final Stage of OCRR Process
            self._final_stage_ocrr_process(self.document_info['ocrrworkspace_doc_path'], self.document_info['taskId'])
        except Exception as e:
            self.logger.error(f"| Error in OCRR Process for task is: {self.document_info['taskId']}")
            self._write_xml_rejected_status(e)
            # Final Stage of OCRR Process
            self._final_stage_ocrr_process(self.document_info['ocrrworkspace_doc_path'], self.document_info['taskId'])
    
    # Write XML for REDACTED status
    def _write_xml_redacted_status(self, coordinate_data: list, message: str):
        self.logger.info("| Writing XML for REDACTED status document")
        write_xml_coordinates = WriteRedactedDocumentXML(self.document_info['redactedPath'], self.document_info['document_name'], coordinate_data, self.logger)
        write_xml_coordinates.write_xml()
        self.logger.info(f"| XML Coordinate ready for {self.document_info['document_name']}")
        write_xml_coordinates.write_redacted_data()
        self.logger.info(f"| Redacted data ready for {self.document_info['document_name']}")
        # Update the document status in the database
        self._update_document_status(self.document_info['taskId'], "REDACTED", message)

    # Write XML for REJECTED status
    def _write_xml_rejected_status(self, message: str):
        self.logger.info("| Writing XML for REJECTED status document")
        # Get the 80% coordinates for the rejected document
        rejected_doc_80_percent_coordinates = GetRejectedDocumentCoordinates(self.document_info['ocrrworkspace_doc_path']).get_coordinates()
        write_xml_coordinates = WriteRejectedDocumentXML(self.document_info['redactedPath'], self.document_info['document_name'], rejected_doc_80_percent_coordinates, self.logger)
        write_xml_coordinates.writexml()
        self.logger.info(f"| XML Coordinate ready for {self.document_info['document_name']}")
        # Update the document status in the database
        self._update_document_status(self.document_info['taskId'], "REJECTED", message)

    # OCRR Process CDSL Document
    def _cdsl_ocrr_process(self):
        self.logger.info("| Starting OCRR Process for CDSL Document")
        result = CDSLDocumentInfo(self.document_info['ocrrworkspace_doc_path'], self.logger, self.redaction_level).collect_document_info()
        # Write XML for coordinates for REDACTED or REJECTED status
        if result['status'] == "REDACTED":
            self._write_xml_redacted_status(result['data'], result['message'])
        else:
            self._write_xml_rejected_status(result['message'])

    # OCRR Process E-PANCARD Document
    def _e_pancard_ocrr_process(self):
        self.logger.info("| Starting OCRR Process for E-PANCARD Document")
        result = EPancardDocumentInfo(self.document_info['ocrrworkspace_doc_path'], self.logger, self.redaction_level).collect_document_info()
        # Write XML for coordinates for REDACTED or REJECTED status
        if result['status'] == "REDACTED":
            self._write_xml_redacted_status(result['data'], result['message'])
        else:
            self._write_xml_rejected_status(result['message'])

    # OCRR Process PANCARD Document
    def _pancard_ocrr_process(self):
        self.logger.info("| Starting OCRR Process for PANCARD Document")
        result = PancardDocumentInfo(self.document_info['ocrrworkspace_doc_path'], self.logger, self.redaction_level).collect_document_info()
        # Write XML for coordinates for REDACTED or REJECTED status
        if result['status'] == "REDACTED":
            self._write_xml_redacted_status(result['data'], result['message'])
        else:
            self._write_xml_rejected_status(result['message'])

    # OCRR Process E-AADHAAR Document
    def _e_aadhaar_ocrr_process(self):
        self.logger.info("| Starting OCRR Process for E-AADHAAR Document")
        result = EAadhaarDocumentInfo(self.document_info['ocrrworkspace_doc_path'], self.logger, self.redaction_level).collect_document_info()
        # Write XML for coordinates for REDACTED or REJECTED status
        if result['status'] == "REDACTED":
            self._write_xml_redacted_status(result['data'], result['message'])
        else:
            self._write_xml_rejected_status(result['message'])

    # OCRR Process AADHAAR Document
    def _aadhaar_ocrr_process(self):
        self.logger.info("| Starting OCRR Process for AADHAAR Document")
        result = AadhaarDocumentInfo(self.document_info['ocrrworkspace_doc_path'], self.logger, self.redaction_level).collect_document_info()
        # Write XML for coordinates for REDACTED or REJECTED status
        if result['status'] == "REDACTED":
            self._write_xml_redacted_status(result['data'], result['message'])
        else:
            self._write_xml_rejected_status(result['message'])

    # Update the document status in the database
    def _update_document_status(self, taskid: str, status: str, message: str):
        try:
            # Initialize the database connection
            self._initialize_db_connection()
            self.logger.info(f"| Updating document {status} status in the database")
            taskid_filter = {"taskId": taskid}
            update = {"$set": {"status": status, "taskResult": message}}
            self.collection_filedetails.update_one(taskid_filter, update)
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
        except Exception as e:
            self.logger.error(f"| Failed to send webhook request for task: {taskid}: {e}")
    
    # Final stage of OCRR process
    def _final_stage_ocrr_process(self, ocrrworkspace_doc_path: str, taskid: str):
        # Remove document from the OCRR workspace
        self._remove_document_from_ocrr_workspace(ocrrworkspace_doc_path)
        
        # Remove document from ocrrworkspace database ocrr collection
        self._remove_document_from_ocrr_workspace_collection_ocrr(taskid)
        self.logger.info(f"| OCRR Process completed for: {taskid}")
        
        # Send Webhook POST request for the TASKID
        # self._webhook_post_request(taskid)
        # self.logger.info(f"| Webhook POST request for: {taskid}")

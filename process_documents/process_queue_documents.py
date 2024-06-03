import os
import shutil
from time import sleep
import cv2
import numpy as np
from ocrr_document.process_ocrr import ProcessDocumentOCRR

class ProcessQueueDocuments:
    def __init__(self, doc_in_progress_status_queue: object, doc_upload_path: str, ocrr_workspace_path: str, logger: object) -> None:
        self.doc_in_progress_status_queue = doc_in_progress_status_queue
        self.doc_upload_path = doc_upload_path
        self.ocrr_workspace_path = ocrr_workspace_path
        self.logger = logger
    
    def process_queue_document(self):
        while True:
            try:
                document_info = self.doc_in_progress_status_queue.get()
                if document_info:
                    # Pre-Process the document
                    self._pre_process_queue_document(document_info)
                    # Process the document using OCRR
                    ProcessDocumentOCRR(document_info, self.logger).process_document()
                sleep(5)
            except Exception as e:
                self.logger.error(f"| Failed to process document: {e}")

    def _pre_process_queue_document(self, document_info: dict):
        try:
            # Copy the document to the OCRR workspace
            shutil.copy(document_info['path'], os.path.join(self.ocrr_workspace_path, document_info['renamedDoc']))
            self.logger.info(f"| Copied document to OCRR workspace: {document_info['renamedDoc']}")

            # Identify document as Grayscale and Pre-Process Colored document
            if not self._check_document_is_grayscale(os.path.join(self.ocrr_workspace_path, document_info['renamedDoc'])):
                self._pre_process_colored_document(os.path.join(self.ocrr_workspace_path, document_info['renamedDoc']))
        except Exception as e:
            self.logger.error(f"| Failed to Pre-Process document: {e}")
            return False
    
    def _check_document_is_grayscale(self, ocrr_workspace_doc_path: str) -> bool:
        try:
            # Load the image
            document = cv2.imread(ocrr_workspace_doc_path)

            # Check if the image has less than 3 dimensions (i.e., grayscale or single channel)
            if len(document.shape) < 3:
                return True

            # Check if the third dimension has only one channel
            if document.shape[2] == 1:
                return True

            # Split the image into its color channels
            b, g, r = document[:, :, 0], document[:, :, 1], document[:, :, 2]

            # Check if all channels are the same
            if (b == g).all() and (b == r).all():
                return True
            # If the above conditions are not met, the image is colored
            return False
        except Exception as e:
            self.logger.error(f"| Failed to check if document is grayscale: {e}")
            return False
    
    def _pre_process_colored_document(self, ocrr_workspace_doc_path: str) -> bool:
        try:
            sigma_x = 1
            sigma_y = 1
            sig_alpha = 1.5
            sig_beta = -0.2
            gamma = 0
        
            document = cv2.imread(ocrr_workspace_doc_path)
            denoise_document = cv2.fastNlMeansDenoisingColored(document, None, 10, 10, 7, 21)
            gray_document = cv2.cvtColor(denoise_document, cv2.COLOR_BGR2GRAY)
            gaussian_blur_document = cv2.GaussianBlur(gray_document, (5, 5), sigmaX=sigma_x, sigmaY=sigma_y)
            sharpened_image = cv2.addWeighted(gray_document, sig_alpha, gaussian_blur_document, sig_beta, gamma)
            sharpened_image_gray = cv2.cvtColor(sharpened_image, cv2.COLOR_GRAY2BGR)
            cv2.imwrite(ocrr_workspace_doc_path, sharpened_image_gray)
            return True
        except Exception as e:
            self.logger.error(f"| Failed to pre-process colored document: {e}")
            return False
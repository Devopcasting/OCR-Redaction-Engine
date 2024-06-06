import re
import os
import xml.etree.ElementTree as ET


class WriteRejectedDocumentXML:
    def __init__(self,  rejected_document_path: str, document_name: str, data_list: list, logger: object) -> None:
        self.rejected_document_path = rejected_document_path
        self.document_name = document_name
        self.data_list = data_list
        self.logger = logger
    
    def _extract_ids(self):
        try:
            pattern = "^[0-9]+F[0-9a-fA-Z_-]+"
            frame_str = self.document_name.split(".")[0].split('-')[0]
            matched_str = re.match(pattern, self.document_name)
            frame_id = None
            doc_id = None
            doc_id_num = None

            if matched_str:
                frame_id = int(frame_str.split("F")[0]) -1
                doc_id = re.split('_', self.document_name)[0].split('-')[1][:-1]
            else:
                doc_id_num = re.split('_', self.document_name)[0]
                doc_id = doc_id_num[:-1]
                frame_id = 0
            return frame_id, doc_id
        except Exception as e:
            self.logger.error(f"| Error in extracting ids {e}")
            return False
    
    def _prepare_data(self, frame_id, doc_id):
        data = []
        count_index = 1
        for coords in self.data_list:
            x1, y1, x2, y2 = coords
            data.append(f'0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,{frame_id},{doc_id},0,{count_index},{x1},{y1},{x2},{y2},0,0')
            count_index += 1
        return data
    
    def _create_xml_structure(self, data: list):
        root = ET.Element("DataBase")
        count = ET.SubElement(root, "Count")
        count.text = str(len(data))
        database_redactions = ET.SubElement(root, "DatabaseRedactions")
        for i, item in enumerate(data, start=1):
            database_redaction = ET.SubElement(database_redactions, "DatabaseRedaction", ID=str(i))
            database_redaction.text = item
        return root

    def writexml(self):
        try:
            frame_id, doc_id = self._extract_ids()
            data = self._prepare_data(frame_id, doc_id)
            root = self._create_xml_structure(data)
            tree = ET.ElementTree(root)
            xml_file_path = os.path.join(self.rejected_document_path, f"{self.document_name.split('.')[0]}.xml")
            if os.path.exists(xml_file_path):
                os.remove(xml_file_path)
            tree.write(xml_file_path, encoding="utf-8", xml_declaration=True)
            return True
        except Exception as e:
            self.logger.error(f"| Error in writing xml {e}")
            return False



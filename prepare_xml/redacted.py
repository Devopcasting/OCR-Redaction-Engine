import re
import os
import xml.etree.ElementTree as ET
class WriteRedactedDocumentXML:
    def __init__(self, redacted_document_path: str, document_name: str, data_list: list, logger: object) -> None:
        self.redacted_document_path = redacted_document_path
        self.document_name = document_name
        self.data_list = data_list
        self.logger = logger
    
    def _parse_document_info(self):
        try:
            pattern = "^[0-9]+F[0-9a-fA-Z_-]+"
            frame_str = self.document_name.split("_")[0].split('-')[0]
            matched_str = re.match(pattern, self.document_name)
            frame_id = None
            document_id = None
            doc_id_num = None

            if matched_str:
                frame_id =  int(frame_str.split('F')[0]) - 1
                document_id = re.split('_', self.document_name)[0].split('-')[1][:-1]
            else:
                doc_id_num = re.split('_', self.document_name)[0]
                frame_id = 0
                document_id = doc_id_num[:-1]
            return frame_id, document_id
        except Exception as e:
            self.logger.error(f"| Error in parsing document name {e}")
            return False
    
    def _prepare_coordinates_xml_data(self, frame_id, document_id) -> list:
        try:
            xml_data = []
            count_index = 1
            coordinates_list = [j for i in self.data_list for j in i['Coordinates'] if len(j) != 0]

            for x1, y1, x2, y2 in coordinates_list:
                xml_data.append(f'0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,{frame_id},{document_id},0,{count_index},{x1},{y1},{x2},{y2},0,0')
                count_index += 1
            return xml_data
        except Exception as e:
            self.logger.error(f"| Error in preparing coordinates xml data {e}")
            return False
    
    def _prepare_redacted_text_xml(self, frame_id, document_id) -> list:
        try:
            xml_data = []
            for i in self.data_list:
                title_text, value_text = list(i.items())[0]
                xml_data.append(f'"Title": "{title_text}", "FrameID": "{frame_id}", "DocID": "{document_id}", "Value": "{value_text}"')
            return xml_data
        except Exception as e:
            self.logger.error(f"| Error in preparing redacted text xml data {e}")
            return False
    
    def _write_xml(self, xml_data: list, element_name: str) -> None:
        try:
            root = ET.Element("DataBase")
            count = ET.SubElement(root, "Count")
            count.text = str(len(xml_data))
            database_element = ET.SubElement(root, element_name)
            
            for i, item in enumerate(xml_data, start=1):
                item_element = ET.SubElement(database_element, element_name[:-1], ID=str(i))
                item_element.text = str(item)
            
            xml_file_path = os.path.join(self.redacted_document_path, self._rename_xml_file(self.document_name, element_name))
            tree = ET.ElementTree(root)
            tree.write(xml_file_path, encoding="utf-8", xml_declaration=True)
        except Exception as e:
            self.logger.error(f"| Error in writing xml file {e}")
            return False

    def write_xml(self):
        try:
            frame_id, document_id = self._parse_document_info()
            coordinates_xml_data = self._prepare_coordinates_xml_data(frame_id, document_id)
            self._write_xml(coordinates_xml_data, "DatabaseRedactions")
            return True
        except Exception as e:
            self.logger.error(f"| Error in writing xml file {e}")
            return False

    def write_redacted_data(self):
        try:
            frame_id, document_id = self._parse_document_info()
            text_xml_data = self._prepare_redacted_text_xml(frame_id, document_id)
            self._write_xml(text_xml_data, "indexvalues")
            return True
        except Exception as e:
            self.logger.error(f"| Error in writing xml file {e}")
            return False
        
    @staticmethod
    def _rename_xml_file(filename: str, element_name: str) -> str:
        filename_list = filename.split('_', 1)
        renamed_filename = ""
        if element_name == "indexvalues":
            renamed_filename = f"{filename_list[0]}-RD_{filename_list[-1]}"
        else:
            renamed_filename = filename
        return renamed_filename.rsplit('.', 1)[0] + '.xml'

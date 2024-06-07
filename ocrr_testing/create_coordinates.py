import xml.etree.ElementTree as ET
import sys

# Sample XML data
xml_data = '''
<DataBase>
<Count>5</Count>
<DatabaseRedactions>
<DatabaseRedaction ID="1">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,1,1,0,1,605,679,650,690,0,0</DatabaseRedaction>
<DatabaseRedaction ID="2">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,1,1,0,2,655,678,715,689,0,0</DatabaseRedaction>
<DatabaseRedaction ID="3">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,1,1,0,3,719,677,792,698,0,0</DatabaseRedaction>
<DatabaseRedaction ID="4">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,1,1,0,4,955,526,1065,581,0,0</DatabaseRedaction>
<DatabaseRedaction ID="5">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,1,1,0,5,599,542,675,580,0,0</DatabaseRedaction>
</DatabaseRedactions>
</DataBase>
'''
# Parse the XML data
root = ET.fromstring(xml_data)

# Open a file for writing
with open("output.txt", "w") as file:
    # Find all DatabaseRedaction elements
    database_redactions = root.findall(".//DatabaseRedaction")

    # Iterate over each DatabaseRedaction element
    for redaction in database_redactions:
        # Extract the specific values and join them with spaces
        values = redaction.text.split(',')[20:24]
        # Write the values to the file with spaces
        file.write(' '.join(values) + '\n')
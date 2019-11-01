import xml.etree.ElementTree as ET
from xml.dom import minidom
from random import randint
from zipfile import ZipFile
from io import BytesIO
import Tools


_NUMB_OF_ZIP = 50
_NUMB_OF_XML_PER_ZIP = 100
_DIR_FOR_XML_FILES = '.\\RESULT'


def main():
    lst_of_rand_str = Tools.get_random_unique_strings(_NUMB_OF_ZIP * _NUMB_OF_XML_PER_ZIP)

    # Part 1. Write ZIP files with XML files (1 thread only)
    # loop of ZIP
    for zip_i in range(_NUMB_OF_ZIP):
        # create ZIP file in memory
        mem_buf = BytesIO()
        mem_zip_file = ZipFile(file=mem_buf, mode='w')

        # loop of XML
        for xml_i in range(_NUMB_OF_XML_PER_ZIP):
            # make XML data for 1 file
            # <root>
            root = ET.Element('root', attrib={}, )

            # -<var name=’id’ value=’<random_unique_string_value>’/>
            var_1 = ET.SubElement(root, 'var')
            var_1.set('name', 'id')                                             # add attribute "name"
            var_1.set('value', lst_of_rand_str[_NUMB_OF_ZIP * zip_i + xml_i])   # add attribute "value"

            # -<var name=’id’ value=’<random_unique_string_value>’/>
            var_2 = ET.SubElement(root, 'var')
            var_2.set('name', 'level')                                          # add attribute "name"
            var_2.set('value', str(randint(1, 100)))                            # add attribute "value"

            # -<objects>
            objects = ET.SubElement(root, 'objects')

            # --<object name=’<random_string_value>’/>
            for _ in range(randint(1, 10)):
                obj = ET.SubElement(objects, 'object')
                obj.set('name', Tools.get_random_str_value())
            # Completed

            # make pretty format for XML data
            xml_data = minidom.parseString(ET.tostring(root))\
                .toprettyxml(indent="   ").replace('<?xml version="1.0" ?>\n', '')

            # write XML data to ZIP file in memory
            mem_zip_file.writestr(f'file_{xml_i:03}.xml', str.encode(xml_data, 'utf-8'))

        mem_zip_file.close()

        # write ZIP file to disk
        with open(f'{_DIR_FOR_XML_FILES}\\file_{zip_i:02}.zip', 'wb') as f:
            f.write(mem_buf.getvalue())

    pass


if __name__ == '__main__':
    main()

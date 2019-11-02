from collections import namedtuple
from typing import List, Dict
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from random import randint
from zipfile import ZipFile
from io import BytesIO
import multiprocessing
from multiprocessing import Process, Manager
import Tools


_NUMB_OF_LOGIC_CORES = multiprocessing.cpu_count()
_NUMB_OF_ZIP = 50
_NUMB_OF_XML_PER_ZIP = 100
_DIR_FOR_ZIP_FILES = '.\\RESULT\\zips'


ParsedXml = namedtuple('ParsedXml', ['id_', 'level', 'objects_names'])


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
        with open(f'{_DIR_FOR_ZIP_FILES}\\file_{zip_i:02}.zip', 'wb') as f:
            f.write(mem_buf.getvalue())

    # Part 2. Reading XML form ZIP files and writing to CSV


    pass


def process_unzip_function(zip_files_names: List[str], result: Dict[str, Dict[str, ParsedXml]]):
    """Function for dedicated process. It unzips N archives and parse XML files into each of them."""

    # loop of ZIP files
    for zip_file_name in zip_files_names:
        result[zip_file_name] = {}
        zip_file = ZipFile(file=f'{_DIR_FOR_ZIP_FILES}\\{zip_file_name}', mode='r')

        # loop of XML files into ZIP
        for xml_file_name in zip_file.namelist():
            xml_file = zip_file.read(xml_file_name)             # get content of XML files
            root = ET.fromstring(xml_file)                      # restore XML structure from bytes

            # parsing
            var_1, var_2, objects = root.findall("./")
            _id = var_1.attrib['value']
            _level = var_2.attrib['value']
            _objects_names = [_obj.attrib['name'] for _obj in objects.findall("./")]

            # store data of current XML to shared memory
            result[zip_file_name][xml_file_name] = ParsedXml(_id, _level, _objects_names)


if __name__ == '__main__':
    # TODO: add priority of process
    #main()
    result = Manager().dict()           # shared memory (dictionary)
    processes = []                      # "pool" of process;
                                        # Important: native Pool is not work on PyCharm IDE! Therefore Process() is used.

    # preparing of tasks for each process
    names_of_zips = os.listdir(_DIR_FOR_ZIP_FILES)
    tasks_per_core = [[] for i in range(_NUMB_OF_LOGIC_CORES)]
    for i in range(len(names_of_zips)):
        tasks_per_core[i % _NUMB_OF_LOGIC_CORES].append(names_of_zips[i])

    # start processes
    for i in range(_NUMB_OF_LOGIC_CORES):
        p = Process(target=process_unzip_function, args=[tasks_per_core[i], result])
        p.start()
        processes.append(p)

    # wait result
    for i in range(_NUMB_OF_LOGIC_CORES):
        processes[i].join()

    # TODO: add CSV
    print(len(result))

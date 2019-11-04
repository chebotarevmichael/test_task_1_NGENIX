from typing import List, Dict
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from random import randint
from zipfile import ZipFile
from io import BytesIO
import multiprocessing
from time import time
from multiprocessing import Process, Manager
import Tools
from ParsedXml import ParsedXml


_NUMB_OF_LOGIC_CORES = multiprocessing.cpu_count()
_NUMB_OF_ZIP = 50
_NUMB_OF_XML_PER_ZIP = 100
_DIR_FOR_ZIP_FILES = '.\\RESULT\\zips'
_DIR_FOR_CSV_FILES = '.\\RESULT'


def process_unzipping(zip_files_names: List[str], result: Dict[str, Dict[str, ParsedXml]]):
    """Function for dedicated process. It unzips N archives and parse XML files into each of them."""

    # loop of ZIP files
    for zip_file_name in zip_files_names:
        zip_file = ZipFile(file=f'{_DIR_FOR_ZIP_FILES}\\{zip_file_name}', mode='r')

        # loop of XML files into ZIP
        cur_zip_content = {}
        for xml_file_name in zip_file.namelist():
            # restore XML object from ZIP file
            xml_file = zip_file.read(xml_file_name)             # get content of XML files
            root = ET.fromstring(xml_file)                      # restore XML structure from bytes

            # parsing
            var_1, var_2, objects = root.findall("./")
            _id = var_1.attrib['value']
            _level = var_2.attrib['value']
            _objects_names = [_obj.attrib['name'] for _obj in objects.findall("./")]

            # write data of current XML to shared memory
            cur_zip_content[xml_file_name] = ParsedXml(_id, _level, _objects_names)

        result[zip_file_name] = cur_zip_content                 # specificity of work with ZIP


def main():
    ts_start = time()
    output_data: Dict[str, Dict[str, ParsedXml]] = {}

    lst_of_rand_str = Tools.get_random_unique_strings(_NUMB_OF_ZIP * _NUMB_OF_XML_PER_ZIP)
    Tools.remove_all_files_in_dir(_DIR_FOR_ZIP_FILES)

    # Build data for all XML and ZIP files (it will be used for validating in assert)
    # loop of ZIP
    for zip_i in range(_NUMB_OF_ZIP):
        zip_file_name = f'file_{zip_i:02}.zip'
        output_data[zip_file_name] = {}

        # loop of XML
        for xml_i in range(_NUMB_OF_XML_PER_ZIP):
            xml_file_name = f'file_{xml_i:03}.xml'

            # craft data (id, level, objects) for one XML file
            output_data[zip_file_name][xml_file_name] = \
                ParsedXml(id_=lst_of_rand_str[_NUMB_OF_XML_PER_ZIP * zip_i + xml_i],
                          level=str(randint(1, 100)),
                          objects_names=[Tools.get_random_str_value() for _ in range(randint(1, 10))])

    # Part 1. Write ZIP files with XML files (1 thread only)
    # loop of ZIP
    for zip_file_name in output_data.keys():
        # create ZIP file in memory
        mem_buf = BytesIO()
        mem_zip_file = ZipFile(file=mem_buf, mode='w')

        # loop of XML
        for xml_file_name in output_data[zip_file_name].keys():
            xml_files_data: ParsedXml = output_data[zip_file_name][xml_file_name]

            # make XML data for 1 file
            # <root>
            root = ET.Element('root')

            # -<var name=’id’ value=’<random_unique_string_value>’/>
            var_1 = ET.SubElement(root, 'var')
            var_1.set('name', 'id')                         # add attribute "name"
            var_1.set('value', xml_files_data.id_)                # add attribute "value"

            # -<var name=’id’ value=’<random_unique_string_value>’/>
            var_2 = ET.SubElement(root, 'var')
            var_2.set('name', 'level')                      # add attribute "name"
            var_2.set('value', xml_files_data.level)              # add attribute "value"

            # -<objects>
            objects = ET.SubElement(root, 'objects')

            # --<object name=’<random_string_value>’/>
            for object_name in xml_files_data.objects_names:
                obj = ET.SubElement(objects, 'object')
                obj.set('name', object_name)
            # Completed

            # make pretty format for XML data
            xml_str_data = minidom.parseString(ET.tostring(root))\
                .toprettyxml(indent="   ").replace('<?xml version="1.0" ?>\n', '')

            # write XML data to ZIP file in memory
            mem_zip_file.writestr(xml_file_name, str.encode(xml_str_data, 'utf-8'))

        mem_zip_file.close()

        # write ZIP file to disk
        with open(f'{_DIR_FOR_ZIP_FILES}\\{zip_file_name}', 'wb') as f:
            f.write(mem_buf.getvalue())

    #
    # Part 2. Reading XML form ZIP files and writing to CSV
    # Important! native Pool is not work on PyCharm IDE therefore Process() is used instead Pool().
    input_data: Dict[str, Dict[str, ParsedXml]] = Manager().dict()  # shared memory (dictionary)
    processes = []                                                  # "pool" of process;

    # preparing sub-tasks for each process
    names_of_zips = os.listdir(_DIR_FOR_ZIP_FILES)
    tasks_per_core = [[] for _ in range(_NUMB_OF_LOGIC_CORES)]
    for i in range(len(names_of_zips)):
        tasks_per_core[i % _NUMB_OF_LOGIC_CORES].append(names_of_zips[i])

    # start processes
    for i in range(_NUMB_OF_LOGIC_CORES):
        p = Process(target=process_unzipping, args=[tasks_per_core[i], input_data])
        p.start()
        processes.append(p)

    # wait result
    for i in range(_NUMB_OF_LOGIC_CORES):
        processes[i].join()

    # validate result
    assert sorted(output_data) == sorted(input_data), f'Error. Input and output data is not equal!' \
                                                      f'\noutput: {output_data}' \
                                                      f'\ninput: {input_data}'

    # write to CSV
    xml_files_data: List[ParsedXml] = [xml_file_data for xml_dict in input_data.values()
                                       for xml_file_data in xml_dict.values()]
    Tools.write_data_to_csv_file(path_csv=f'{_DIR_FOR_CSV_FILES}\\id_and_level.csv',
                                 data=[(xml_file_data.id_, xml_file_data.level) for xml_file_data in xml_files_data])
    Tools.write_data_to_csv_file(path_csv=f'{_DIR_FOR_CSV_FILES}\\id_and_object_name.csv',
                                 data=[(xml_file_data.id_, obj_name) for xml_file_data in xml_files_data
                                       for obj_name in xml_file_data.objects_names])
    print(f'Finished after {round(time() - ts_start, 2)} sec.')

if __name__ == '__main__':
    # TODO: add priority of process
    main()


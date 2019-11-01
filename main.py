import xml.etree.ElementTree as ET
from random import randint
import Tools


_NUMB_OF_ZIP = 50
_NUMB_OF_XML_PER_ZIP = 100


def main():
    lst_of_rand_str = Tools.get_random_unique_strings(_NUMB_OF_ZIP * _NUMB_OF_XML_PER_ZIP)
    i = 0

    # <root>
    a = ET.Element('root')

    #    <var name=’id’ value=’<random_unique_string_value>’/>
    var_1 = ET.SubElement(a, 'var')
    var_1.set('name', 'id')                             # add attribute "name"
    var_1.set('value', lst_of_rand_str[i])              # add attribute "value"

    #    <var name=’id’ value=’<random_unique_string_value>’/>
    var_2 = ET.SubElement(a, 'var')
    var_2.set('name', 'level')                          # add attribute "name"
    var_2.set('value', str(randint(1, 100)))            # add attribute "value"

    #    <objects>
    



    print(ET.dump(a))
    pass


if __name__ == '__main__':
    main()

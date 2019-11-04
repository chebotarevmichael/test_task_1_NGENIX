from typing import List
import os
import hashlib
import csv


def get_random_unique_strings(numb_of_str) -> List[str]:
    """
    :param numb_of_str:     length of list
    :return:                list of unique string values
    """
    list_of_unique_strings = []
    i = 0
    while i < numb_of_str:
        # generate random str
        rand_str = get_random_str_value()

        # is string unique?
        if rand_str not in list_of_unique_strings:
            list_of_unique_strings.append(rand_str)
            i += 1

    return list_of_unique_strings


def get_random_str_value() -> str:
    return hashlib.md5(os.urandom(32)).hexdigest()


def remove_all_files_in_dir(dir_path):
    for file in os.listdir(dir_path):
        path_to_file = f'{dir_path}//{file}'

        # remove only files
        if os.path.isfile(path_to_file):
            os.remove(path_to_file)


def write_data_to_csv_file(path_csv: str, data) -> bool:
    """Create and write @data to CSV file at @path"""
    try:
        with open(path_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(('id', 'level'))
            writer.writerows(data)

        print(f'Success. Looking for CSV file: "{path_csv}"')
        return True
    except PermissionError:
        print(f'ERROR. Permission denied: "{path_csv}"')
        return False
    except:
        print(f'ERROR. Unexpected exception: "{path_csv}"')
        return False

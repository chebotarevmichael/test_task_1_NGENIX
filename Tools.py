from typing import List
import os
import hashlib


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

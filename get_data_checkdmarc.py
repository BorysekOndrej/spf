import json
from typing import List
import checkdmarc
import get_data_website_lists
from util import create_folder_for_file

filename_checkdmarc = 'data/checkdmarc/checkdmarc.json'


def try_use_checkdmarc(hostnames: List[str], output_filename: str):
    test1 = checkdmarc.check_domains(hostnames, skip_tls=True)
    with open(output_filename, "w", encoding="utf8") as f:
        json.dump(test1, f, indent=3)
    

if __name__ == "__main__":
    with open(get_data_website_lists.filename_merged_to_check, "r", encoding="utf8") as f:
        list_of_possible_web_targets = f.readlines()

    create_folder_for_file(filename_checkdmarc)
    try_use_checkdmarc(list_of_possible_web_targets, filename_checkdmarc)


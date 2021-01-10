import sys
import requests
from config import api_token
import json
import urllib.parse
import itertools
from typing import List
from os import path
from util import beautify_json_file, load_txt_list_file_and_strip, create_folder_for_file
import csv

filename_weby_hlidac_statu = 'data/source_lists/weby_hlidac_statu.json'
filename_weby_hlidac_statu_indented = 'data/source_lists/weby_hlidac_statu_indented.json'
filename_weby_hlidac_statu_list = 'data/source_lists/weby_hlidac_statu_list.txt'

filename_majestic_million = 'data/source_lists/majestic_million.csv'
filename_weby_majestic_top_500 = 'data/source_lists/weby_majestic_top_500.txt'

filename_merged_to_check = 'data/source_lists/weby_merged.txt'


def download_web_list():
    if not path.exists(filename_weby_hlidac_statu):
        s = requests.Session()
        headers = {'Accept': 'application/json', 'Authorization': f'Token {api_token}'}
        api_response = s.get('https://www.hlidacstatu.cz/api/v2/Weby', headers=headers)
        # print(api_response.text)

        if api_response.status_code != 200:
            print(api_response.status_code)
            sys.exit(1)

        with open(filename_weby_hlidac_statu, "w", encoding="utf-8") as f:
            f.write(api_response.text)

        beautify_json_file(filename_weby_hlidac_statu, filename_weby_hlidac_statu_indented)


def parse_web_list() -> List[str]:
    with open(filename_weby_hlidac_statu_indented, "r", encoding="utf8") as f:
        data = json.load(f)
    list_of_urls = list(map(lambda x: x.get("url"), data))
    list_of_hostnames = list(map(lambda x: urllib.parse.urlparse(x).hostname, list_of_urls))
    list_of_domains = list(map(lambda x: ".".join(x.split(".")[-2:]), list_of_hostnames)) # this will not work for things like www.bbc.co.uk, but .cz doesn't have that
    
    final_set = set(itertools.chain(list_of_hostnames, list_of_domains))
    final_list_sorted = sorted(final_set, key=lambda x: x[::-1])
    return final_list_sorted


def download_majestic_million():
    if not path.exists(filename_majestic_million):
        api_response = requests.get('https://downloads.majestic.com/majestic_million.csv')

        if api_response.status_code != 200:
            print(api_response.status_code)
            sys.exit(1)

        with open(filename_majestic_million, "w", encoding="utf-8") as f:
            f.write(api_response.text)

    if not path.exists(filename_weby_majestic_top_500):
        sites_list = []
        with open(filename_majestic_million, newline='', encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            i = -1
            for row in reader:
                i += 1
                if i == 0:
                    continue  # the csv has header                
                if len(sites_list) >= 500:
                    break
                sites_list.append(row[2])
        # print(sites_list)
        with open(filename_weby_majestic_top_500, "w", encoding="utf-8") as f:
            f.write("\n".join(sites_list))


def merge_lists(filename_a: str, filename_b: str, output_filename):
    a = load_txt_list_file_and_strip(filename_a)
    b = load_txt_list_file_and_strip(filename_b)
    c = set(a+b)
    with open(output_filename, "w", encoding="utf8") as f:
        f.write("\n".join(c))


if __name__ == "__main__":
    create_folder_for_file(filename_weby_hlidac_statu)

    download_web_list()
    list_of_possible_web_targets = parse_web_list()
        
    if not path.exists(filename_weby_hlidac_statu_list):
        with open(filename_weby_hlidac_statu_list, "w", encoding="utf8") as f:
            f.write("\n".join(list_of_possible_web_targets))

    download_majestic_million()

    merge_lists(filename_weby_hlidac_statu_list, filename_weby_majestic_top_500, filename_merged_to_check)

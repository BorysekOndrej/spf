import json
import spf
from tqdm import tqdm

from util import load_txt_list_file_and_strip, create_folder_for_file
import get_data_website_lists

filename_input = get_data_website_lists.filename_merged_to_check
filename_output = 'data/pyspf/raw.json'
# pip install dnspython pyspf authres loguru


def test_spf_record_validity(domain: str):
    return spf.check2(i='192.0.2.1', s=f'spf_research@{domain}', h=f'{domain}')


def main():
    create_folder_for_file(filename_output)

    domains = load_txt_list_file_and_strip(filename_input)
    results = {}
    for domain in tqdm(domains):
        results[domain] = test_spf_record_validity(domain)

    with open(filename_output, "w", encoding="utf8") as f:
        json.dump(results, f, indent=3, ensure_ascii=False, sort_keys=True)


if __name__ == "__main__":
    main()

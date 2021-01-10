import json
from util import beautify_json_file

filename_dns_crawler_raw = 'data/fromAdam/raw.json'
filename_dns_crawler_indented = 'data/fromAdam/output_beautified.json'
filename_dns_crawler_filtered = 'data/fromAdam/output_filtered.json'


def fix_json_file_from_dns_crawler(filename):
    with open(filename, "r", encoding="utf8") as f:
        whole_file_lines = f.readlines()
    if whole_file_lines[0][0] == "[":
        return

    with open(filename, "w", encoding="utf8") as f:
        new_whole_file = ",\n".join(whole_file_lines)
        f.write(f'[{new_whole_file}]')


def filter_dns_crawler_results(input_filename: str, output_filename: str):
    with open(input_filename, "r", encoding="utf8") as f:
        data = json.load(f)

    answer = []
    for x in data:
        new_dict = {}
        new_dict["domain"] = x.get("domain")
        new_dict["dns_txt"] = x.get("results").get("DNS_LOCAL").get("TXT")
        new_dict["dns_txt_spf"] = x.get("results").get("DNS_LOCAL").get("TXT_SPF")
        new_dict["dns_txt_dmarc"] = x.get("results").get("DNS_LOCAL").get("TXT_DMARC")
        new_dict["mail"] = x.get("results").get("MAIL")
        answer.append(new_dict)

    with open(output_filename, "w", encoding="utf8") as f:
        json.dump(answer, f, indent=3)
    

if __name__ == "__main__":
    fix_json_file_from_dns_crawler(filename_dns_crawler_raw)
    beautify_json_file(filename_dns_crawler_raw, filename_dns_crawler_indented)
    filter_dns_crawler_results(filename_dns_crawler_indented, filename_dns_crawler_filtered)


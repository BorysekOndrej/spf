import json
from typing import List, Set, Dict, Any
from pprint import pprint
from loguru import logger

import filter_data_from_cznic_adam
import get_data_checkdmarc
import get_data_website_lists
import get_data_pyspf
from util import load_txt_list_file_and_strip

filename_weby_hlidac_statu_list = get_data_website_lists.filename_weby_hlidac_statu_list
filename_weby_majestic_top_500 = get_data_website_lists.filename_weby_majestic_top_500

filename_dns_crawler_filtered = filter_data_from_cznic_adam.filename_dns_crawler_filtered
filename_checkdmarc = get_data_checkdmarc.filename_checkdmarc
filename_pyspf = get_data_pyspf.filename_output

filename_final_result = 'data/preprocess_output/result.json'
filename_final_result_cz_gov = 'data/preprocess_output/result_cz_gov.json'
filename_final_result_top_500 = 'data/preprocess_output/result_top_500.json'


def load_data():
    with open(filename_dns_crawler_filtered, "r", encoding="utf8") as f:
        return json.load(f)


def get_first_or_default(x, default):
    if x is None:
        return default
    return x


def extract_dns_txt_field(full_result: Dict[str, dict], field: str) -> Dict[str, dict]:
    answer = {}

    for single_domain in full_result:
        dns_txt_single_field = get_first_or_default(full_result[single_domain]["raw_result"].get(field), [])

        if len(dns_txt_single_field) > 1:
            logger.warning("Multiple TXT SPFs. This is unusual, the rest of the program will consider the first one.")

        answer[single_domain] = {}
        if len(dns_txt_single_field):
            answer[single_domain] = dns_txt_single_field[0]

    return answer


def extract_dns_txt_spf(full_result: Dict[str, dict]) -> Dict[str, dict]:
    return extract_dns_txt_field(full_result, "dns_txt_spf")


def extract_dns_txt_dmarc(full_result: Dict[str, dict]) -> Dict[str, dict]:
    return extract_dns_txt_field(full_result, "dns_txt_dmarc")


def is_main_domain(full_result: Dict[str, dict]) -> Dict[str, bool]:
    answer = {}
    for single_domain in full_result:
        answer[single_domain] = single_domain.count(".") == 1
    return answer


def has_spf_record(full_result: Dict[str, dict]) -> Dict[str, bool]:
    answer = {}
    for single_domain in full_result:
        answer[single_domain] = len(full_result[single_domain]["extract_dns_txt_spf"]) > 0
    return answer


def has_dmarc_record(full_result: Dict[str, dict]) -> Dict[str, bool]:
    answer = {}
    for single_domain in full_result:
        answer[single_domain] = len(full_result[single_domain]["extract_dns_txt_dmarc"]) > 0
    return answer


def is_main_domain_or_spf_or_dmarc(full_result: Dict[str, dict]) -> Dict[str, bool]:
    answer = {}
    for single_domain in full_result:
        answer[single_domain] = full_result[single_domain]["has_spf_record"] or \
                                full_result[single_domain]["has_dmarc_record"] or \
                                full_result[single_domain]["is_main_domain"]
    return answer


def spf_all(full_result: Dict[str, dict]) -> Dict[str, bool]:
    answer = {}
    for single_domain in full_result:
        answer[single_domain] = full_result[single_domain]["extract_dns_txt_spf"].get("all", "NO SPF")
    return answer


def has_mx_record(full_result: Dict[str, dict]) -> Dict[str, bool]:
    answer = {}
    for single_domain in full_result:
        answer[single_domain] = len(get_first_or_default(full_result[single_domain]["raw_result"].get("mail"), [])) > 0
    return answer


def direct_includes(full_result: Dict[str, dict]) -> Dict[str, str]:
    answer = {}
    for single_domain in full_result:
        answer[single_domain] = ";".join(full_result[single_domain]["extract_dns_txt_spf"].get("include", ""))
    return answer


# todo: spf2.0/pra
# todo: check for private IPs

def example_failed_dns_lookup():
    domain = "businessinfo.cz"
    value = "v=spf1 mx ip4:193.86.21.51 ip4:193.86.21.52 ip4:193.86.21.3 ip4:193.86.21.23 ip4:193.86.21.33 ip4:193.86.21.29 ip4:193.86.21.241 ip4:193.86.21.235 ip4:193.85.215.251 ip4:62.109.140.190 ip4:212.67.71.5 ip4:93.185.102.127 ip4:193.86.21.25 include:sendg\" \"rid.net -all\""
    value_smaller = "v=spf1 mx include:sendg\" \"rid.net -all\""


def extract_largest_direct_ranges(full_result: Dict[str, dict], field: str) -> Dict[str, str]:
    INF_RANGE_CONST = 10000

    answer = {}
    for single_domain in full_result:
        answer[single_domain] = INF_RANGE_CONST
        ranges = []
        field_arr = full_result[single_domain]["extract_dns_txt_spf"].get(field, [])
        for x in field_arr:
            if "/" in x:
                ranges.append(x)
        for x in ranges:
            range_str = x.split("/")[1]
            range_str = range_str.replace('"', '')
            range_int = int(range_str)
            answer[single_domain] = min(range_int, answer[single_domain])

        if answer[single_domain] == INF_RANGE_CONST:
            answer[single_domain] = None
    return answer


def extract_largest_direct_ranges_ip4(full_result: Dict[str, dict]) -> Dict[str, str]:
    return extract_largest_direct_ranges(full_result, 'ip4')


def extract_largest_direct_ranges_ip6(full_result: Dict[str, dict]) -> Dict[str, str]:
    return extract_largest_direct_ranges(full_result, 'ip6')


def extract_largest_direct_ranges_mx(full_result: Dict[str, dict]) -> Dict[str, str]:
    return extract_largest_direct_ranges(full_result, 'mx')


def dmarc_rua(full_result: Dict[str, dict]) -> Dict[str, bool]:
    answer = {}
    for single_domain in full_result:
        answer[single_domain] = full_result[single_domain]["extract_dns_txt_dmarc"].get("rua", None)
    return answer


def dmarc_ruf(full_result: Dict[str, dict]) -> Dict[str, bool]:
    answer = {}
    for single_domain in full_result:
        answer[single_domain] = full_result[single_domain]["extract_dns_txt_dmarc"].get("ruf", None)
    return answer


def dmarc_reporting(full_result: Dict[str, dict]) -> Dict[str, bool]:
    answer = {}
    for single_domain in full_result:
        ruf = bool(full_result[single_domain]["dmarc_ruf"])
        rua = bool(full_result[single_domain]["dmarc_rua"])
        answer[single_domain] = "DMARC but no monitoring" if full_result[single_domain]["has_dmarc_record"] else "NO DMARC"
        if rua:
            answer[single_domain] = "rua"
        if ruf:
            answer[single_domain] = "ruf"
        if rua and ruf:
            answer[single_domain] = "rua + ruf"
    return answer


def dmarc_has_reporting(full_result: Dict[str, dict]) -> Dict[str, bool]:
    answer = {}
    for single_domain in full_result:
        answer[single_domain] =  bool(full_result[single_domain]["dmarc_ruf"]) or bool(full_result[single_domain]["dmarc_rua"])
    return answer


def dmarc_action(full_result: Dict[str, dict]) -> Dict[str, bool]:
    answer = {}
    for single_domain in full_result:
        answer[single_domain] = full_result[single_domain]["extract_dns_txt_dmarc"].get("p", "NO DMARC")
    return answer


def evaluate(raw_data):
    columns_order = [
        extract_dns_txt_spf,
        extract_dns_txt_dmarc,
        has_spf_record,
        has_dmarc_record,
        is_main_domain,
        is_main_domain_or_spf_or_dmarc,
        spf_all,
        has_mx_record,
        direct_includes,
        extract_largest_direct_ranges_ip4,
        extract_largest_direct_ranges_ip6,
        extract_largest_direct_ranges_mx,
        dmarc_rua,
        dmarc_ruf,
        dmarc_reporting,
        dmarc_has_reporting,
        dmarc_action,
    ]

    full_result = {}
    for single_dict in raw_data:
        full_result[single_dict["domain"]] = {"raw_result": single_dict}

    for single_function in columns_order:
        function_name = str(single_function).split(" ")[1]
        result = single_function(full_result)
        for single_domain in result:
            full_result[single_domain][function_name] = result[single_domain]

    return full_result


def filter_file(filename_all, filename_select, filename_output):
    with open(filename_all, "r", encoding="utf8") as f:
        data = json.load(f)
    select_list = load_txt_list_file_and_strip(filename_select)
    result = dict()
    for x in data:
        if x in select_list:
            result[x] = data[x]
    with open(filename_output, "w", encoding="utf8") as f:
        json.dump(result, f, indent=3, ensure_ascii=False, sort_keys=True)


def add_pyspf(data: dict):
    with open(filename_pyspf, "r", encoding="utf8") as f:
        pyspf_data = json.load(f)

    for domain_name in data:
        data[domain_name]["pyspf_result"] = pyspf_data[domain_name][0] if pyspf_data[domain_name][0] != "none" else None
        data[domain_name]["pyspf_msg"] = pyspf_data[domain_name][1]

    return data


def main():
    data = load_data()
    # print(extract_all_includes(data))
    # pprint(count_dns_txt_spf_records(data))
    # print(f'check_no_more_than_1_txt_spf_records: {check_no_more_than_1_txt_spf_records(data)}')

    #pprint(extract_dns_txt_spf(data))
    #pprint(extract_dns_txt_dmarc(data))

    result = evaluate(data)
    # pprint(result)

    result = add_pyspf(result)

    with open(filename_final_result, "w", encoding="utf8") as f:
        json.dump(result, f, indent=3, ensure_ascii=False, sort_keys=True)

    filter_file(filename_final_result, filename_weby_hlidac_statu_list, filename_final_result_cz_gov)
    filter_file(filename_final_result, filename_weby_majestic_top_500, filename_final_result_top_500)


if __name__ == "__main__":
    main()



import json
import typing
from pathlib import Path


def beautify_json_file(input_filename: str, output_filename: str):
    with open(input_filename, "r", encoding="utf8") as f_in:
        with open(output_filename, "w", encoding="utf8") as f_out:
            a = json.load(f_in)
            # print(a)
            json.dump(a, f_out, indent=3, ensure_ascii=False)


def load_txt_list_file_and_strip(input_filename: str) -> typing.List[str]:
    with open(input_filename, "r", encoding="utf8") as f:
        lines = f.readlines()
    return list(map(lambda x: x.strip(), lines))


def create_folder_for_file(filepath_including_filename: str):
    # warning: todo: I'm not sure if this correctly handles absolute paths.
    filepath_including_filename = filepath_including_filename.replace("\\", "/")
    filepath = "/".join(filepath_including_filename.split("/")[:-1])
    Path(filepath).mkdir(parents=True, exist_ok=True)

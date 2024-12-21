import re
import requests
import os
from pathlib import Path


def check_folder(directory, category):
    category_list = ["targets", "metadata"]
    file_list = []

    if category not in category_list:
        print("Invalid category. Use 'metadata' or 'targets'.")
        return

    if category == "metadata":
        directory_path = Path(directory)
        for filename in os.listdir(directory_path):
            f = os.path.join(directory_path, filename)
            if os.path.isfile(f):
                file_list.append(f)
        return file_list

    if category == "targets":
        directory_path = Path(directory)
        for filename in os.listdir(directory_path):
            f = os.path.join(directory_path, filename)
            file_list.append(f)
        return file_list


def upload( directory, category, version_no):
    file_list = check_folder(directory, category)
    url = "https://tuf-server-y43f.onrender.com/upload"
    version_number = version_no
    pattern = r"\\(\d+)\."

    for file_path in file_list:


        # Extract integer from the file name using regex
        match = re.search(pattern, file_path)
        if match:
            extracted_integer = int(match.group(1))

            if extracted_integer == version_number:
                with open(file_path, "rb") as file:
                    file = {"file": file}
                    payload = {"category":category }
                    res = requests.post(url=url, files=file, data=payload)
                    print(res.text)
        else:
            with open(file_path, "rb") as file:
                file = {"file": file}
                payload = {"category":category }
                res = requests.post(url=url, files=file, data=payload)
                print(res.text)

directory = "targets"
category = "targets"
version_no = 2
upload(directory, category, version_no)
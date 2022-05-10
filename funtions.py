
from basic import toascii, get_url_validater
import re
from error import invalid_url, file_not_found, cant_create_file,file_already_exists
import random
import string
import os


def get_random_string():
    include_letters = string.ascii_lowercase
    return "".join(random.choice(include_letters) for _ in range(7))


def isyoutue(url: str):
    return 1 if url.split("/")[2].split(".")[1] == "googlevideo" else 0


def get_filename(url: str, filename: str = "") -> str:
    # get last text as filename
    if filename == None:
        filename = url.split("?")[0]

        filename = filename.split("/")[-1]

        # filter non ascii char and select only the max filename lenght
        filename = toascii(filename)[0:249]

        if filename == "":
            filename = get_random_string()

    return filename + ".downloading"


def check_url(url: str) -> None:
    if re.match(get_url_validater(), url) is None:
        invalid_url(url)


def realease_file(filename_path: str) -> None:
    if os.path.exists(filename_path):
        real_file_path = os.path.splitext(filename_path)[0]
        if os.path.exists(real_file_path):
            os.remove(real_file_path)
        os.rename(filename_path, real_file_path)
    else:
        file_not_found(filename_path)


def filename_bypassing(filename: str, inc: int = 0, trys: int = 2) -> str:
    temp = os.path.join(
        os.path.dirname(filename), (str(inc) + os.path.basename(filename))
    )

    if os.path.exists(temp):

        if trys <= 2:
            filename = filename_bypassing(filename, inc + 1, trys)
        else:
            cant_create_file(filename)
    else:
        filename = temp
    return filename


def create_file(temp_file_path: str) -> None:

    if os.path.exists(os.path.splitext(temp_file_path)[0]):
        file_already_exists(temp_file_path)

    full_temp_path = os.path.abspath(temp_file_path)
    if not os.path.exists(full_temp_path):
        if not os.path.exists(os.path.dirname(full_temp_path)):
            os.makedirs(os.path.dirname(full_temp_path))





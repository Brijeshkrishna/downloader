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


def realease_file(filename: str) -> None:
    if os.path.exists(filename):

        if os.path.exists(filename[0:-12]):
            file_already_exists(filename[0:-12])
        else:
            os.rename(filename, filename[0:-12])
        
    else:
        file_not_found(filename)


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


def create_file(filename_path: str) -> str:
    full_filename_path = os.path.abspath(filename_path)
    if not os.path.exists(full_filename_path):
        if not os.path.exists(os.path.dirname(full_filename_path)):
            os.makedirs(os.path.dirname(full_filename_path))

        with open(full_filename_path,"w"):
            pass





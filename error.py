



def invalid_url(url):
    raise Exception(f"Invaild url: {url}")


def file_not_found(filename):
    raise Exception(f"File not found: {filename}")

def cant_create_file(filename):
    raise Exception(f"Cannot create file: {filename} (MAX trys)")


def file_is_corecpted(filename):
    raise Exception(f"{filename} is edited corecpted file (delete the file and run)")


def file_already_exists(filename):
    raise Exception(f"{filename} file already exists")
# # class invalid_url(Exception):
# #     def __init__(self,url):
# #         self.url =url
# #     def __str__(self):
# from rich.console import Console
# console = Console()


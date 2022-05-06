import time
from funtions import *
from typing import Dict, Union
import requests
import os
from rich.progress import Progress
from rich import print as rprint
import re
from basic import speedMapper, toascii
import threading
from error import *
import rich

MAX_FILENAME = 20


con = rich.console.Console()


class downloader:
    def __init__(
        self,
        url: str,
        save_as: Union[str, None] = None,
        buffer_size: int = 126976,
        fn_callback=None,
        fn_callback_argc: Dict = {},
        create_new_thread: bool = False,
        rich_progressbar_args: Dict = {"disable": False},
        requests_session: requests.Session = requests.Session(),
    ) -> None:

        self.url: str = url
        self.file_path: str = save_as
        self.callback = fn_callback
        self.buffer_size: int = buffer_size
        self.fn_callback_argc: Dict = fn_callback_argc
        self.create_new_thread: bool = create_new_thread
        self.rich_progressbar_args: Dict = rich_progressbar_args
        self.session: requests.Session = requests_session

        ######################### checking url #########################
        check_url(url)

        ###################### get the file path #######################
        self.file_path = get_filename(self.url, self.file_path)

        ################get size of partially downloaded file ##########
        self.intial_size: int = self.getFileSize(self.file_path)

        ########### get the total size of downloading file #############
        self.total_size: int = self.getTotalsize(session=self.session, url=self.url)

        self.remaining_size: int = self.total_size - self.intial_size

    def download(self):
        if self.create_new_thread:
            self.new_thread = threading.Thread(target=self.start_downlaod)
            self.new_thread.start()
        else:
            self.start_downlaod()

    def __child_download(self):

        endbyte: int = self.buffer_size - 1 + self.intial_size
        startbyte: int = self.intial_size
        downloaded_size: int = self.intial_size
        start_time: float

        with Progress(**self.rich_progressbar_args) as progress:

            with open(self.file_path, "ab") as file:

                task1 = progress.add_task(
                    "[green]Downloading...",
                    total=self.total_size,
                    completed=self.intial_size,
                )

                while startbyte <= self.total_size:
                    start_time = time.perf_counter_ns()

                    rv = self.session.get(
                        self.url,
                        stream=True,
                        allow_redirects=True,
                        headers={"Range": f"bytes={startbyte}-{endbyte}"},
                    )

                    downloaded_size += self.buffer_size

                    file.write(rv.content)

                    startbyte = endbyte + 1
                    endbyte += self.buffer_size

                    cur_speed = (
                        self.buffer_size * (time.perf_counter_ns() - start_time) / 1e9
                    )

                    progress.update(
                        task1,
                        advance=self.buffer_size,
                        description=f"[blue]Speed [green bold]{speedMapper(cur_speed)}/s [red]Downloading[green] .... \n      downloaded [{speedMapper(downloaded_size)}]",
                    )
                    if not self.callback == None:
                        self.callback(cur_speed, **self.fn_callback_argc)

    def start_downlaod(self):

        create_file(self.file_path)

        if self.total_size == -1:
            print(-1)
            with open(self.fileName, "wb") as file:
                file.write(self.session.get(self.url).content)

        print(self.intial_size, self.total_size)

        if self.intial_size > self.total_size:
            file_is_corecpted(self.file_path)

        if self.remaining_size != 0:
            self.__child_download()

        realease_file(self.file_path)

    def create_dir(self):

        if not self.isexist_fileName:
            file_dir = os.path.dirname(self.fileName)
            if not os.path.exists(file_dir):
                # os.makedirs(file_dir)
                pass
        if not self.isexist_tempfile:
            file_dir = os.path.dirname(self.tempfile)
            print(self.tempfile)
            if os.path.exists(file_dir):
                print(file_dir)
                os.makedirs(file_dir)

    @staticmethod
    def gettempfile(url):

        # get last text as filename
        filename: str = url.split("?")[-1]
        filename = filename.split("/")[-1]

        # filter non ascii char and select only the max filename lenght
        filename = toascii(filename)[0:MAX_FILENAME]

        return filename + ".downloading"

    @staticmethod
    def getFileSize(file: str) -> int:
        if os.path.exists(file):
            return os.path.getsize(file)
        else:
            return 0

    @staticmethod
    def getTotalsize(session: requests.Session, url: str) -> int:
        try:
            data = session.get(
                url,
                stream=True,
                allow_redirects=True,
                headers={"Range": "bytes=0-0"},
            ).headers.get("Content-Range")
        except AttributeError:
            if data is None:
                return -1
        else:
            return int(data.split("/")[-1])


s = time.perf_counter_ns()
r = downloader("https://www.python.org/ftp/python/3.10.4/Python-3.10.4.tar.xz")
r.start_downlaod()


print((time.perf_counter_ns() - s) * 1e-9)

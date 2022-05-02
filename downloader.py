"""
MIT License

Copyright (c) 2022 Brijesh Krishna

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import time
from typing import Dict, Union
import requests
import os
from rich.progress import Progress
from rich import print as rprint
import re
from .basic import speedMapper, toascii
import threading

MAX_FILENAME = 20


class downloader:
    def __init__(
        self,
        url: str,
        save_as: Union[str, None] = None,
        tempfile: Union[str, None] = None,
        buffer_size: int = 126976,
        fn_callback=None,
        fn_callback_argc: Dict = {},
        create_new_thread: bool = False,
        rich_progressbar_args: Dict = {"disable": False},
        requests_session : requests.Session = requests.Session() 
    
    ) -> None:

        self.url: str
        self.tempfile: str
        self.fileName: str
        self.callback = fn_callback
        self.buffer_size: int = buffer_size
        self.fn_callback_argc: Dict = fn_callback_argc
        self.create_new_thread :bool= create_new_thread
        self.rich_progressbar_args :Dict= rich_progressbar_args
        self.session: requests.Session = requests_session

        ######################### checking url #########################
        if self.isUrl(url):
            self.url = url
        else:
            raise Exception("Invaild URL")
        ################################################################
        
        ##################### get the downloading file name ############
        self.tempfile = (
            self.gettempfile(url) if tempfile is None else os.path.realpath(tempfile)
        )
        ################################################################

        ###################### get the file name #######################
        self.fileName = (
            self.tempfile[0:-12] if save_as is None else os.path.realpath(save_as)
        )
        ################################################################

        ################get size of partially downloaded file ##########
        self.intial_size: int = self.getFileSize(self.tempfile)

        ################################################################

        ########### get the total size of downloading file #############
        self.total_size: int = self.getTotalsize(session=self.session, url=self.url)

        ################################################################

        self.downloadableSize: int = self.total_size - self.intial_size

        # is fileName exists
        self.isexist_fileName = os.path.exists(self.fileName)

        # is tempfile exists
        self.isexist_tempfile = os.path.exists(self.tempfile)

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
        headers: dict
        counter: int

        with Progress(**self.rich_progressbar_args) as progress:
            with open(self.tempfile, "ab") as file:
                task = progress.add_task(
                    "[red]Downloading...",
                    total=self.total_size,
                    completed=self.intial_size,
                )

                while startbyte <= self.total_size:
                    counter = time.perf_counter_ns()

                    headers = {"Range": f"bytes={startbyte}-{endbyte}"}

                    r = self.session.get(
                        self.url, stream=True, allow_redirects=True, headers=headers
                    )

                    downloaded_size += self.buffer_size

                    file.write(r.content)

                    startbyte = endbyte + 1
                    endbyte += self.buffer_size

                    cur_speed = (
                        self.buffer_size * (time.perf_counter_ns() - counter) / 1e9
                    )

                    progress.update(
                        task,
                        advance=self.buffer_size,
                        description=f"[blue]Speed [green bold]{speedMapper(cur_speed)}/s [red]Downloading[green] .... \n      downloaded [{speedMapper(downloaded_size)}]",
                    )
                    if not self.callback == None:
                        self.callback(cur_speed, **self.fn_callback_argc)

    

    def start_downlaod(self):

        self.create_dir()

        if self.total_size == -1:
            if not self.isexist_fileName:
                with open(self.fileName, "wb") as file:
                    file.write(self.session.get(self.url).content)
            else:
                rprint("another file exists")

        try:

            # file already exist
            if self.intial_size > self.total_size:
                rprint(
                    f"{self.tempfile} is edited corecpted file (delete the file and run)"
                )

            else:

                if not self.isexist_fileName:

                    self.__child_download()
                    if not self.isexist_fileName:
                        os.rename(self.tempfile, self.fileName)
                    else:
                        rprint(
                            "File already exist (you can delete the file *.downloading)"
                        )

                else:

                    if self.getFileSize(self.fileName) == self.total_size:
                        rprint(
                            "File already exist (you can delete the file *.downloading)"
                        )
                    else:
                        rprint("another file exists")

        except KeyboardInterrupt:
            pass
        except Exception as e:
            raise (e)

    def create_dir(self):

        if not self.isexist_fileName:
            file_dir = os.path.dirname(self.fileName)
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)

        if not self.isexist_tempfile:
            file_dir = os.path.dirname(self.tempfile)
            print(self.tempfile)
            if os.path.exists(file_dir):
                print(file_dir)
                os.makedirs(file_dir)

    @staticmethod
    def gettempfile(url):

        # get last text as filename
        filename: str = url.split("/")[-1]

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
            return -1

        if data is None:
            return -1
        else:
            return int(data.split("/")[-1])


    @staticmethod
    def isUrl(url: str) -> bool:
        regex = re.compile(
            r"^(?:http|ftp)s?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        if re.match(regex, url) is not None:
            return True
        return False

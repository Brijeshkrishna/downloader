import time
from funtions import check_url, get_filename, create_file, realease_file
from typing import Dict, Optional
import requests
import os
from rich.progress import Progress
from basic import speedMapper
from error import file_is_corecpted


MAX_FILENAME = 20


class downloader:
    def __init__(
        self,
        url: str,
        save_as: Optional[str] = None,
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

        endbyte: int = self.buffer_size - 1 + self.intial_size
        startbyte: int = self.intial_size
        downloaded_size: int = self.intial_size
        start_time: float

        with Progress(**self.rich_progressbar_args) as progress:
            with open(self.file_path, "ab") as file:

                task1 = progress.add_task(
                    "[green]Download started",
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
                    cur_speed = self.buffer_size / ((time.perf_counter_ns() - start_time) / 1e9)

                    downloaded_size += self.buffer_size

                    file.write(rv.content)

                    startbyte = endbyte + 1
                    endbyte += self.buffer_size

                    

                    progress.update(
                        task1,
                        advance=self.buffer_size,
                        description="[green]{} [green bold]Speed {:0.2f}MB/s[blue]\n[red]❰[blue bold]{:,} [red]/[blue bold] {:,}[red]❱".format(self.file_path,cur_speed/1045504,downloaded_size,self.total_size),
                    )
                    if self.callback != None:
                        self.callback(cur_speed, **self.fn_callback_argc)

    def start_downlaod(self):

        create_file(self.file_path)

        if self.total_size == -1:
            print(-1)
            with open(self.fileName, "wb") as file:
                file.write(self.session.get(self.url).content)

        if self.intial_size > self.total_size:
            file_is_corecpted(self.file_path)

        if self.remaining_size != 0:
            try:
                self.download()
            except KeyboardInterrupt:
                pass

        self.intial_size: int = self.getFileSize(self.file_path)
        if self.intial_size == self.total_size:
            realease_file(self.file_path)

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

            return int(data.split("/")[-1])

        except AttributeError:
            if data is None:
                return -1



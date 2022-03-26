import time
from typing import Union
import requests
import os
from rich.progress import Progress
from rich import print as rprint
import re


regex = re.compile(
    r"^(?:http|ftp)s?://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


class downloader:
    def __init__(
        self,
        url: str,
        maxSpeed: int = 126976,
        fileName: Union[str, None] = None,
        downloadingFileName: Union[str, None] = None,
    ) -> None:
        self.url: str
        self.downloadingFileName: str
        self.fileName: str

        if re.match(regex, url) is not None:
            self.url = url
        else:
            raise Exception("invalid url")

        self.maxSpeed: int = maxSpeed

        if downloadingFileName is None:
            self.downloadingFileName = self.getFileName(url)
        else:
            self.downloadingFileName = downloadingFileName

        if fileName is None:
            self.fileName = self.downloadingFileName[0:-12]
        else:
            self.fileName = fileName

        if self.downloadingFileName.__len__() >= 10:
            self.downloadingFileName =self.downloadingFileName[-15:]
        if self.fileName.__len__() >= 10:
            self.fileName = self.fileName[-15:]

        self.session: requests.Session = requests.Session()
        self.intial_size: int = self.getFileData(self.downloadingFileName)
        self.requestsSend: int = 0
        self.total_size: int = self.getTotalsize(session=self.session, url=self.url)
        self.downloadableSize: int = self.total_size - self.intial_size

    def __child_download(self):
        endbyte: int = self.maxSpeed - 1 + self.intial_size
        startbyte: int = self.intial_size
        downloadedData: int = 0
        headersList: dict
        counter: int
        with Progress() as progress:
            with open(self.downloadingFileName, "ab") as file:
                task1 = progress.add_task(
                    "[red]Downloading...",
                    total=self.total_size,
                    completed=self.intial_size,
                )
                while startbyte <= self.total_size:
                    counter = time.perf_counter_ns()

                    headersList = {"Range": f"bytes={startbyte}-{endbyte}"}

                    r = self.session.get(
                        self.url, stream=True, allow_redirects=True, headers=headersList
                    )
                    self.requestsSend += 1
                    downloadedData += self.maxSpeed
                    file.write(r.content)

                    progress.update(
                        task1,
                        advance=self.maxSpeed,
                        description=f"[blue]Speed [green bold]{str(self.maxSpeed*( time.perf_counter_ns() - counter)/ 1e9)[0:7]} Bytes/s [red]Downloading[green] ....",
                    )

                    startbyte = endbyte + 1
                    endbyte += self.maxSpeed

    def downlaod(self):
        try:
            if self.total_size == -1:
                if not os.path.exists(self.fileName):
                    rprint("Downloading cant't be canceled")
                    with open(self.fileName, "wb") as file:
                        file.write(self.session.get(self.url).content)

            else:
                if self.intial_size > self.total_size:
                    rprint(
                        f"{self.downloadingFileName} is edited corecpted file (delete the file and run)"
                    )
                    exit(1)

                else:

                    if (
                        os.path.exists(self.fileName)
                        and self.getFileData(self.fileName) == self.total_size
                    ):
                        rprint(
                            "File already exist (you can delete the file *.downloading)"
                        )

                    elif (
                        os.path.exists(self.fileName)
                        and self.getFileData(self.fileName) != self.total_size
                    ):
                        self.__child_download()
                        rprint(f"Total sent requets =>[green bold] {self.requestsSend}")
                        while os.path.exists(self.fileName):
                            self.fileName = os.path.splitext(self.fileName)
                            self.fileName = self.fileName[0] + str(0) + self.fileName[1]
                        os.rename(self.downloadingFileName, self.fileName)

                    elif not os.path.exists(self.fileName):
                        self.__child_download()
                        os.rename(self.downloadingFileName, self.fileName)
                        rprint(f"Total sent requets =>[green bold] {self.requestsSend}")
        except KeyboardInterrupt:
            pass
        except Exception as e:
            raise (e)

    @staticmethod
    def getFileName(url):
        return url.split("/")[-1] + ".downloading"

    @staticmethod
    def getFileData(file: str) -> int:
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
            if data is None:
                return -1
            else:
                return int(data.split("/")[-1])

        except AttributeError:
            return -1

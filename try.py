# """
# MIT License

# Copyright (c) 2022 Brijesh Krishna

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# """

# import time
# from typing import Dict, Union
# import requests
# import os
# from rich.progress import Progress
# from rich import print as rprint
# import re
# from basic import speedMapper, toascii
# import threading

# MAX_FILENAME = 20


# class downloader:
#     def __init__(
#         self,
#         url: str,
#         save_as: Union[str, None] = None,
#         buffer_size: int = 126976,
#         fn_callback=None,
#         fn_callback_argc: Dict = {},
#         create_new_thread: bool = False,
#         rich_progressbar_args: Dict = {"disable": False},
#         requests_session : requests.Session = requests.Session()

#     ) -> None:

#         self.url: str
#         self.fileName: str
#         self.callback = fn_callback
#         self.buffer_size: int = buffer_size
#         self.fn_callback_argc: Dict = fn_callback_argc
#         self.create_new_thread :bool= create_new_thread
#         self.rich_progressbar_args :Dict= rich_progressbar_args
#         self.session: requests.Session = requests_session

#         ######################### checking url #########################
#         if self.isUrl(url):
#             self.url = url
#         else:
#             raise Exception("Invaild URL")
#         ################################################################

#         ##################### get the downloading file name ############
#         self.tempfile = (
#             self.gettempfile(url) if tempfile is None else os.path.realpath(tempfile)
#         )
#         ################################################################

#         ###################### get the file name #######################
#         self.fileName = (
#             self.tempfile[0:-12] if save_as is None else os.path.realpath(save_as)
#         )
#         ################################################################

#         ################get size of partially downloaded file ##########
#         self.intial_size: int = self.getFileSize(self.tempfile)

#         ################################################################

#         ########### get the total size of downloading file #############
#         self.total_size: int = self.getTotalsize(session=self.session, url=self.url)

#         ################################################################

#         self.downloadableSize: int = self.total_size - self.intial_size

#         # is fileName exists
#         self.isexist_fileName = os.path.exists(self.fileName)

#         # is tempfile exists
#         self.isexist_tempfile = os.path.exists(self.tempfile)

#     def download(self):
#         if self.create_new_thread:
#             self.new_thread = threading.Thread(target=self.start_downlaod)
#             self.new_thread.start()
#         else:
#             self.start_downlaod()

#     def __child_download(self):

#         endbyte: int = self.buffer_size - 1 + self.intial_size
#         startbyte: int = self.intial_size
#         downloaded_size: int = self.intial_size
#         headers: dict
#         counter: int

#         with Progress(**self.rich_progressbar_args) as progress:
#             with open(self.tempfile, "ab") as file:
#                 task = progress.add_task(
#                     "[red]Downloading...",
#                     total=self.total_size,
#                     completed=self.intial_size,
#                 )

#                 while startbyte <= self.total_size:
#                     counter = time.perf_counter_ns()

#                     headers = {"Range": f"bytes={startbyte}-{endbyte}"}

#                     r = self.session.get(
#                         self.url, stream=True, allow_redirects=True, headers=headers
#                     )

#                     downloaded_size += self.buffer_size

#                     file.write(r.content)

#                     startbyte = endbyte + 1
#                     endbyte += self.buffer_size

#                     cur_speed = (
#                         self.buffer_size * (time.perf_counter_ns() - counter) / 1e9
#                     )

#                     progress.update(
#                         task,
#                         advance=self.buffer_size,
#                         description=f"[blue]Speed [green bold]{speedMapper(cur_speed)}/s [red]Downloading[green] .... \n      downloaded [{speedMapper(downloaded_size)}]",
#                     )
#                     if not self.callback == None:
#                         self.callback(cur_speed, **self.fn_callback_argc)


#     def start_downlaod(self):

#         self.create_dir()

#         if self.total_size == -1:
#             if not self.isexist_fileName:
#                 with open(self.fileName, "wb") as file:
#                     print()
#                     file.write(self.session.get(self.url).content)

#             else:
#                 rprint("another file exists")

#         try:

#             # file already exist
#             if self.intial_size > self.total_size:
#                 rprint(
#                     f"{self.tempfile} is edited corecpted file (delete the file and run)"
#                 )

#             else:

#                 if not self.isexist_fileName:

#                     self.__child_download()
#                     if not self.isexist_fileName:
#                         os.rename(self.tempfile, self.fileName)
#                     else:
#                         rprint(
#                             "File already exist (you can delete the file *.downloading)"
#                         )

#                 else:

#                     if self.getFileSize(self.fileName) == self.total_size:
#                         rprint(
#                             "File already exist (you can delete the file *.downloading)"
#                         )
#                     else:
#                         rprint("another file exists")

#         except KeyboardInterrupt:
#             pass
#         except Exception as e:
#             raise (e)

#     def create_dir(self):

#         if not self.isexist_fileName:
#             file_dir = os.path.dirname(self.fileName)
#             if not os.path.exists(file_dir):
#                 #os.makedirs(file_dir)
#                 pass
#         if not self.isexist_tempfile:
#             file_dir = os.path.dirname(self.tempfile)
#             print(self.tempfile)
#             if os.path.exists(file_dir):
#                 print(file_dir)
#                 os.makedirs(file_dir)

#     @staticmethod
#     def gettempfile(url):

#         # get last text as filename
#         filename: str = url.split("?")[-1]
#         filename = filename.split("/")[-1]

#         # filter non ascii char and select only the max filename lenght
#         filename = toascii(filename)[0:MAX_FILENAME]

#         return filename + ".downloading"

#     @staticmethod
#     def getFileSize(file: str) -> int:
#         if os.path.exists(file):
#             return os.path.getsize(file)
#         else:
#             return 0

#     @staticmethod
#     def getTotalsize(session: requests.Session, url: str) -> int:

#         try:
#             data = session.get(
#                 url,
#                 stream=True,
#                 allow_redirects=True,
#                 headers={"Range": "bytes=0-0"},
#             ).headers.get("Content-Range")

#         except AttributeError:
#             return -1

#         if data is None:
#             return -1
#         else:
#             return int(data.split("/")[-1])


# def main():
#     import cProfile
#     import pstats

#     with cProfile.Profile() as pr:

#         r = downloader("https://www.keil.com/fid/wkg2g3wdb3mj1wy3oow19rytewxyr1a91vmud1/files/eval/c251v560.exe")
#         r.start_downlaod()

#     # staus = pstats.Stats(pr)
#     # staus.sort_stats(pstats.SortKey.TIME)
#     # staus.print_stats()
#     # staus.dump_stats("dow.prof")


# main()


import asyncio
import aiohttp
import os
import cProfile
import pstats
import aiofiles



class gen_ranges:
    def __init__(self, buffer_size, from_size, to_size):
        self.start = from_size
        self.end = from_size + buffer_size
        self.buffer_size = buffer_size
        self.first_loop = 1
        self.to_size = to_size
        if self.end > self.to_size:
            self.end = self.to_size

    def __iter__(self):
        return self

    def __next__(self):
        if self.first_loop:
            self.first_loop = 0
            return {"Range": f"bytes={self.start}-{self.end}"}

        self.start = self.end + 1
        self.end = self.end + self.buffer_size

        if self.start >= self.to_size:
            raise StopIteration

        if self.end > self.to_size:
            self.end = self.to_size

        return {"Range": f"bytes={self.start}-{self.end}"}


URL = "https://download-cdn.jetbrains.com/resharper/dotUltimate.2022.1.1/JetBrains.ReSharper.CommandLineTools.2022.1.1.zip"


def createfile(filename):
    pwd = os.getcwd()
    os.chdir("./temp")
    files = os.listdir(".")
    files.sort()
    cmd = "cat "
    for i in files:
        cmd += i + " "
    cmd = cmd + ">> " + filename
    os.system(cmd)
    os.chdir(pwd)





def getfile(h):
    h = str(h).split("=")[1].replace("'}", "").split("-")
    return f"{h[0]}_{h[1]}"


async def fetch(session: aiohttp.ClientSession, headers,id):
    for header in headers:
        async with session.get(URL,headers=header) as response:
            await response.read()
            print(header,id)


async def main(headers):
    tasks=[]
    async with aiohttp.ClientSession() as session:
            for i in range(4):
                tasks.append(fetch(session, headers,i))
            await asyncio.gather(*tasks)


def run(headers):
    asyncio.run(main(headers))


# headers = gen_ranges(1269760, 0, 111503590)
# run(headers)

def asyncDownloader():
    pass
    

# with cProfile.Profile() as pr:


# staus = pstats.Stats(pr)
# staus.sort_stats(pstats.SortKey.TIME)
# staus.print_stats()
# staus.dump_stats("dow.prof")
# #createfile("datagrip-2022.1.3.tar.gz")


with open("dow.prof","w") as f:
    f.seek(0,5)

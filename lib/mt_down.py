# encoding:utf-8
import time
from pathlib import Path
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, wait
import requests
import re

ILLEGAL_NAMES = re.compile(r'[\\/:*?\"<>| \.,，。、？：‘’“”、【】！￥\!\@\#\$\%\^\&\*\(\)]')


def make_valid_name(name: str) -> str:
    if len(name) > 50:
        name = name[:50]
    return ILLEGAL_NAMES.sub('', name)


class MultiDownloader:
    def __init__(self, links, download_path, threads=10, headers=None):
        """
        Download multiple files at once.
        the following arguments are required:

        - import time
        - from pathlib import Path
        - from threading import Lock
        - from concurrent.futures import ThreadPoolExecutor, wait
        - import requests

        :param links: the list of links to download
        :param download_path: where to save the files
        :param threads: how many threads to use
        """
        self.links = links
        self.download_path = download_path
        if not Path(download_path).exists():
            Path(download_path).mkdir(parents=True)
        self.threads = threads
        self.headers = headers

        self.lock = Lock()
        self.total = len(links)
        self.downloaded = 0
        self.errors = 0
        self.skip = 0
        self.retry = 0
        self.failed = []

        self.begin_time = 0.0

    def __clear_download(self):
        self.downloaded = 0
        self.errors = 0
        self.skip = 0
        self.retry = 0
        self.failed = []
        self.total = len(self.links)

    def __add_success(self):
        with self.lock:
            self.downloaded += 1

    def __add_error(self, failed_link=None):
        with self.lock:
            self.downloaded += 1
            self.errors += 1
            if failed_link:
                self.failed.append(failed_link)

    def __add_skip(self):
        with self.lock:
            self.downloaded += 1
            self.skip += 1

    def __add_retry(self):
        with self.lock:
            self.retry += 1

    def __handle(self, link):
        filep = Path(self.download_path) / Path(link).name
        if filep.exists():
            self.__add_skip()
            return
        for i in range(3):
            try:
                if self.headers:
                    r = requests.get(link, headers=self.headers, timeout=5)
                else:
                    r = requests.get(link, timeout=5)
                with self.lock:
                    with open(filep, 'wb') as f:
                        f.write(r.content)
                self.__add_success()
                break
            except Exception as e:
                if i < 2:
                    self.__add_retry()
                else:
                    print(e)
                    self.__add_error(link)

        progress = (f'下载进度 {self.downloaded}/{self.total} '
                    f'@ {self.downloaded * 100 // self.total}%')
        status = (f'| 总计 {self.downloaded} '
                  f'| 重试 {self.retry} '
                  f'| 错误 {self.errors} '
                  f'| 跳过 {self.skip} |')
        eta = (self.total - self.downloaded) / (self.downloaded / (time.time() - self.begin_time))

        eta = f'剩余 {int(eta % 3600 // 60)}分{int(eta % 60)}秒'

        print(f'\r{progress} {status} {eta}      ', end='')

    def thread_down(self):
        print(self.download_path)
        self.__clear_download()
        self.begin_time = time.time()
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            missions = []
            for link in self.links:
                missions.append(executor.submit(self.__handle, link))
            wait(missions)
        print('\n+ 下载完成：')
        print(f'| 总计: {int(time.time() - self.begin_time)}s')
        print(f'| 成功: {self.downloaded}')
        print(f'| 错误: {self.errors}')
        print(f'| 跳过: {self.skip}\n')
        if self.failed:
            print('| 失败链接:')
            for link in self.failed:
                print('+ ' + link)
        else:
            print('+ 没有失败链接')

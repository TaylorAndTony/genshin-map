import time
from typing import Callable, Iterable

import requests
from rich.console import Console
from pathlib import Path

console = Console()

headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0'
}

# class State:

#     def __init__(self):
#         self.x: int = 0
#         self.y: int = 0
#         self.zoom_level: str = 'P0'

# def save_state(state: State):
#     with open('state.json', 'w') as f:
#         json.dump(state.__dict__, f)

# def load_state() -> State:
#     try:
#         with open('state.json', 'r') as f:
#             state_dict = json.load(f)
#             state = State()
#             state.__dict__.update(state_dict)
#             return state
#     except FileNotFoundError:
#         return State()


def gen_one_link(x: int, y: int, zoom_level: str) -> str:
    # https://act-webstatic.mihoyo.com/ys-map-op/map/2/38c777262414ff6a7b3e73829d4a7ab1/91_27_P0.webp
    return f"https://act-webstatic.mihoyo.com/ys-map-op/map/2/38c777262414ff6a7b3e73829d4a7ab1/{x}_{y}_{zoom_level}.webp"


def gen_links(start_x: int, start_y: int, end_x: int, end_y: int,
              zoom_level: str) -> Iterable:
    # https://act-webstatic.mihoyo.com/ys-map-op/map/2/38c777262414ff6a7b3e73829d4a7ab1/91_27_P0.webp
    for x in range(start_x, end_x + 1):
        for y in range(start_y, end_y + 1):
            yield gen_one_link(x, y, zoom_level), x, y


def url_valid(url: str) -> bool:
    try:
        response = requests.head(url, headers=headers, timeout=3)
        console.print(url, response.status_code)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False
    except Exception:
        return False


def find_max_existing_number(exists_func: Callable[[int], bool],
                             sleep_time: float = 0.5) -> int:
    """
    使用二分法查找最大的数字N，使得0到N的所有数字都存在
    
    参数:
        exists_func: 一个函数，接受一个数字，返回该数字是否存在（布尔值）
                     如果返回True，意味着从0到该数字的所有数字都存在
    
    返回:
        最大的数字N，使得0到N的所有数字都存在
    """
    # 处理特殊情况：0是否存在
    if not exists_func(0):
        return -1  # 连0都不存在，返回-1表示没有有效范围

    # 确定一个足够大的上限
    high = 1
    console.print(f'Finding max number up to [yellow]{high}[/yellow]')
    while exists_func(high):
        high *= 2  # 指数级增长，快速找到一个不存在的上限
        time.sleep(sleep_time)

    console.print(f'Max number up to [yellow]{high}[/yellow] found')
    # 现在已知exists_func(high)为False，exists_func(high//2)为True
    # 开始二分查找
    low = 0
    best = 0  # 记录找到的最佳结果

    while low <= high:
        mid = (low + high) // 2
        console.print(f'Testing [cyan]{mid}[/cyan]')
        if exists_func(mid):
            # 当前数字存在，尝试找更大的
            best = mid
            low = mid + 1
        else:
            # 当前数字不存在，尝试找更小的
            high = mid - 1
        time.sleep(sleep_time)
    console.print(f'Max is [bold green]{best}[/bold green]')
    return best


def find_max_x(zoom_level: str, sleep_time: float = 0.5) -> int:
    console.print('Finding max X')

    def func(x):
        return url_valid(gen_one_link(x, 0, zoom_level))

    return find_max_existing_number(func, sleep_time)


def find_max_y(zoom_level: str) -> int:
    console.print('Finding max Y')

    def func(y):
        return url_valid(gen_one_link(0, y, zoom_level))

    return find_max_existing_number(func)


def download_one_link(link: str, save_path: str | Path) -> bool:
    for i in range(3):
        try:
            response = requests.get(link, headers=headers, timeout=3)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True
        except requests.exceptions.RequestException:
            pass
        except Exception:
            pass
    return False


def get_filename(link):
    return Path('download') / Path(link).name


def readable_bytes(size: float | int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}PB"


def readable_time(seconds: int | float) -> str:
    """
    Convert seconds to a human-readable time format.
    
    Args:
        seconds: The number of seconds to convert.
    
    Returns:
        A string representing the time in the format "HH:MM:SS".
    """
    hours = int(seconds // 3600)  # Convert to int
    minutes = int((seconds % 3600) // 60)  # Convert to int
    seconds = int(seconds % 60)  # Convert to int
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def batch_craw(end_x: int,
               end_y: int,
               zoom_level: str,
               sleep_time: float = 0.5):
    # state = load_state()
    # start_x = state.x
    # start_y = state.y
    # state.zoom_level = zoom_level
    console.print(
        f'Crawling from 0 to {end_x}, 0 to {end_y}, zoom level {zoom_level}')
    # skipped = 0
    # for link, x, y in gen_links(0, 0, end_x, end_y, zoom_level):
    #     filename = get_filename(link)
    #     if not filename.exists():
    #         if skipped != 0:
    #             console.print(f'  Skipped {skipped} files from last download')
    #             skipped = 0
    #         console.print(f'  Downloading {link}\n  to {filename}')
    #         download_one_link(link, str(filename))
    #         time.sleep(sleep_time)
    #     else:
    #         skipped += 1
    #     # state.x = x
    #     # state.y = y
    #     # save_state(state)
    with console.status('Finding exsisting files...'):
        link_group = list(gen_links(0, 0, end_x, end_y, zoom_level))
        links = [link for link, _, _ in link_group]
        filtered = [link for link in links if not get_filename(link).exists()]
    console.print(
        f'{len(filtered)} files to download, skipping {len(links) - len(filtered)} files'
    )
    ask = console.input('Start downloading? (Y/n) ')
    if ask.lower() not in ('', 'y', 'yes'):
        console.print('Aborted')
        return
    time_begin = time.monotonic()
    for idx, link in enumerate(filtered):
        filename = get_filename(link)
        msg = f'({idx+1} / {len(filtered)}) Downloading {link}\n  - to {filename}'
        console.print(msg)
        download_one_link(link, str(filename))
        time.sleep(sleep_time)
        time_passed = time.monotonic() - time_begin
        speed = (idx + 1) / time_passed
        eta = (len(filtered) - idx) / speed
        console.print(f'  - Speed: {speed:.2f} files/s\n  - ETA: {readable_time(eta)}s')

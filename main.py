import lib
from lib.mt_down import MultiDownloader

from rich.console import Console
import typer

from pathlib import Path

console = Console()
app = typer.Typer()

MAX_X = 143
MAX_Y = 71
MODE = 'P0'


@app.command('val')
def validate(
    to_x: int = typer.Argument(MAX_X, help=f'Max X (default {MAX_X})'),
    to_y: int = typer.Argument(MAX_Y, help=f'Max Y (default {MAX_Y})'),
    zoom: str = typer.Option(
        MODE, help=f'Map mode, N3 N2 N1 or P0 (default {MODE})'),
):
    """
    Validate downloaded files.

    Under ./download, there should be 0_0_P0.webp, 0_1_P0.webp, ...
    """
    not_exist = []
    for x in range(to_x+1):
        for y in range(to_y+1):
            name = f'./download/{x}_{y}_{zoom}.webp'
            if not Path(name).exists():
                not_exist.append(name)
    if not_exist:
        console.print(f'Some files are missing: {len(not_exist)}')
        # for name in not_exist:
            # console.print(name)
        with open('./missing.txt', 'w', encoding='utf-8') as f:
            for name in not_exist:
                f.write(name + '\n')
        console.print('Saved missing files to [cyan]missing.txt[/]')
        return False
    console.print('[bold green]All files exist[/bold green]')        
    return True


@app.command('probe')
def probe_xy(mode: str = typer.Option(
    MODE, help='Map mode, N3 N2 N1 or P0 (default)')):
    """
    Test max x and y tiles.
    """
    x = lib.find_max_x(mode)
    y = lib.find_max_y(mode)
    console.print(f'Max X: {x}, Max Y: {y}')


@app.command('batch')
def batch(x: int = typer.Argument(MAX_X, help=f'Max X (default {MAX_X})'),
          y: int = typer.Argument(MAX_Y, help=f'Max Y (default {MAX_Y})'),
          zoom: str = typer.Option(
              MODE, help=f'Map mode, N3 N2 N1 or P0 (default {MODE})'),
          sleep: float = typer.Option(
              0.5, help='Sleep time between requests (default 0.5)'),
          threads: int = typer.Option(
              -1, help='Number of threads (-1 = single thread)')):
    """
    Batch download tiles. from 0 to x and 0 to y with zoom level.
    
    Automatically skip existing files.
    """
    if threads < 2:
        lib.batch_craw(x, y, zoom, sleep_time=sleep)
    else:
        links = lib.get_to_down_file_list(x, y, zoom)
        ask = console.input(f'Start downloading with {threads} threads? (Y/n) ')
        if ask.lower() not in ('', 'y', 'yes'):
            console.print('Aborted')
            return
        d = MultiDownloader(links, './download', threads, lib.headers)
        d.thread_down()


@app.command('down')
def download_one(
    x: int = typer.Argument(0, help='X tile number'),
    y: int = typer.Argument(0, help='Y tile number'),
    zoom: str = typer.Option(
        MODE, help=f'Map mode, N3 N2 N1 or P0 (default {MODE})'),
) -> None:
    """
    Download one tile. Tile at x and y with zoom level.
    """
    link = lib.gen_one_link(x, y, zoom)
    console.print(f'Downloading {link}')
    lib.download_one_link(link, lib.get_filename(link))
    console.print(f'Downloaded {link}')


if __name__ == "__main__":
    app()

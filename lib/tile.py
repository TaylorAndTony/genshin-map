from pickletools import optimize
from PIL import Image
from rich.console import Console

from pathlib import Path
import sys

console = Console()

def readable_bytes(size: float | int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}PB"


def make_full_image(max_x: int, max_y: int, zoom_level: str,
                    one_tile_size: int, output_to: str | Path, quality: int = 90):
    big_image = Image.new('RGBA', ((max_x + 1) * one_tile_size,
                                   (max_y + 1) * one_tile_size))
    try:
        with console.status('(full) [yellow]Testing file save...'):
            big_image.save(output_to, optimize=True, quality=quality)
    except OSError as e:
        console.print(f'[bold red]Error: Cannot save image to {output_to}')
        console.print(e)
        return
    console.print('(full) [yellow]Test file save successful')
    mem_use = sys.getsizeof(big_image)
    console.print(f'[cyan](full) Memory usage: {readable_bytes(mem_use)}')
    console.print(f'[cyan](full) Image size: {big_image.size}')
    for x in range(max_x + 1):
        for y in range(max_y + 1):
            img_file = f'./download/{x}_{y}_{zoom_level}.webp'
            if not Path(img_file).exists():
                console.print(f'[bold red[File not found: [/]{img_file}')
                continue
            img = Image.open(img_file)
            big_image.paste(img, (x * one_tile_size, y * one_tile_size))
            print(f'\r(full) Paste image {x} {y}    ', end='')
    console.print(f'(full) Save image to {output_to}')
    big_image.save(output_to, optimize=True, quality=quality)
    console.print('[bold green](full) Done')
    big_image.close()

"""
Imagediff
Copyright (C) 2020-2025  Greger Stolt Nilsen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import logging
from typing import List, Literal, TypedDict, Union
import click
import hashlib
from pathlib import Path
from PIL import Image
from PIL import ImageChops

logging.basicConfig(level=os.environ.get('LOGLEVEL', logging.INFO))

NEW = 0
COMMON = 1
DELETED = 2


class ImageInfo(TypedDict):
    file: Path
    status: Union[Literal[0], Literal[1], Literal[2]]


def render_diffs(files: List[ImageInfo], dira: Path, dirb: Path, output: Path = Path("output")):
    if not output.exists():
        output.mkdir(parents=True, exist_ok=True)

    for f in files:
        imga = Image.open(dira / f['file'])
        imgb = Image.open(dirb / f['file'])

        assert imga.size == imgb.size

        out = ImageChops.difference(imga, imgb)

        out.save(output / f['file'])


def file_hash(filename: Path):
    BLOCK_SIZE = 4096
    assert filename.is_file()
    file_hash = hashlib.md5()
    with open(filename, 'rb') as f:
        fb = f.read(BLOCK_SIZE)
        while(len(fb) > 0):
            file_hash.update(fb)
            fb = f.read(BLOCK_SIZE)

    return file_hash.hexdigest()


def find_images(foldername: Path):
    images: List[str] = []
    for root, folder, files in foldername.walk():
        for f in files:
            filename = Path(f)
            if filename.suffix in ('.png', '.jpeg', '.jpg', '.gif'):
                logging.debug("Appending: %s/%s", root.relative_to(foldername), filename)
                images.append(f"{root.relative_to(foldername)}/{f}")

    return images


def compare(a: Path, b: Path, render: bool = False):

    images_a = find_images(a)
    images_b = find_images(b)

    images_common = sorted(list(set(images_a).intersection(set(images_b))))

    images_new = list(set(images_a) - set(images_b))

    images_deleted = list(set(images_b) - set(images_a))

    image_list: List[ImageInfo] = []

    for image in images_common:
        image_list.append({
            'file': Path(image),
            'status': COMMON
        })

    for image in images_new:
        image_list.append({
            'file': Path(image),
            'status': NEW
        })

    for image in images_deleted:
        image_list.append({
            'file': Path(image),
            'status': DELETED
        })

    print("Found {} image(s).".format(len(image_list)))

    if render:
        render_diffs(image_list, a, b, Path('output'))

    return image_list


@click.command()
@click.argument("source", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("destination", type=click.Path(exists=True, file_okay=False, path_type=Path))
def main(source: Path, destination: Path):
    """
    Compare two folders of images, with the possibility to copy from one to the other.

    SOURCE: Source folder, these are the "new" images.

    DESTINATION: Destination folder. Images that are copied ends up here.
    """
    compare(source, destination, render=True)


if __name__ == "__main__":
    main()

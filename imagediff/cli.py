"""
Imagediff
Copyright (C) 2020  Greger Stolt Nilsen

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
import sys
import hashlib
from PIL import Image
from PIL import ImageChops

def render_diffs(files, dira, dirb, output="output"):
    if not os.path.isdir(output):
        os.makedirs(output)

    for f in files:
        imga = Image.open(os.path.join(dira, f))
        imgb = Image.open(os.path.join(dirb, f))

        assert imga.size == imgb.size

        out = ImageChops.difference(imga, imgb)

        out.save(os.path.join(output, f))

def file_hash(filename):
    BLOCK_SIZE = 4096
    assert os.path.isfile(filename)
    file_hash = hashlib.md5()
    with open(filename, 'rb') as f:
        fb = f.read(BLOCK_SIZE)
        while(len(fb) > 0):
            file_hash.update(fb)
            fb = f.read(BLOCK_SIZE)
    
    return file_hash.hexdigest()


def find_images(foldername):
    images = []
    for root, folders, files in os.walk(foldername):
        for f in files:
            if f.endswith('.png'):
                images.append(f)

    return sorted(images)


def compare(a, b, render=False):
    assert os.path.isdir(a)
    assert os.path.isdir(b)

    images_a = find_images(a)
    images_b = find_images(b)

    # Here we should check for missing images
    # ma = list(set(images_a) - set(images_b))
    # mb = list(set(images_b) - set(images_a))

    hashes_a = [file_hash(os.path.join(a, f)) for f in images_a]
    hashes_b = [file_hash(os.path.join(b, f)) for f in images_b]

    files_and_hashes = list(zip(images_a, hashes_a, hashes_b))

    changed_files = [f[0] for f in files_and_hashes if f[1] != f[2]]
    
    print("Found {} changed file(s).".format(len(changed_files)))

    if render:
        render_diffs(changed_files, a, b, 'output')
    
    return changed_files


def main():
    if len(sys.argv) < 3:
        print("Folders need to be specified")
    
    foldera, folderb = sys.argv[1:3]
    
    compare(foldera, folderb, render=True)


if __name__ == "__main__":
    main()
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
from typing import Any, List, Optional
import click
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget,
                             QVBoxLayout, QListWidget, QListWidgetItem,
                             QHBoxLayout, QGridLayout, QMainWindow,
                             QPushButton)
from PyQt5.QtGui import QPixmap, QResizeEvent
from PyQt5.QtCore import Qt, QSize
from .cli import ImageInfo, compare
from PIL import Image
from PIL.ImageQt import ImageQt
from PIL.ImageChops import difference
import shutil
import logging

logging.basicConfig(level=os.environ.get('LOGLEVEL', logging.INFO))


class ImageList(QListWidget):
    def sizeHint(self):
        logging.debug("ImageList: sizeHint()")
        s = QSize()
        s.setHeight(super(ImageList, self).sizeHint().height())
        s.setWidth(self.sizeHintForColumn(0))
        return s


class LabelImage(QLabel):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.image: Optional[QPixmap] = None
        self.image_scaled: Optional[QPixmap] = None

    def setimage(self, image: QPixmap):
        self.image = image
        self.setPixmap(image, self.size())

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        if self.image is not None:
            self.setPixmap(self.image, event.size())

    def setPixmap(self, qPixmap: QPixmap, size: QSize):
        self.image = qPixmap
        if self.image.size().width() > size.width() or self.image.size().height() > size.height():
            self.image_scaled = self.image.scaled(size, Qt.KeepAspectRatio)
        else:
            self.image_scaled = self.image.copy()
        super().setPixmap(self.image_scaled)


class Imgdiff(QMainWindow):
    def __init__(self, source: Path, destination: Path, image_list: List[ImageInfo]):
        super().__init__()
        self.initUI(image_list)
        self.source = source
        self.destination = destination
        self.selectedItem = None

    def initUI(self, image_list: List[ImageInfo]):
        widget = QWidget()

        # Main layout container
        hbox = QHBoxLayout()

        # List and buttonss sublayout
        vbox = QVBoxLayout()

        # Setup file list
        imagelist = ImageList()

        for f in image_list:
            item = QListWidgetItem(str(f['file']))
            if f['status'] == 0:
                item.setBackground(Qt.green)
            if f['status'] == 2:
                item.setBackground(Qt.red)
            imagelist.addItem(item)

        imagelist.itemClicked.connect(self.selected)
        vbox.addWidget(imagelist)
        imagelist.setMaximumWidth(imagelist.sizeHintForColumn(0) + 5)

        # Setup copy button
        copybutton = QPushButton("Copy")
        copybutton.clicked.connect(self.copy)
        vbox.addWidget(copybutton)

        hbox.addLayout(vbox, 1)

        # Setup image grid
        self.imagea = LabelImage()
        self.imagea.setAlignment(Qt.AlignCenter)
        self.imageb = LabelImage()
        self.imageb.setAlignment(Qt.AlignCenter)
        self.imagediff = LabelImage()
        self.imagediff.setAlignment(Qt.AlignCenter)
        imagegrid = QGridLayout()
        imagegrid.addWidget(self.imagea, 0, 0)
        imagegrid.addWidget(self.imageb, 0, 1)
        imagegrid.addWidget(self.imagediff, 1, 0)

        hbox.addLayout(imagegrid, 1)

        widget.setLayout(hbox)

        self.setCentralWidget(widget)
        self.setGeometry(300, 300, 640, 480)
        self.setWindowTitle("Imagediff")
        self.show()

    def selected(self, item: QListWidgetItem, *args: Any, **kwargs: Any):
        self.selectedItem = item

        self.imagea.clear()
        self.imageb.clear()
        self.imagediff.clear()

        image_source = self.source / item.text()
        image_destination = self.destination / item.text()
        logging.debug("Comparing {} and {}".format(
            image_source, image_destination))

        a: Optional[Image.Image] = None
        b: Optional[Image.Image] = None

        if image_source.is_file():
            logging.debug("Opening {}".format(image_source))
            a = Image.open(image_source)
            logging.debug("Image source: {}".format(a))
            self.imagea.setimage(QPixmap.fromImage(ImageQt(a.copy())))

        if image_destination.is_file():
            logging.debug("Opening {}".format(image_destination))
            b = Image.open(image_destination)
            logging.debug("Image destionation: {}".format(b))
            self.imageb.setimage(QPixmap.fromImage(ImageQt(b.copy())))

        if image_source.is_file() and image_destination.is_file():
            assert a and b
            logging.debug("Creating difference map")
            d = (difference(a, b)).convert("L")
            logging.debug("Converting differente map")
            pixmapdiff = QPixmap.fromImage(ImageQt(d.copy()))
            logging.debug("Setting difference map")
            self.imagediff.setimage(pixmapdiff)

    def copy(self, *args: Any, **kwargs: Any):
        if self.selectedItem is None:
            return

        source = self.source / self.selectedItem.text()
        dest = self.destination / self.selectedItem.text()

        print("Copy from {} to {}".format(source, dest))
        shutil.copyfile(source, dest)


@click.command()
@click.argument("source", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("destination", type=click.Path(exists=True, file_okay=False, path_type=Path))
def main(source: Path, destination: Path):
    """
    Compare two folders of images, with the possibility to copy from one to the other.

    SOURCE: Source folder, these are the "new" images.
    DESTINATION: Destination folder. Images that are copied ends up here.
    """

    image_list = compare(source, destination, render=False)

    app = QApplication([])
    app.setApplicationName("Imagediff")
    app.setApplicationDisplayName("Imagediff")
    _ = Imgdiff(source, destination, image_list)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

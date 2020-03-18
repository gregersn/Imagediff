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
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget,
                             QVBoxLayout, QListWidget, QListWidgetItem,
                             QHBoxLayout, QGridLayout, QMainWindow,
                             QPushButton)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize
from .cli import compare
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image: QPixmap = None
        self.image_scaled: QPixmap = None

    def setimage(self, image):
        self.image = image
        self.setPixmap(image, self.size())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.image is not None:
            self.setPixmap(self.image, event.size())

    def setPixmap(self, qPixmap, size):
        self.image = qPixmap
        if self.image.size().width() > size.width() or self.image.size().height() > size.height():
            self.image_scaled = self.image.scaled(size, Qt.KeepAspectRatio)
        else:
            self.image_scaled = self.image.copy()
        super().setPixmap(self.image_scaled)


class Imgdiff(QMainWindow):
    def __init__(self, foldera, folderb, image_list):
        super().__init__()
        self.initUI(image_list)
        self.foldera = foldera
        self.folderb = folderb
        self.selectedItem = None

    def initUI(self, image_list):
        widget = QWidget()

        # Main layout container
        hbox = QHBoxLayout()

        # List and buttonss sublayout
        vbox = QVBoxLayout()

        # Setup file list
        imagelist = ImageList()

        for f in image_list:
            item = QListWidgetItem(f['file'])
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

    def selected(self, item: QListWidgetItem, *args, **kwargs):
        self.selectedItem = item

        self.imagea.clear()
        self.imageb.clear()
        self.imagediff.clear()

        imagea = os.path.join(self.foldera, item.text())
        imageb = os.path.join(self.folderb, item.text())
        logging.debug("Comparing {} and {}".format(imagea, imageb))

        if os.path.isfile(imagea):
            logging.debug("Opening {}".format(imagea))
            a = Image.open(imagea)
            logging.debug("Image A: {}".format(a))
            self.imagea.setimage(QPixmap.fromImage(ImageQt(a.copy())))

        if os.path.isfile(imageb):
            logging.debug("Opening {}".format(imageb))
            b = Image.open(imageb)
            logging.debug("Image B: {}".format(b))
            self.imageb.setimage(QPixmap.fromImage(ImageQt(b.copy())))

        if os.path.isfile(imagea) and os.path.isfile(imageb):
            logging.debug("Creating difference map")
            d = (difference(a, b)).convert("L")
            logging.debug("Converting differente map")
            pixmapdiff = QPixmap.fromImage(ImageQt(d.copy()))
            logging.debug("Setting difference map")
            self.imagediff.setimage(pixmapdiff)

    def copy(self, *args, **kwargs):
        if self.selectedItem is None:
            return

        source = os.path.join(self.foldera, self.selectedItem.text())
        dest = os.path.join(self.folderb, self.selectedItem.text())

        print("Copy from {} to {}".format(source, dest))
        shutil.copyfile(source, dest)


def main():
    if len(sys.argv) < 3:
        print("Folders need to be specified")

    foldera, folderb = sys.argv[1:3]
    image_list = compare(foldera, folderb, render=False)

    app = QApplication([])
    app.setApplicationName("Imagediff")
    app.setApplicationDisplayName("Imagediff")
    imgdiff = Imgdiff(foldera, folderb, image_list)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

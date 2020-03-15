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
from .cli import compare
from PIL import Image
from PIL.ImageQt import ImageQt
from PIL.ImageChops import difference
import shutil


class Imgdiff(QMainWindow):
    def __init__(self, foldera, folderb, changed_files):
        super().__init__()
        self.initUI(changed_files)
        self.foldera = foldera
        self.folderb = folderb
        self.selectedItem = None
    
    def initUI(self, changed_files):
        widget = QWidget()

        # Main layout container
        hbox = QHBoxLayout()

        # List and buttonss sublayout
        vbox = QVBoxLayout()

        # Setup file list
        imagelist = QListWidget()

        for f in changed_files:
            imagelist.addItem(QListWidgetItem(f))
        
        imagelist.itemClicked.connect(self.selected)
        vbox.addWidget(imagelist)

        # Setup copy button
        copybutton = QPushButton("Copy")
        copybutton.clicked.connect(self.copy)
        vbox.addWidget(copybutton)

        hbox.addLayout(vbox, 1)

        # Setup image grid
        self.imagea = QLabel()
        self.imageb = QLabel()
        self.imagediff = QLabel()
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
        imagea = os.path.join(self.foldera, item.text())
        imageb = os.path.join(self.folderb, item.text())

        pixmapa = QPixmap(imagea)
        self.imagea.setPixmap(pixmapa)
        pixmapb = QPixmap(imageb)
        self.imageb.setPixmap(pixmapb)

        a = Image.open(imagea)
        b = Image.open(imageb)

        d = (difference(a, b)).convert("RGB")

        pixmapdiff = QPixmap.fromImage(ImageQt(d))
        self.imagediff.setPixmap(pixmapdiff)
    
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
    changed_files = compare(foldera, folderb, render=False)

    app = QApplication([])
    app.setApplicationName("Imagediff")
    app.setApplicationDisplayName("Imagediff")
    imgdiff = Imgdiff(foldera, folderb, changed_files)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
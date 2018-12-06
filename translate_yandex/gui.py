#!/usr/bin/env python3
# -*- coding: utf-8 -*-
try:
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtGui import *


class MyWidget(QWidget):
    """Окошко программы"""
    def __init__(self):
        super(MyWidget, self).__init__()
        self.edit = QPlainTextEdit()

        button = QPushButton("OK")
        button.clicked.connect(self.click)

        vbox = QVBoxLayout()
        vbox.addWidget(self.edit)
        vbox.addWidget(button)

        self.setLayout(vbox)
        self.resize(600, 400)

    def click(self):
        text = self.edit.toPlainText()
        text = self.func(text)
        self.edit.setPlainText(text)

    def func(self, text):
        raise NotImplementedError

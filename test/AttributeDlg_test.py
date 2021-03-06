#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
#
#    nexdatas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nexdatas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nexdatas.  If not, see <http://www.gnu.org/licenses/>.
# \package test nexdatas
# \file AttributeDlgTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import random
import struct
import binascii
import time

from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import (QApplication, QMessageBox)
from PyQt5.QtCore import Qt, QTimer

from nxsconfigtool.AttributeDlg import AttributeDlg

# from nxsconfigtool.ui.ui_attributedlg import Ui_AttributeDlg

#  Qt-application
app = None

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)

if sys.version_info > (3,):
    unicode = str
    long = int


# test fixture
class AttributeDlgTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"
        # MessageBox text
        self.text = None
        # MessageBox title
        self.title = None

        try:
            self.__seed = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed = long(time.time() * 256)

        self.__rnd = random.Random(self.__seed)

    # test starter
    # \brief Common set up
    def setUp(self):
        print("\nsetting up...")
        print("SEED = %s" % self.__seed)

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")

    # constructor test
    # \brief It tests default settings
    def test_constructor_accept(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = AttributeDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.value, '')
        self.assertTrue(form.ui.__class__.__name__, "AttributeDlg")
        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.valueLineEdit.text())
        self.assertTrue(
            not form.ui.buttonBox.button(form.ui.buttonBox.Ok).isEnabled())
        self.assertTrue(
            form.ui.buttonBox.button(form.ui.buttonBox.Cancel).isEnabled())

        name = "myname"
        value = "myentry"
        QTest.keyClicks(form.ui.nameLineEdit, name)
        self.assertEqual(form.ui.nameLineEdit.text(), name)
        QTest.keyClicks(form.ui.valueLineEdit, value)
        self.assertEqual(form.ui.valueLineEdit.text(), value)

        self.assertTrue(bool(form.ui.nameLineEdit.text()))
        self.assertTrue(bool(form.ui.valueLineEdit.text()))
        self.assertTrue(
            form.ui.buttonBox.button(form.ui.buttonBox.Ok).isEnabled())
        self.assertTrue(
            form.ui.buttonBox.button(form.ui.buttonBox.Cancel).isEnabled())

        okWidget = form.ui.buttonBox.button(form.ui.buttonBox.Ok)
        QTest.mouseClick(okWidget, Qt.LeftButton)

        self.assertEqual(form.name, name)
        self.assertEqual(form.value, value)

        self.assertEqual(form.result(), 1)

    # constructor test
    # \brief It tests default settings
    def test_constructor_reject(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = AttributeDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.value, '')

        name = "myname"
        value = "myentry"
        QTest.keyClicks(form.ui.nameLineEdit, name)
        self.assertEqual(form.ui.nameLineEdit.text(), name)
        QTest.keyClicks(form.ui.valueLineEdit, value)
        self.assertEqual(form.ui.valueLineEdit.text(), value)
        clWidget = form.ui.buttonBox.button(form.ui.buttonBox.Cancel)
        QTest.mouseClick(clWidget, Qt.LeftButton)

        self.assertEqual(form.name, '')
        self.assertEqual(form.value, '')

        self.assertEqual(form.result(), 0)

    def checkMessageBox(self):
        # self.assertEqual(QApplication.activeWindow(), None)
        mb = QApplication.activeModalWidget()
        self.assertTrue(isinstance(mb, QMessageBox))
#        print mb.text()
        self.text = mb.text()
        self.title = mb.windowTitle()
        mb.close()

    # constructor test
    # \brief It tests default settings
    def test_constructor_accept_dash(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        form = AttributeDlg()
        form.show()
        self.assertEqual(form.name, '')
        self.assertEqual(form.value, '')
        self.assertTrue(not form.ui.nameLineEdit.text())
        self.assertTrue(not form.ui.valueLineEdit.text())
        self.assertTrue(
            not form.ui.buttonBox.button(form.ui.buttonBox.Ok).isEnabled())
        self.assertTrue(
            form.ui.buttonBox.button(form.ui.buttonBox.Cancel).isEnabled())

        name = "-myname"
        value = "myentry"
        QTest.keyClicks(form.ui.nameLineEdit, name)
        QTest.keyClicks(form.ui.valueLineEdit, value)
        self.assertEqual(form.ui.nameLineEdit.text(), name)
        self.assertEqual(form.ui.valueLineEdit.text(), value)

        self.assertTrue(bool(form.ui.nameLineEdit.text()))
        self.assertTrue(bool(form.ui.valueLineEdit.text()))
        self.assertTrue(
            form.ui.buttonBox.button(form.ui.buttonBox.Ok).isEnabled())
        self.assertTrue(
            form.ui.buttonBox.button(form.ui.buttonBox.Cancel).isEnabled())

        QTimer.singleShot(0, self.checkMessageBox)
        okWidget = form.ui.buttonBox.button(form.ui.buttonBox.Ok)
        QTest.mouseClick(okWidget, Qt.LeftButton)

#        self.assertEqual(self.title, 'Character Error')
        self.assertEqual(self.text, "The first character of Name is '-'")

        self.assertEqual(form.name, '')
        self.assertEqual(form.value, '')

        self.assertEqual(form.result(), 0)

    # constructor test
    # \brief It tests default settings
    def test_constructor_accept_chars(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        chars = '!"#$%&\'()*+,/;<=>?@[\\]^`{|}~'

        for ch in chars:

            form = AttributeDlg()
            form.show()
            self.assertEqual(form.name, '')
            self.assertEqual(form.value, '')
            self.assertTrue(not form.ui.nameLineEdit.text())
            self.assertTrue(not form.ui.valueLineEdit.text())
            self.assertTrue(
                not form.ui.buttonBox.button(form.ui.buttonBox.Ok).isEnabled())
            self.assertTrue(
                form.ui.buttonBox.button(form.ui.buttonBox.Cancel).isEnabled())

            name = "myname"
            value = "myentry"

            pos = self.__rnd.randint(0, len(name)-1)
            name = name[:pos] + ch + name[pos:]

            QTest.keyClicks(form.ui.nameLineEdit, name)
            QTest.keyClicks(form.ui.valueLineEdit, value)
            self.assertEqual(form.ui.nameLineEdit.text(), name)
            self.assertEqual(form.ui.valueLineEdit.text(), value)

            self.assertTrue(bool(form.ui.nameLineEdit.text()))
            self.assertTrue(bool(form.ui.valueLineEdit.text()))
            self.assertTrue(
                form.ui.buttonBox.button(form.ui.buttonBox.Ok).isEnabled())
            self.assertTrue(
                form.ui.buttonBox.button(form.ui.buttonBox.Cancel).isEnabled())

            QTimer.singleShot(0, self.checkMessageBox)
            okWidget = form.ui.buttonBox.button(form.ui.buttonBox.Ok)
            QTest.mouseClick(okWidget, Qt.LeftButton)

#            self.assertEqual(self.title, 'Character Error')
            self.assertEqual(
                self.text, 'Name contains one of forbidden characters')

            self.assertEqual(form.name, '')
            self.assertEqual(form.value, '')

            self.assertEqual(form.result(), 0)


if __name__ == '__main__':
    if not app:
        app = QApplication([])
    unittest.main()

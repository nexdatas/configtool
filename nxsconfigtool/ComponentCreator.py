#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2016 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \package nxsconfigtool nexdatas
## \file ComponentCreator.py
# Class for connecting to configuration server

""" Provides connects to configuration server"""

from PyQt4.QtGui import (QMessageBox)

import logging
## message logger
logger = logging.getLogger("nxsdesigner")

try:
    import nxstools
    from nxstools.nxscreator import OnlineCPCreator, OnlineDSCreator
    NXSTOOLS_AVAILABLE = True
    NXSTOOLS_MASTERVER, NXSTOOLS_MINORVER, NXSTOOLS_PATCHVER = \
        nxstools.__version__.split(".")
    if int(NXSTOOLS_MASTERVER) <= 1:
        if int(NXSTOOLS_MINORVER) <= 18:
            raise ImportError("nxstools is below 1.19.0")
except ImportError, e:
    NXSTOOLS_AVAILABLE = False
    logger.info("nxstools is not available: %s" % e)

from PyQt4.QtGui import (QFileDialog)

from .CreatorDlg import CreatorDlg


## option class
class Options(object):
    def __init__(self, server=None):
        self.server = server
        self.overwrite = True
        self.lower = True
        self.component = None
        self.directory = None


## configuration server
class ComponentCreator(object):

    ## constructor
    def __init__(self, configServer, parent):
        ## configuration server
        self.configServer = configServer

        ## online file name
        self.onlineFile = None

        ## componentName
        self.componentName = None

        ## created components
        self.components = {}
        ## created components
        self.datasources = {}
        ## available components
        self.avcomponents = []
        ## parent
        self.parent = parent

    ## sets onlineFile name and check if online file exists
    def checkOnlineFile(self, onlineFile):
        onlineFile = onlineFile or '/online_dir/online.xml'
        onlineFile = unicode(QFileDialog.getOpenFileName(
            self.parent, "Open Online File", onlineFile,
            "XML files (*.xml)"))
        if onlineFile:
            self.onlineFile = onlineFile
            return True
        else:
            self.onlineFile = None

    ## creates component and datasources from online xml
    def create(self):
        self.action = None
        self.componentName = None
        self.components = {}
        self.datasources = {}
        if NXSTOOLS_AVAILABLE and self.onlineFile:
            options = Options(self.configServer.getDeviceName())

            occ = OnlineCPCreator(options, [self.onlineFile], False)
            self.avcomponents = occ.listcomponents() or []
            if self.avcomponents:
                self.action = self.selectComponent()
                options.component = self.componentName
                if self.action:
                    occ.createXMLs()
                    self.components = dict(occ.components)
                    self.datasources = dict(occ.datasources)
            else:
                QMessageBox.warning(
                    self.parent,
                    "Error in creating Component",
                    "Cannot find any known components in '%s'" %
                    self.onlineFile)

    ## runs Creator widget to select the required component
    # \returns action to be performed with the components and datasources
    def selectComponent(self):
        aform = CreatorDlg(self.parent)
        if self.avcomponents:
            aform.components = list(self.avcomponents)

        action = None
        self.componentName = None
        aform.createGUI()
        aform.show()
        if aform.exec_():
            action = aform.action
            self.componentName = aform.componentName
        return action


## configuration server
class DataSourceCreator(object):

    ## constructor
    def __init__(self, configServer, parent):
        ## configuration server
        self.configServer = configServer

        ## online file name
        self.onlineFile = None

        ## componentName
        self.componentName = None

        ## created components
        self.datasources = {}
        ## available components
        self.avcomponents = []
        ## parent
        self.parent = parent

    ## sets onlineFile name and check if online file exists
    def checkOnlineFile(self, onlineFile):
        onlineFile = onlineFile or '/online_dir/online.xml'
        onlineFile = unicode(QFileDialog.getOpenFileName(
            self.parent, "Open Online File", onlineFile,
            "XML files (*.xml)"))
        if onlineFile:
            self.onlineFile = onlineFile
            return True
        else:
            self.onlineFile = None

    ## creates component and datasources from online xml
    def create(self):
        self.action = None
        self.datasources = {}
        if NXSTOOLS_AVAILABLE and self.onlineFile:
            options = Options(self.configServer.getDeviceName())

            occ = OnlineDSCreator(options, [self.onlineFile], False)
            self.action = self.selectAction()
            if self.action:
                occ.createXMLs()
                self.datasources = dict(occ.datasources)

    ## runs Creator widget to select the required component
    # \returns action to be performed with the components and datasources
    def selectAction(self):
        aform = CreatorDlg(self.parent)
        action = None
        aform.createGUI()
        aform.setWindowTitle("DataSource Creator")
        aform.ui.compFrame.hide()
        aform.resize(600, 0)
        aform.show()
        if aform.exec_():
            action = aform.action
        return action


## test function
def test():
    import sys
    from PyQt4.QtGui import QApplication

    app = QApplication(sys.argv)
    app.exit()

if __name__ == "__main__":
    test()
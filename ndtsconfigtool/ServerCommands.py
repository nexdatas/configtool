#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2013 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \package ndtsconfigtool nexdatas
## \file ServerCommands.py
# user commands of GUI application

""" Component Designer commands """

from PyQt4.QtGui import (QMessageBox, QUndoCommand, QProgressDialog)

from PyQt4.QtCore import (Qt, QString)

from .DataSourceDlg import (CommonDataSourceDlg)
from . import DataSource
from .ComponentDlg import ComponentDlg
from .Component import Component

import logging
logger = logging.getLogger(__name__)


## Command which performs connection to the configuration server
class ServerConnect(QUndoCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        ## main window
        self.receiver = receiver
        self._oldstate = None
        self._state = None
        

    ## executes the command
    # \brief It perform connection to the configuration server
    def redo(self):       
        if self.receiver.configServer:
            try:
                if self._oldstate is None:
                    self._oldstate = self.receiver.configServer.getState()
                if  self._state is None:   
                    self.receiver.configServer.open()
                    self._state = self.receiver.configServer.getState()
                else:
                    self.receiver.configServer.setState(self._state)
                    self.receiver.configServer.connect()
                    
                self.receiver.disableServer(False)
            except Exception, e:
                QMessageBox.warning(
                    self.receiver, 
                    "Error in connecting to Configuration Server", 
                    unicode(e))
    
        logger.info("EXEC serverConnect")

    ## unexecutes the command
    # \brief It undo connection to the configuration server, 
    #        i.e. it close the connection to the server
    def undo(self):
        if self.receiver.configServer:
            try:
                self.receiver.configServer.close()
                if self._oldstate is None:
                    self.receiver.configServer.setState(self._oldstate)
                self.receiver.disableServer(True)
            except Exception, e:
                QMessageBox.warning(
                    self.receiver, 
                    "Error in Closing Configuration Server Connection", 
                    unicode(e))

        logger.info("UNDO serverConnect")




## Command which fetches the components from the configuration server
class ServerFetchComponents(QUndoCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        ## main window
        self.receiver = receiver

    ## executes the command
    # \brief It fetches the components from the configuration server
    def redo(self):       
        if QMessageBox.question(
            self.receiver, 
            "Component - Reload List from Configuration server",
            ("All unsaved components will be lost. "\
                 "Would you like to proceed ?").encode(),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes) == QMessageBox.No :
            return

        
        subwindows = self.receiver.ui.mdi.subWindowList()
        if subwindows:
            for subwindow in subwindows:
                dialog = subwindow.widget()
                if isinstance(dialog, ComponentDlg):
                    self.receiver.ui.mdi.setActiveSubWindow(subwindow)
                    self.receiver.ui.mdi.closeActiveSubWindow()

        self.receiver.componentList.elements = {} 

        if self.receiver.configServer:
            try:
                if not self.receiver.configServer.connected:
                    QMessageBox.information(
                        self.receiver, 
                        "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.configServer.device,
                            self.receiver.configServer.host,
                            self.receiver.configServer.port
                            )
                        )

                self.receiver.configServer.connect()
                self.receiver.disableServer(False)
                cdict = self.receiver.configServer.fetchComponents()
                self.receiver.setComponents(cdict)
            except Exception, e:
                QMessageBox.warning(
                    self.receiver, 
                    "Error in fetching components", unicode(e))
    
        logger.info("EXEC serverFetchComponents")

    ## unexecutes the command
    # \brief It does nothing
    def undo(self):
        logger.info("UNDO serverFetchComponents")


## Command which stores the current component in the configuration server
class ServerStoreComponent(QUndoCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        ## main window
        self.receiver = receiver
        self._cp = None
        self._cpEdit = None

    ## executes the command
    # \brief It stores the current component in the configuration server
    def redo(self):       
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListElement()
        if self._cp is not None:
            if self._cp.instance is None:
                #                self._cpEdit = FieldWg()  
                self._cpEdit = Component(self.receiver.componentList)
                self._cpEdit.id = self._cp.id
                self._cpEdit.directory = \
                    self.receiver.componentList.directory
                self._cpEdit.name = \
                    self.receiver.componentList.elements[
                    self._cp.id].name
                self._cpEdit.createGUI()
                self._cpEdit.addContextMenu(
                    self.receiver.contextMenuActions)
                self._cpEdit.createHeader()
                self._cpEdit.dialog.setWindowTitle(
                    "%s [Component]" % self._cp.name)
            else:
                self._cpEdit = self._cp.instance 
                
            if hasattr(self._cpEdit, "connectExternalActions"):     
                self._cpEdit.connectExternalActions(
                    **self.receiver.externalCPActions)      


                
            subwindow = self.receiver.subWindow(
                self._cpEdit, self.receiver.ui.mdi.subWindowList())
            if subwindow:
                self.receiver.ui.mdi.setActiveSubWindow(subwindow) 
            else:    
                self._cpEdit.createGUI()

                self._cpEdit.addContextMenu(
                    self.receiver.contextMenuActions)
                if self._cpEdit.isDirty():
                    self._cpEdit.dialog.setWindowTitle(
                        "%s [Component]*" % self._cp.name)
                else:
                    self._cpEdit.dialog.setWindowTitle(
                        "%s [Component]" % self._cp.name)
                     
                self._cpEdit.reconnectSaveAction()
                subwindow = self.receiver.ui.mdi.addSubWindow(
                    self._cpEdit.dialog)
                subwindow.resize(680, 560)
                self._cpEdit.dialog.show()
                self._cp.instance = self._cpEdit 
                    
            try:
                xml = self._cpEdit.get()    
                if not self.receiver.configServer.connected:
                    if QMessageBox.question(
                        self.receiver, 
                        "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.configServer.device,
                            self.receiver.configServer.host,
                            self.receiver.configServer.port
                            ),
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes) == QMessageBox.No :
                        raise Exception("Server not connected")

                self.receiver.configServer.connect()
                self.receiver.disableServer(False)
                self.receiver.configServer.storeComponent(
                    self._cpEdit.name, xml)
                self._cpEdit.savedXML = xml
                self._cp.savedName = self._cp.name
            except Exception, e:
                QMessageBox.warning(self.receiver, 
                                    "Error in storing the component", 
                                    unicode(e))
        if hasattr(self._cp, "id"):
            self.receiver.componentList.populateElements(self._cp.id)
        else:
            self.receiver.componentList.populateElements()

            
        logger.info("EXEC serverStoreComponent")

    ## unexecutes the command
    # \brief It populates only the component list
    def undo(self):
        if hasattr(self._cp, "id"):
            self.receiver.componentList.populateElements(self._cp.id)
        else:
            self.receiver.componentList.populateElements()
        logger.info("UNDO serverStoreComponent")



## Command which deletes the current component from the configuration server
class ServerDeleteComponent(QUndoCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        ## main window
        self.receiver = receiver
        self._cp = None
        

    ## executes the command
    # \brief It deletes the current component from the configuration server
    def redo(self):       
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListElement()
        if self._cp is not None:

            try:
                if not self.receiver.configServer.connected:
                    QMessageBox.information(
                        self.receiver, 
                        "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.configServer.device,
                            self.receiver.configServer.host,
                            self.receiver.configServer.port
                            )
                        )

                self.receiver.configServer.connect()
                self.receiver.disableServer(False)
                self.receiver.configServer.deleteComponent(self._cp.name)
                self._cp.savedName = ""
                if hasattr(self._cp, "instance"):
                    self._cp.instance.savedXML = ""
            except Exception, e:
                QMessageBox.warning(
                    self.receiver, "Error in deleting the component", 
                    unicode(e))

        cid = self._cp.id if hasattr(self._cp, "id") else None
        self.receiver.componentList.populateElements(cid)

            
        logger.info("EXEC serverDeleteComponent")

    ## unexecutes the command
    # \brief It populates only the component list
    def undo(self):
        if hasattr(self._cp, "id"):
            self.receiver.componentList.populateElements(self._cp.id)
        else:
            self.receiver.componentList.populateElements()
        logger.info("UNDO serverDeleteComponent")



## Command which sets on the configuration server the current component 
#  as mandatory
class ServerSetMandatoryComponent(QUndoCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        ## main window
        self.receiver = receiver
        self._cp = None
        
        

    ## executes the command
    # \brief It sets on the configuration server the current component 
    #        as mandatory
    def redo(self):       
        if self._cp is None:
            self._cp = self.receiver.componentList.currentListElement()
        if self._cp is not None:
            try:
                if not self.receiver.configServer.connected:
                    QMessageBox.information(
                        self.receiver, 
                        "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.configServer.device,
                            self.receiver.configServer.host,
                            self.receiver.configServer.port
                            )
                        )

                self.receiver.configServer.connect()
                self.receiver.disableServer(False)
                self.receiver.configServer.setMandatory(self._cp.name)
            except Exception, e:
                QMessageBox.warning(
                    self.receiver, 
                    "Error in setting the component as mandatory", 
                    unicode(e))
        logger.info("EXEC serverSetMandatoryComponent")



## Command which fetches a list of the mandatory components from 
#  the configuration server
class ServerGetMandatoryComponents(QUndoCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        ## main window
        self.receiver = receiver
        

    ## executes the command
    # \brief It fetches a list of the mandatory components from 
    #        the configuration server
    def redo(self):       
        try:
            if not self.receiver.configServer.connected:
                QMessageBox.information(
                    self.receiver, 
                    "Connecting to Configuration Server", 
                    "Connecting to %s on %s:%s" % (
                        self.receiver.configServer.device,
                        self.receiver.configServer.host,
                        self.receiver.configServer.port
                        )
                    )

            self.receiver.configServer.connect()
            self.receiver.disableServer(False)
            mandatory = self.receiver.configServer.getMandatory()
            QMessageBox.information(
                self.receiver, "Mandatory", 
                "Mandatory Components: \n %s" % unicode(mandatory)) 
        except Exception, e:
            QMessageBox.warning(
                self.receiver, 
                "Error in getting the mandatory components", 
                unicode(e))
        logger.info("EXEC serverGetMandatoryComponent")



## Command which sets on the configuration server the current component 
#  as not mandatory
class ServerUnsetMandatoryComponent(QUndoCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        ## main window
        self.receiver = receiver
        self._cp = None
        

    ## executes the command
    # \brief It sets on the configuration server the current component 
    #        as not mandatory
    def redo(self):       
        if self._cp is None:
            self._cp = \
                self.receiver.componentList.currentListElement()
        if self._cp is not None:
            try:
                if not self.receiver.configServer.connected:
                    QMessageBox.information(
                        self.receiver, 
                        "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.configServer.device,
                            self.receiver.configServer.host,
                            self.receiver.configServer.port
                            )
                        )

                self.receiver.configServer.connect()
                self.receiver.disableServer(False)
                self.receiver.configServer.unsetMandatory(
                    self._cp.name)
            except Exception, e:
                QMessageBox.warning(
                    self.receiver, 
                    "Error in setting the component as mandatory", 
                    unicode(e))
        logger.info("EXEC serverUnsetMandatoryComponent")

    ## unexecutes the command
    # \brief It does nothing    
    def undo(self):
        logger.info("UNDO serverUnsetMandatoryComponent")


## Command which fetches the datasources from the configuration server
class ServerFetchDataSources(QUndoCommand):
    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        ## main window
        self.receiver = receiver
        

    ## executes the command
    # \brief It fetches the datasources from the configuration server
    def redo(self):       

        if QMessageBox.question(
            self.receiver, 
            "DataSource - Reload List from Configuration Server",
            ("All unsaved datasources will be lost. "\
                 "Would you like to proceed ?").encode(),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes ) == QMessageBox.No :
            return


        subwindows = self.receiver.ui.mdi.subWindowList()
        if subwindows:
            for subwindow in subwindows:
                dialog = subwindow.widget()
                if isinstance(dialog, CommonDataSourceDlg):
                    self.receiver.ui.mdi.setActiveSubWindow(subwindow)
                    self.receiver.ui.mdi.closeActiveSubWindow()
                    
        self.receiver.sourceList.elements = {} 


        if self.receiver.configServer:
            try:
                if not self.receiver.configServer.connected:
                    QMessageBox.information(
                        self.receiver, 
                        "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.configServer.device,
                            self.receiver.configServer.host,
                            self.receiver.configServer.port
                            )
                        )
                self.receiver.configServer.connect()
                self.receiver.disableServer(False)
                cdict = self.receiver.configServer.fetchDataSources()
                self.receiver.setDataSources(cdict)
            except Exception, e:
                QMessageBox.warning(
                    self.receiver, 
                    "Error in fetching datasources", unicode(e))
    

        logger.info("EXEC serverFetchDataSources")

    ## unexecutes the command
    # \brief It does nothing    
    def undo(self):
        logger.info("UNDO serverFetchDataSources")


## Command which stores the current datasource in the configuration server
class ServerStoreDataSource(QUndoCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        ## main window
        self.receiver = receiver
        self._ds = None
        

    ## executes the command
    # \brief It fetches the datasources from the configuration server
    def redo(self):       
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListElement()
        if self._ds is not None and hasattr(self._ds, "instance"):
            try:
                xml = self._ds.instance.get()    
                if not self.receiver.configServer.connected:
                    if QMessageBox.question(
                        self.receiver, 
                        "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.configServer.device,
                            self.receiver.configServer.host,
                            self.receiver.configServer.port
                            ),
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes) == QMessageBox.No :
                        raise Exception("Server not connected")

                self.receiver.configServer.connect()
                self.receiver.disableServer(False)
                if self._ds.instance.name:
                    self.receiver.configServer.storeDataSource(
                        self._ds.instance.dataSourceName, xml)
                else:
                    self.receiver.configServer.storeDataSource(
                        self._ds.instance.name, xml)
                self._ds.instance.savedXML = xml
                self._ds.savedName = self._ds.name
            except Exception, e:
                QMessageBox.warning(
                    self.receiver, 
                    "Error in datasource storing", unicode(e))
            

        ds = self.receiver.sourceList.currentListElement()
        if hasattr(ds , "id"):
            self.receiver.sourceList.populateElements(ds.id)
        else:
            self.receiver.sourceList.populateElements()
            
        logger.info("EXEC serverStoreDataSource")

    ## unexecutes the command
    # \brief It populates the datasource list
    def undo(self):
        ds = self.receiver.sourceList.currentListElement()
        if hasattr(ds , "id"):
            self.receiver.sourceList.populateElements(ds.id)
        else:
            self.receiver.sourceList.populateElements()
        logger.info("UNDO serverStoreDataSource")


## Command which deletes the current datasource in the configuration server
class ServerDeleteDataSource(QUndoCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        ## main window
        self.receiver = receiver
        self._ds = None

    ## executes the command
    # \brief It deletes the current datasource in the configuration server
    def redo(self):       
        if self._ds is None:
            self._ds = self.receiver.sourceList.currentListElement()
        if self._ds is not None:
            try:
                if hasattr(self._ds, "instance"):
                    self._ds.instance.savedXML = ""
                    name = self._ds.instance.dataSourceName 
                    if name is None:
                        name = ""
                    if not self.receiver.configServer.connected:
                        QMessageBox.information(
                            self.receiver, 
                            "Connecting to Configuration Server", 
                            "Connecting to %s on %s:%s" % (
                                self.receiver.configServer.device,
                                self.receiver.configServer.host,
                                self.receiver.configServer.port
                                )
                            )

                    self.receiver.configServer.connect()
                    self.receiver.disableServer(False)
                    self.receiver.configServer.deleteDataSource(name)
                    self._ds.savedName = ""

            except Exception, e:
                QMessageBox.warning(
                    self.receiver, 
                    "Error in datasource deleting", unicode(e))
            

        ds = self.receiver.sourceList.currentListElement()
        if hasattr(ds , "id"):
            self.receiver.sourceList.populateElements(ds.id)
        else:
            self.receiver.sourceList.populateElements()
        logger.info("EXEC serverDeleteDataSource")

    ## unexecutes the command
    # \brief It populates the datasource list
    def undo(self):
        ds = self.receiver.sourceList.currentListElement()
        if hasattr(ds , "id"):
            self.receiver.sourceList.populateElements(ds.id)
        else:
            self.receiver.sourceList.populateElements()
        logger.info("UNDO serverDeleteDataSource")



## Command which closes connection to the configuration server
class ServerClose(QUndoCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        ## main window
        self.receiver = receiver
        self._state = None

    ## executes the command
    # \brief It closes connection to the configuration server
    def redo(self):       
        if self.receiver.configServer:
            self.receiver.configServer.close()


        if self.receiver.configServer:
            try:
                if self._state is None:
                    self._state = self.receiver.configServer.getState()
                self.receiver.configServer.close()
                self.receiver.disableServer(True)
            except Exception, e:
                QMessageBox.warning(
                    self.receiver, 
                    "Error in closing connection to Configuration Server", 
                    unicode(e))
    
        logger.info("EXEC serverClose")

    ## unexecutes the command
    # \brief It reopen the connection to the configuration server
    def undo(self):
        if self.receiver.configServer:
            try:
                if  self._state is None:   
                    self.receiver.configServer.open()
                else:
                    self.receiver.configServer.setState(self._state)
                    self.receiver.configServer.connect()
                self.receiver.disableServer(False)
            except Exception, e:
                QMessageBox.warning(
                    self.receiver, 
                    "Error in connecting to Configuration Server", 
                    unicode(e))
        logger.info("UNDO serverClose")


## Command which saves all components in the file
class ServerStoreAllComponents(QUndoCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        ## main window
        self.receiver = receiver
        self._subwindow = None
        
        
    ## executes the command
    # \brief It saves all components in the file
    def redo(self):

        keys = self.receiver.componentList.elements.keys()
        progress = QProgressDialog(
            "Storing Component elements", 
            QString(), 0, len(keys), self.receiver.componentList)    
        progress.setWindowTitle("Store All Components")
        progress.setWindowModality(Qt.WindowModal)
        progress.show()    

        for i in range(len(keys)):
            icp = keys[i]
            cp = self.receiver.componentList.elements[icp]
            if cp.instance is None:
                #                self._cpEdit = FieldWg()  
                cpEdit = Component(self.receiver.componentList)
                cpEdit.id = cp.id
                cpEdit.directory = self.receiver.componentList.directory
                cpEdit.name = self.receiver.componentList.elements[
                    cp.id].name
                cpEdit.createGUI()
                cpEdit.addContextMenu(self.receiver.contextMenuActions)
                cpEdit.createHeader()
                cpEdit.dialog.setWindowTitle("%s [Component]" % cp.name)
                cp.instance = cpEdit

            try:
                cp.instance.merge(False)    
                xml = cp.instance.get()    
                if not self.receiver.configServer.connected:
                    QMessageBox.information(
                        self.receiver, 
                        "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.configServer.device,
                            self.receiver.configServer.host,
                            self.receiver.configServer.port
                            )
                        )
                self.receiver.configServer.connect()
                self.receiver.disableServer(False)
                self.receiver.configServer.storeComponent(
                    cp.instance.name, xml)
                cp.instance.savedXML = xml
                cp.savedName = cp.name
            except Exception, e:
                QMessageBox.warning(
                    self.receiver, "Error in storing the component", 
                    unicode(e))
            progress.setValue(i)
        progress.setValue(len(keys))
        progress.close()    
        if hasattr(cp, "id"):
            self.receiver.componentList.populateElements(cp.id)
        else:
            self.receiver.componentList.populateElements()


        logger.info("EXEC componentStoreAll")


    ## unexecutes the command
    # \brief It does nothing
    def undo(self):
        logger.info("UNDO componentStoreAll")



## Command which saves all the datasources in files
class ServerStoreAllDataSources(QUndoCommand):

    ## constructor
    # \param receiver command receiver
    # \param parent command parent
    def __init__(self, receiver, parent=None):
        QUndoCommand.__init__(self, parent)
        ## main window
        self.receiver = receiver
        
        
    ## executes the command
    # \brief It saves all the datasources in files
    def redo(self):
            
        keys = self.receiver.sourceList.elements.keys()
        progress = QProgressDialog(
            "Storing DataSource elements", 
            QString(), 0, len(keys), self.receiver.sourceList)    
        progress.setWindowTitle("Store All DataSources")
        progress.setWindowModality(Qt.WindowModal)
        progress.show()    

        for i in range(len(keys)):
            ids = keys[i]
            ds = self.receiver.sourceList.elements[ids]
            if ds.instance is None:
                dsEdit = DataSource.DataSource(self.receiver.sourceList)
                dsEdit.id = ds.id
                dsEdit.directory = self.receiver.sourceList.directory
                dsEdit.name = \
                    self.receiver.sourceList.elements[ds.id].name
                ds.instance = dsEdit 
            logger.info("Store %s" % ds.instance.name)

            try:
                xml = ds.instance.get()    
                if not self.receiver.configServer.connected:
                    QMessageBox.information(
                        self.receiver, 
                        "Connecting to Configuration Server", 
                        "Connecting to %s on %s:%s" % (
                            self.receiver.configServer.device,
                            self.receiver.configServer.host,
                            self.receiver.configServer.port
                            )
                        )
                self.receiver.configServer.connect()
                self.receiver.disableServer(False)
                if ds.instance.name:
                    self.receiver.configServer.storeDataSource(
                        ds.instance.dataSourceName, xml)
                else:
                    self.receiver.configServer.storeDataSource(
                        ds.instance.name, xml)
                ds.instance.savedXML = xml
                ds.savedName = ds.name
            except Exception, e:
                QMessageBox.warning(
                    self.receiver, "Error in datasource storing", 
                    unicode(e))


            progress.setValue(i)
        progress.setValue(len(keys))
        progress.close()    
        ds = self.receiver.sourceList.currentListElement()
        if hasattr(ds , "id"):
            self.receiver.sourceList.populateElements(ds.id)
        else:
            self.receiver.sourceList.populateElements()


        logger.info("EXEC dsourceStoreAll")

    ## executes the command
    # \brief It does nothing
    def undo(self):
        logger.info("UNDO dsourceStoreAll")


        

if __name__ == "__main__":
    pass

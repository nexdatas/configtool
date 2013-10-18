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
## \file DataSourceDlg.py
# Data Source data class

""" Provides datasource widget """

import os
import copy

from PyQt4.QtCore import (SIGNAL, QModelIndex, QString, QFileInfo, QFile, 
                          QIODevice, QTextStream)
from PyQt4.QtGui import (QApplication, QFileDialog, QMessageBox, 
                         QWidget, QVBoxLayout)
from PyQt4.QtXml import (QDomDocument)

from .NodeDlg import NodeDlg 
from .DomTools import DomTools
from .Errors import ParameterError
from .DataSources import ClientSource, TangoSource, DBSource, PyEvalSource
import DataSourceDlg 
from .DataSourceMethods import DataSourceMethods

from .ui.ui_datasourcedlg import Ui_DataSourceDlg




## dialog defining datasource
class CommonDataSource(object):
    
    ## constructor
    def __init__(self):
        
#        ## datasource dialog parent
#        self.parent = parent

        ## data source type
        self.dataSourceType = 'CLIENT'
        ## attribute doc
        self.doc = u''

        ## datasource dialog
        self.dialog = NodeDlg()

        ## datasource name
        self.dataSourceName = u''



        ## external save method
        self.externalSave = None
        ## external store method
        self.externalStore = None
        ## external close method
        self.externalClose = None
        ## external apply method
        self.externalApply = None

        ## applied flag
        self.applied = False

        ## datasource id
        self.ids = None

        
        ## if datasource in the component tree
        self.tree = False
        

        ## creates variables dynamically
        self.clear()


    ## clears the datasource content
    # \brief It sets the datasource variables to default values
    def clear(self):
        for cl in DataSourceDlg.dsTypes.values():
            for vr in cl.var.keys():
                setattr(self, vr, cl.var[vr])


        

    ## provides the state of the datasource dialog        
    # \returns state of the datasource in tuple
    def getState(self):
        state = [self.dataSourceType,
                 self.dataSourceName,
                 self.doc]

        for cl in DataSourceDlg.dsTypes.values():
            for vr in cl.var.keys():
                vv = getattr(self, vr)
                state.append(
                    copy.copy(vv) \
                        if ((type(vv) is list) or (type(vv) is dict)) else vv)
        return tuple(state)        



    ## sets the state of the datasource dialog        
    # \brief note that ids, applied and tree are not in the state
    # \param state state datasource written in tuple 
    def setState(self, state):
    
        cnt = 3
        (self.dataSourceType, self.dataSourceName, self.doc) = state[:cnt]

        for cl in DataSourceDlg.dsTypes.values():
            for vr in cl.var.keys():
                setattr(
                    self, vr, copy.copy(state[cnt]) \
                        if ((type(state[cnt]) is list) \
                                or (type(state[cnt]) is dict)) \
                        else state[cnt])
                cnt += 1


## dialog defining datasource
class DataSource(CommonDataSource):

    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(DataSource, self).__init__()


        ## dialog parent
        self.parent = parent

        ## datasource dialog
        self.dialog = DataSourceDlg.CommonDataSourceDlg(self, parent)

        ## datasource methods
        self.__methods = DataSourceMethods(self.dialog, self)

        ## datasource directory
        self.directory = ""

        ## datasource file name
        self.name = None

        ## DOM document
        self.document = None
        ## saved XML
        self.savedXML = None
        

        
    ## creates dialog
    # \brief It creates dialog, its GUI , updates Nodes and Form
    def createDialog(self):
        self.dialog = DataSourceDlg.CommonDataSourceDlg(self, self.parent)
        self.__methods.setDialog(self.dialog)
        self.createGUI()
        
        self.updateForm()
        self.updateNode()


    ## clears the datasource content
    # \brief It sets the datasource variables to default values
    def clear(self):
        CommonDataSource.clear(self)
        
        if hasattr(self.dialog, "imp"):
            for ds in self.dialog.imp.values():
                if hasattr(ds,"clear"):
                    ds.clear()


    ## checks if not saved
    # \returns True if it is not saved     
    def isDirty(self):
        string = self.get()

        return False if string == self.savedXML else True


    ## provides the datasource in xml string
    # \returns xml string    
    def get(self, indent = 0):
        if hasattr(self.document,"toString"):
            return unicode(self.document.toString(indent))


    ## sets file name of the datasource and its directory
    # \param name name of the datasource
    # \param directory directory of the datasources   
    def setName(self, name, directory):
        self.name = unicode(name)
#        self.dialog.ui.nameLineEdit.setText(self.name)
        if directory:
            self.directory = unicode(directory)



    ## loads datasources from default file directory
    # \param fname optional file name
    def load(self, fname = None):
        if fname is None:
            if not self.name:
                filename = unicode(QFileDialog.getOpenFileName(
                        self.dialog,"Open File",self.directory,
                        "XML files (*.xml);;HTML files (*.html);;"
                        "SVG files (*.svg);;User Interface files (*.ui)"))
                fi = QFileInfo(filename)
                fname = str(fi.fileName())
                if fname[-4:] == '.xml':
                    self.name = fname[:-4]
                    if self.name[-3:] == '.ds':
                        self.name = self.name[:-3]
                    else:
                        self.name = fname
            else:
                filename = os.path.join(self.directory, self.name + ".ds.xml")
        else:
            filename = fname
            if not self.name:
                fi = QFileInfo(filename)
                fname = str(fi.fileName())
                if fname[-4:] == '.xml':
                    self.name = fname[:-4]
                    if self.name[-3:] == '.ds':
                        self.name = self.name[:-3]
                    else:
                        self.name = fname
        try:
            fh = QFile(filename)
            if  fh.open(QIODevice.ReadOnly):
                self.document = QDomDocument()
                self.root = self.document
#                if not self.document.setContent(self.repair(fh)):
                if not self.document.setContent(fh):
                    raise ValueError, "could not parse XML"

                ds = DomTools.getFirstElement(self.document, "datasource")
                if ds:
                    self.setFromNode(ds)
                self.savedXML = self.document.toString(0)
            else:
                QMessageBox.warning(self.dialog, "Cannot open the file", 
                                    "Cannot open the file: %s" % (filename))
            try:
                self.createGUI()

            except Exception, e:
                QMessageBox.warning(self.dialog, "dialog not created", 
                                    "Problems in creating a dialog %s :\n\n%s" \
                                        %(self.name,unicode(e)))
                
        except (IOError, OSError, ValueError), e:
            error = "Failed to load: %s" % e
            print error
            QMessageBox.warning(self.dialog, "Saving problem", error )

        except Exception, e:
            QMessageBox.warning(self.dialog, "Saving problem", e )
            print e
        finally:                 
            if fh is not None:
                fh.close()
        if fh is not None:
            return filename

    ## repairs xml datasources 
    # \param xml xml string
    # \returns repaired xml        
    @classmethod        
    def repair(cls, xml):
        olddoc = QDomDocument()
        if not olddoc.setContent(xml):
            raise ValueError, "could not parse XML"

        definition = olddoc.firstChildElement(QString("definition"))           
        if definition and definition.nodeName() =="definition":
            ds  = definition.firstChildElement(QString("datasource"))
            if ds and ds.nodeName() =="datasource":
                return xml
        
        ds = DomTools.getFirstElement(olddoc, "datasource")           
        
        newdoc = QDomDocument()
        processing = newdoc.createProcessingInstruction("xml", "version='1.0'")
        newdoc.appendChild(processing)

        definition = newdoc.createElement(QString("definition"))
        newdoc.appendChild(definition)

        newds = newdoc.importNode(ds, True)
        definition.appendChild(newds)            
        return newdoc.toString(0)

            
    ## sets datasources from xml string
    # \param xml xml string
    # \param new True if datasource is not saved
    def set(self, xml, new = False):
        self.document = QDomDocument()
        self.root = self.document
        if not self.document.setContent(self.repair(xml)):
            raise ValueError, "could not parse XML"
        else:
            if self.dialog and hasattr(self.dialog,"root"):
                self.dialog.root = self.document 

        ds = DomTools.getFirstElement(self.document, "datasource")           
        if ds:
            self.setFromNode(ds)
            if new:
                self.savedXML = ""
            else:
                self.savedXML = self.document.toString(0)
        try:    
            self.createGUI()
        except Exception, e:
            QMessageBox.warning(self, "dialog not created", 
                                "Problems in creating a dialog %s :\n\n%s" \
                                    %(self.name,unicode(e)))
                

    ## accepts and save input text strings
    # \brief It copies the parameters and saves the dialog
    def save(self):

        error = None
        filename = os.path.join(self.directory, self.name + ".ds.xml") 
        print "saving in %s"% (filename)
        if filename:
            try:
                fh = QFile(filename)
                if not fh.open(QIODevice.WriteOnly):
                    raise IOError, unicode(fh.errorString())
                stream = QTextStream(fh)
                self.createNodes()

                xml = self.repair(self.document.toString(0))
                document = QDomDocument()
                document.setContent(xml)
                stream << document.toString(2)
            #                print self.document.toString(2)
                self.savedXML = document.toString(0)
            except (IOError, OSError, ValueError), e:
                error = "Failed to save: %s " % e \
                    + "Please try to use Save As command " \
                    + "or change the datasource directory"
                print error
                QMessageBox.warning(self.dialog, "Saving problem",  error) 

            finally:
                if fh is not None:
                    fh.close()
        if not error:
            return True

    ## provides the datasource name with its path
    # \returns datasource name with its path 
    def getNewName(self):
        filename = unicode(
            QFileDialog.getSaveFileName(
                self.dialog,"Save DataSource As ...",self.directory,
                "XML files (*.xml);;HTML files (*.html);;"
                "SVG files (*.svg);;User Interface files (*.ui)"))
        print "saving in %s"% (filename)
        return filename





    ## gets the current view
    # \returns the current view  
    def __getview(self):
        if self.dialog and hasattr(self.dialog,"view"):
            return self.dialog.view

    ## sets the current view
    # \param view value to be set 
    def __setview(self, view):
        if self.dialog and hasattr(self.dialog,"view"):
            self.dialog.view = view

    ## attribute value       
    view = property(__getview, __setview)            



    ## gets the current root
    # \returns the current root  
    def __getroot(self):
        if self.dialog and hasattr(self.dialog,"root"):
            return self.dialog.root

    ## sets the current root
    # \param root value to be set 
    def __setroot(self, root):
        if self.dialog and hasattr(self.dialog,"root"):
            self.dialog.root = root

    ## attribute value       
    root = property(__getroot, __setroot)            






    ## shows dialog
    # \brief It adapts the dialog method
    def show(self):
        if hasattr(self,"datasource")  and self.dialog:
            if self.dialog:
                return self.dialog.show()


    ## clears the dialog
    # \brief clears the dialog
    def clearDialog(self):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.setDialog(None)

    ## updates the form
    # \brief abstract class
    def updateForm(self):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.updateForm()


    ## updates the node
    # \brief abstract class
    def updateNode(self, index=QModelIndex()):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.updateNode(index)

        

    ## creates GUI
    # \brief abstract class
    def createGUI(self):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.createGUI()

        
    ## sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.setFromNode(node)

    ## creates datasource node
    # \param external True if it should be create on a local DOM root, 
    #        i.e. in component tree
    # \returns created DOM node   
    def createNodes(self, external = False):        
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.createNodes(external)
        

    ## accepts input text strings
    # \brief It copies the parameters and accept the dialog
    def apply(self):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.apply()


    ## sets the tree mode used in ComponentDlg without save/close buttons
    # \param enable logical variable which dis-/enables mode 
    def treeMode(self, enable = True):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.treeMode(enable)

    ## connects the save action and stores the apply action
    # \param externalApply apply action
    # \param externalSave save action
    # \param externalClose close action
    # \param externalStore store action
    def connectExternalActions(self, externalApply=None , externalSave=None,
                               externalClose = None, externalStore=None):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.connectExternalActions(
                externalApply, externalSave, externalClose, externalStore)

    ## reconnects save actions
    # \brief It reconnects the save action 
    def reconnectSaveAction(self):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.reconnectSaveAction()

        


    ## copies the datasource to the clipboard
    # \brief It copies the current datasource to the clipboard
    def copyToClipboard(self):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.copyToClipboard()
        

    ## copies the datasource from the clipboard to the current 
    #  datasource dialog
    # \return status True on success
    def copyFromClipboard(self):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.copyFromClipboard()


    ## creates the new empty header
    # \brief It clean the DOM tree and put into it xml and definition nodes
    def createHeader(self):
        if hasattr(self,"_DataSource__methods")  and self.__methods:
            return self.__methods.createHeader()

if __name__ == "__main__":
    import sys

    ## Qt application
    app = QApplication(sys.argv)
    ## data source form
    w = QWidget()
    w.show()
    ## the first datasource form
    form = DataSource(w)

    form.dataSourceType = 'CLIENT'
    form.clientRecordName = 'counter1'
    form.doc = 'The first client counter  '

    form.dataSourceType = 'TANGO'
    form.tangoDeviceName = 'p09/motor/exp.01'
    form.tangoMemberName = 'Position'
    form.tangoMemberType = 'attribute'
    form.tangoHost = 'hasso.desy.de'
    form.tangoPort = '10000'
    form.tangoEncoding = 'LIMA2D'
    form.tangoGroup = 'Coordinates'

    form.dataSourceType = 'DB'
    form.dbType = 'PGSQL'
    form.dbDataFormat = 'SPECTRUM'
#    form.dbParameters = {'DB name':'tango', 'DB user':'tangouser'}

    form.createGUI()

    form.dialog.show()


    app.exec_()


#  LocalWords:  decryption

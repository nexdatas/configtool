#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
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
## \file ComponentList.py
# Data component list class

import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_componentlist
import os

from ComponentDlg import *


## dialog defining a group tag
class ComponentList(QWidget, ui_componentlist.Ui_ComponentList):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, directory, parent=None):
        super(ComponentList, self).__init__(parent)
        self.directory = directory
        
        ## group components
        self.components = {}

    ##  creates GUI
    # \brief It calls setupUi and  connects signals and slots    
    def createGUI(self):

        self.setupUi(self)


#        self.connect(self.componentListWidget, 
#                     SIGNAL("itemChanged(QListWidgetItem*)"),
#                     self.listItemChanged)

        self.populateComponents()

    ## adds an component    
    #  \brief It runs the Component Dialog and fetches component name and value    
    def addComponent(self,obj, flag = True):

        self.components[obj.id] = obj
        self.populateComponents(obj.id,flag)
                
                
    ## takes a name of the current component
    # \returns name of the current component            
    def currentListComponent(self):
        item = self.componentListWidget.currentItem()
        if item is None:
            return None    
        return self.components[item.data(Qt.UserRole).toLongLong()[0]] 


    ## removes an component    
    #  \brief It removes the current component asking before about it
    def removeComponent(self,obj = None, question = True):
        if obj is not None:
            oid = obj.id
        else:
            comp = self.currentListComponent()
            if comp is None:
                return
            oid = comp.id
        if oid is None:
            return
        if oid in self.components.keys():
            if question :
                if QMessageBox.question(self, "Component - Close",
                                        "Close the component: %s ".encode() %  (self.components[oid].name),
                                        QMessageBox.Yes | QMessageBox.No) == QMessageBox.No :
                    return

            self.components.pop(oid)
            self.populateComponents()

        attr = self.currentListComponent()
        if attr is None:
            return
        if QMessageBox.question(self, "Component - Remove",
                                "Remove component: %s = \'%s\'".encode() %  (attr, self.components[unicode(attr)]),
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.No :
            return
        if unicode(attr) in self.components.keys():
            self.components.pop(unicode(attr))
            self.populateComponents()

    ## changes the current value of the component        
    # \brief It changes the current value of the component and informs the user that component names arenot editable
    def listItemChanged(self, item):
        icp = self.currentListComponent().id

        if icp in self.components.keys():
            old = self.components[icp] 
            oname = self.components[icp].name
            self.components[icp].name = unicode(item.text())
            self.populateComponents()
            return old, oname


    ## fills in the component table      
    # \param selectedComponent selected component    
    def populateComponents(self, selectedComponent = None, edit = False):
        selected = None
        self.componentListWidget.clear()
        for cp in self.components.keys():
            name = self.components[cp].name
            item  = QListWidgetItem(QString("%s" % name))
            item.setData(Qt.UserRole, QVariant(self.components[cp].id))
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.componentListWidget.addItem(item)
            if selectedComponent is not None and selectedComponent == self.components[cp].id:
                selected = item
            if self.components[cp].widget is not None:
                self.components[cp].widget.setWindowTitle("Components: %s" %name)


        if selected is not None:
            selected.setSelected(True)
            self.componentListWidget.setCurrentItem(selected)
            if edit:
                self.componentListWidget.editItem(selected)


            

    def loadList(self):
        dirList=os.listdir(self.directory)
        for fname in dirList:
            if fname[-4:] == '.xml':
                name = fname[:-4]
            else:
                name = fname
                
            dlg = ComponentDlg()
            dlg.directory = self.directory
            dlg.name = name
            dlg.createGUI()
            dlg.load()    
            cp = LabeledObject(name, dlg)
            self.components[id(cp)] =  cp
            if cp.widget is not None:
                cp.widget.idc = cp.id
            print name
            



    ## accepts input text strings
    # \brief It copies the group name and type from lineEdit widgets and accept the dialog
    def accept(self):
        
        QWidget.accept(self)

if __name__ == "__main__":
    import sys

    ## Qt application
    app = QApplication(sys.argv)
    ## group form
    form = ComponentList()
    form.components={"title":"Test run 1", "run_cycle":"2012-1"}
    form.createGUI()
    form.show()
    app.exec_()


    if form.result():
        if form.components:
            print "Other components:"
            for k in form.components.keys():
                print  " %s = '%s' " % (k, form.components[k])
    

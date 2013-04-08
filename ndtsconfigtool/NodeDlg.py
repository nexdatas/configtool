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
## \file NodeDlg.py
# Abstract Node dialog class

from PyQt4.QtGui import QDialog
from PyQt4.QtXml import QDomNode
from PyQt4.QtCore import (QString, SIGNAL, QModelIndex)

from DomTools import DomTools

## abstract node dialog 
class NodeDlg(QDialog):
    
    ## constructor
    # \param parent patent instance
    def __init__(self, parent=None):
        super(NodeDlg, self).__init__(parent)

#        print "parent :", parent
        ## DOM node    
        self.node = None
        ## DOM root
        self.root = None
        ## component tree view
        self.view = None 

        ## allowed subitems
        self.subItems = []

        ##  user interface 
        self.ui = None

        ## external apply action
        self._externalApply = None

        ## DOM tools
        self.dts = DomTools()

    ## connects the given apply action
    # \param externalApply apply action   
    def connectExternalActions(self,  externalApply=None):
        if externalApply and self._externalApply is None and self.ui and self.ui.applyPushButton:
            self.connect(self.ui.applyPushButton, SIGNAL("clicked()"), externalApply)
            self._externalApply = externalApply

        
    ## resets the dialog
    # \brief It sets forms and dialog from DOM    
    def reset(self):
        if self.view and hasattr(self.view,"currentIndex"):
            index = self.view.currentIndex()
        self.setFromNode()
        self.updateForm()
        if self.view:
            if  index.column() != 0:
                index = self.view.model().index(index.row(), 0, index.parent())
            self.view.model().emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)


    ## provides the first element in the tree with the given name
    # \param node DOM node
    # \param name child name
    # \returns DOM child node
    def _getFirstElement(self, node, name):
        return self.dts.getFirstElement(node, name)
                
                


    ## provides row number of the given node
    # \param child child item
    # \param node parent node        
    # \returns row number
    def getNodeRow(self, child, node = None):
        lnode =  node if node is not None else self.node
        if lnode:
            return self.dts.getNodeRow(child, lnode)


    ## provides node text for the given node
    # \param node DOM node        
    # \returns string with node texts
    def _getText(self, node):
        return self.dts.getText(node)
        

    ## replaces node text for the given node
    # \param node parent DOM node        
    # \param index of child text node
    # \param text string with text
    def _replaceText(self, node, index, text = None):
        return self.dts.replaceText(node, index, self.root, text)
    

    ## removes node
    # \param node DOM node to remove
    # \param parent parent node index        
    def removeNode(self, node, parent):
        if self.view is not None and self.view.model() is not None: 
            return self.dts.removeNode(node, parent, self.view.model())

                
    ## replaces node
    # \param oldNode old DOM node 
    # \param newNode new DOM node 
    # \param parent parent node index
    def _replaceNode(self, oldNode, newNode, parent):
        if self.view is not None and self.view.model() is not None: 
            return self.dts.replaceNode(oldNode, newNode, parent, self.view.model())




    ## appends node
    # \param node DOM node to remove
    # \param parent parent node index
    def appendNode(self, node, parent):
        if self.view is not None and self.view.model() is not None: 
            return self.dts.appendItem(node, parent, self.view.model())
        return False     
   

    ## removes node element
    # \param element DOM node element to remove
    # \param parent parent node index      
    def _removeElement(self, element, parent):
        if self.view is not None and self.view.model() is not None: 
            return self.dts.removeElement(element, parent, self.view.model())



    ## replaces node element
    # \param oldElement old DOM node element 
    # \param newElement new DOM node element 
    # \param parent parent node index
    def _replaceElement(self, oldElement, newElement, parent):
        if self.view is not None and self.view.model() is not None: 
            return self.dts.replaceElement(oldElement, newElement, parent, self.view.model())
            


    ## appends node element
    # \param newElement new DOM node element 
    # \param parent parent node index      
    def _appendElement(self, newElement, parent):
        if self.view is not None and self.view.model() is not None: 
            return self.dts.appendElement(newElement, parent, self.view.model())

            
    ## updates the form
    # \brief abstract class
    def updateForm(self):
        pass


    ## updates the node
    # \brief abstract class
    def updateNode(self, index=QModelIndex()):
        pass
        

    ## creates GUI
    # \brief abstract class
    def createGUI(self):
        pass

        
    ## sets the form from the DOM node
    # \param node DOM node
    def setFromNode(self, node=None):
        pass



if __name__ == "__main__":
    import sys
    

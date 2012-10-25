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
## \file Merger.py
# Class for merging DOM component trees

from PyQt4.QtXml import QDomNode


from PyQt4.QtCore import QString, QThread
from PyQt4.QtGui import QDialog, QWidget, QLabel, QHBoxLayout

## merging error for wrong node structure
class IncompatibleNodeError(Exception): 
    ## constructor
    # \param value text of the error
    # \param nodes list of error related nodes
    def __init__(self, value, nodes = []):
        ## text of the error
        self.value = value
        ## list of error related nodes
        self.nodes = nodes
        ## selected node
        self.selectedNode = None
        
## dialog of the merger
class MergerDlg(QDialog):
    ## constructor
    # \param parent dialog
    def __init__(self,  parent=None):
        super(MergerDlg, self).__init__(parent)
        

    ## creates GUI
    # \brief It creates dialog with a merging label 
    def createGUI(self):
        label = QLabel(" Please be patient: Component merging...")
        layout = QHBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
        self.setWindowTitle("Merging")

## merges the components
class Merger(QThread):

    
    ## constructor
    # \param root  DOM root node
    def __init__(self, root):
        QThread.__init__(self)
        ## DOM root node
        self._root = root
        ## tags which cannot have the same siblings
        self._singles =['datasource', 'strategy', 'dimensions', 'definition',
                       'record', 'device', 'query', 'database', 'door']

        ## allowed children of the given nodes
        self._children ={
            "datasource":["record", "doc", "device", "database", "query", "door"],
            "attribute":["enumeration", "doc"],
            "definition":["group", "field", "attribute", "link", "component", "doc", "symbols"],
            "dimensions":["dim", "doc"],
            "field":["attribute", "datasource", "doc", "dimensions", "enumeration", "strategy"],
            "group":["group", "field", "attribute", "link", "component", "doc"],
            "link":["doc"]
            }


        self._requiredAttr ={
            "attribute":["name"],
            "definition":[],
            "dimensions":["rank"],
            "dim":["index", "value"],
            "field":["name"],
            "group":["type"],
            "link":["name","target"],
            "strategy":["mode"],
            "datasource":["type"],
            "record":["name"],
            "device":["member","name"],
            "database":["dbtype"],
            "query":["format"]
            }

        ## it contains an exeption instance when the exception was raised
        self.exception = None
        ## it has to be set on False when we want to break merging
        self.running = True

    ## fetches the text from all DOM child text nodes
    # \param node the given DOM node
    def _getText(self, node):
        text = QString()
        if node:
            child = node.firstChild()
            while not child.isNull():
                if child.nodeType() == QDomNode.TextNode:
                    text += child.toText().data()
                child = child.nextSibling()
        return text    


    ## fetches node ancestors int the tree
    # \param node the given DOM node
    # \returns string with node ancestors in the tree
    def _getAncestors(self, node):
        res = "" 
        attr = node.attributes()

        name = attr.namedItem("name").nodeValue() \
            if attr.contains("name") else ""

        if node.parentNode().nodeName() != '#document':
#            print node.nodeName()
            res =  self._getAncestors(node.parentNode()) 
        res += "/" + unicode(node.nodeName()) 
        if name:
            res += ":" + name
        return res 


    ## checks if the given node elements are mergeable
    # \param elem1 first node element
    # \param elem2 secound node element
    # \returns True if the given elements are mergeable
    def _areMergeable(self,elem1, elem2):
#        print "checking:" ,elem1.nodeName(), elem2.nodeName()
        if elem1.nodeName() != elem2.nodeName():
            return False
        tagName = unicode(elem1.nodeName())
        attr1 = elem1.attributes()
        attr2 = elem2.attributes()
        status = True
        tags = []

        name1 = attr1.namedItem("name").nodeValue() \
            if attr1.contains("name") else ""
        name2 = attr2.namedItem("name").nodeValue() \
            if attr1.contains("name") else ""
#        print "with names" ,name1,name2        

        if name1 != name2 :
            return False

        for i1 in range(attr1.count()):
            at1 = attr1.item(i1)
            for i2 in range(attr2.count()):
                at2 = attr2.item(i2)
                if at1.nodeName() == at2.nodeName() and at1.nodeValue() != at2.nodeValue():
                    status = False
                    tags.append((str(self._getAncestors(at1)),
                                 str(at1.nodeValue()) , str(at2.nodeValue())))

                    
            

        if not status  and tagName in self._singles: 
            raise IncompatibleNodeError("Incompatible element attributes  %s: " % str(tags),
                                        [elem1, elem2])
                


        if tagName == 'field':
            text1=unicode(self._getText(elem1)).strip()
            text2=unicode(self._getText(elem2)).strip()         
            ## TODO white spaces?
            if text1 != text2:
                raise IncompatibleNodeError(
                    "Incompatible \n%s element value\n%s \n%s "  \
                        % (str(self._getAncestors(elem1)), text1, text2),
                    [elem1, elem2])
                    
            
        return status


    ## merges the given node elements
    # \param elem1 first node element
    # \param elem2 secound node element
    def _mergeNodes(self,elem1, elem2):
        tagName = elem1.nodeName()
        attr1 = elem1.attributes()
        attr2 = elem2.attributes()
        texts = []

        for i2 in range(attr2.count()):
            at2 = attr2.item(i2)
            elem1.setAttribute(at2.nodeName(),at2.nodeValue())
        
            
        child1 = elem1.firstChild()
        while not child1.isNull(): 
            if child1.nodeType() == QDomNode.TextNode:
                texts.append(unicode(child1.toText().data()).strip())
            child1 = child1.nextSibling()    

        toMove = []    

        child2 = elem2.firstChild()
        while not child2.isNull(): 
            if child2.nodeType() == QDomNode.TextNode:
                if unicode(child2.toText().data()).strip() not in texts:
                    toMove.append(child2)
            else:    
                toMove.append(child2)
            child2 = child2.nextSibling()    

        for child in toMove:
            elem1.appendChild(child)
        toMove = []    


        parent = elem2.parentNode()    
        if self.selectedNode == elem2:
            selectedNode = elem1
        parent.removeChild(elem2)


    ## checks if the nodes has required attributes
    # \param node the given DOM node
    def _hasAttributes(self, node):
        elem1 = node.toElement()
        if elem1 is not None:
            attr1 = elem1.attributes()
            name1 = attr1.namedItem("name").nodeValue() \
                if attr1.contains("name") else ""
            if elem1.nodeName() in self._requiredAttr.keys():
                for at1 in self._requiredAttr[str(elem1.nodeName())]:
                    if not attr1.contains(at1) or not str(attr1.namedItem(at1).nodeValue()).strip():
                        message = "Not defined %s attribute of %s%s " \
                            % (at1, str(elem1.nodeName()), (":"+ str(name1)) if str(name1).strip() else  " ")
                        raise IncompatibleNodeError(message, [elem1])
        

    ## merge all children of the given DOM node
    # \param node the given DOM node
    def _mergeChildren(self, node):
        status = False
        if node:
            self._hasAttributes(node)

#            print "merging the children of: ", node.nodeName()
            changes = True            
            while changes and self.running:
                children = node.childNodes()
                changes = False
                for c1 in range(children.count()):
                    child1 = children.item(c1)
                    elem1 = child1.toElement()
                    for c2 in range(children.count()):
                        child2 = children.item(c2)
                        if child1 != child2:
                            elem2 = child2.toElement()
                            if elem1 is not None and elem2 is not None:
                                if self._areMergeable(elem1,elem2):
                                    self._mergeNodes(elem1, elem2)
                                    changes = True
                                    status = True
                        if changes:
                            break
                    if changes:
                        break
                        
            child = node.firstChild()
            elem = node.toElement()
            nName = unicode(elem.nodeName()) if elem else ""

            if elem and nName =='query':
                if not str(elem.text()).strip():
                    raise IncompatibleNodeError(
                        "Empty content of the query tag: %s" % (self._getAncestors(elem)),
                        [elem])
            
            if child:
                while not child.isNull() and self.running:
                    if nName and nName in self._children.keys():
                        childElem = child.toElement()
                        cName = unicode(childElem.nodeName()) if childElem  else ""
                        if cName and cName not in self._children[nName]:
                            raise IncompatibleNodeError(
                                "Not allowed <%s> child of \n < %s > \n parent"  \
                                    % (cName, self._getAncestors(elem)),
                                [childElem])
                                
                    self._mergeChildren(child)
                    child = child.nextSibling()


        

    ## runs thread
    # \brief It runs the mergeChildren with the root node and catches the exceptions if needed
    def run(self):
        if self._root:
            try:
                self._mergeChildren(self._root)
                if not self.running:
                    raise Exception("Merging Interrupted")
            except Exception, e:
                self.exception = e
            
if __name__ == "__main__":
    import sys

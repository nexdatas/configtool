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
## \file Command.py
# user commands of GUI application

from PyQt4.QtGui import *
from PyQt4.QtCore import *

## abstract command
class Command(object):
    
    ## constructor
    def __init__(self):
        pass

    ## 
    def execute(self):
        pass
    ## 
    def unexecute(self):
        pass

    def clone(self): 
        pass


class FileNewCommand(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self._slot = 'fileNew'
        self._textEdit = None
        
    def slot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)
    

    def execute(self):
        self._textEdit = QTextEdit()
        if hasattr(self.receiver,'mdi'):
            self._textEdit = QTextEdit()
            self.receiver.mdi.addWindow(self._textEdit)
            self._textEdit.setAttribute(Qt.WA_DeleteOnClose)
            self._textEdit.show()
            print "EXEC fileNew"

    def unexecute(self):
        self.receiver.mdi.setActiveWindow(self._textEdit)
        self.receiver.mdi.closeActiveWindow()
        print "UNDO fileNew"

    def clone(self):
        return FileNewCommand(self.receiver) 





class DataSourceNew(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self._slot = 'dsourceNew'
        self._textEdit = None
        
    def slot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)
    

    def execute(self):
        print "EXEC dsourceNew"

    def unexecute(self):
        print "UNDO dsourceNew"

    def clone(self):
        return DataSourceNew(self.receiver) 





class CloseApplication(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self._slot = 'closeApp'

    def slot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)
    

    def execute(self):
        if hasattr(self.receiver,'mdi'):
            self.receiver.close()
            print "EXEC closeApp"

    def unexecute(self):
        print "UNDO closeApp"

    def clone(self):
        return CloseApplication(self.receiver) 



class UndoCommand(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self._slot = 'undo'

    def slot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)
    

    def execute(self):
        print "EXEC undo"

    def unexecute(self):
        pass

    def clone(self):
        return UndoCommand(self.receiver) 

class ReundoCommand(Command):
    def __init__(self, receiver):
        self.receiver = receiver
        self._slot = 'reundo'

    def slot(self):
        if hasattr(self.receiver, self._slot):
            return  getattr(self.receiver, self._slot)
    

    def execute(self):
        print "EXEC reundo"

    def unexecute(self):
        pass

    def clone(self):
        return ReundoCommand(self.receiver) 


class SimpleCommand(Command):
    def __init__(self, receiver, action, undo=None):
        self.receiver = receiver
        self.action = action
        self.undo = undo
        
    def execute(self):
        if hasattr(self.receiver,self.action):
            obj = getattr(self.receiver, self.action)
            if callable(obj):
                obj()

    def unexecute(self):
        if hasattr(self.receiver,self.undo):
            obj = getattr(self.receiver, self.undo)
            if callable(obj):
                obj()

    def clone(self):
        return SimpleCommand(receiver, action, undo)


class TextCommand(Command):
    def __init__(self, receiver, action, originator=None, undo=None ):
        self.receiver = receiver
        self.action = action
        self.undo = undo
        self.originator = originator
        self._state = None
        
    def execute(self):
        if hasattr(self.originator,'createMemento'):
            self._state = self.originator.createMemento()
            
        if hasattr(self.receiver,self.action):
            obj = getattr(self.receiver, self.action)
            if callable(obj):
                obj()

    def unexecute(self):
        if hasattr(self.receiver,self.undo):
            obj = getattr(self.receiver, self.undo)
            if callable(obj):
                obj()
            if hasattr(self.originator,'setMemento'):
                self.originator.setMemento(self._state)

    def clone(self):
        return TextCommand(receiver, action, originator, undo)



class ActionClass(object):        
    def __init__(self):
        self.txt = []

    def myAction(self):
        self.txt.append("ACTION !!!")
        print "Action: ", self.txt

    def undo(self):
        self.txt.pop()
 #       print "Undo: ", self.txt


class TextMemento(object):
    def __init__(self, txt):
        self.txt = txt


class ActionMemClass(object):        
    def __init__(self):
        self.txt = "ROOT: "

    def createMemento(self):
        return TextMemento(self.txt) 
    
    def setMemento(self,memento):
        self.txt = memento.txt

    def myAction(self):
        self.txt += "ACTION !!!"
#        print "Action: ", self.txt

    def undo(self):
        pass


        

if __name__ == "__main__":
    import sys

    pool = []
    
    actionObj2 = ActionClass()
    actionObj = ActionMemClass()
    print actionObj.txt
    print actionObj2.txt

    print "EXEC"
    cmd = TextCommand(actionObj, 'myAction', actionObj, 'undo')
    cmd.execute()
    pool.append(cmd)
    print actionObj.txt

    print "EXEC"
    cmd = SimpleCommand(actionObj2, 'myAction', 'undo')
    cmd.execute()
    pool.append(cmd)
    print actionObj2.txt


    print "EXEC"
    cmd = TextCommand(actionObj, 'myAction', actionObj, 'undo')
    cmd.execute()
    pool.append(cmd)
    print actionObj.txt

    print "EXEC"
    cmd = SimpleCommand(actionObj2, 'myAction', 'undo')
    cmd.execute()
    pool.append(cmd)
    print actionObj2.txt


    while pool:

        print "UNEXEC"
        cmd = pool.pop()
        if cmd:
            cmd.unexecute()
            print actionObj.txt
            print actionObj2.txt
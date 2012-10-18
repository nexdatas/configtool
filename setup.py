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
## \file setup.py
# GUI to create the XML components 

import os, shutil, sys
from distutils.core import setup
from distutils.command.build import build
from distutils.command.clean import clean

TOOL = "ndtsconfigtool"
ITOOL = __import__(TOOL)

## reading a file
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

class toolBuild(build):

    def makeqrc(self, qfile, path):
        compiled = os.system("pyrcc4 %s/%s.qrc -o %s/qrc_%s.py" % (path, qfile, path, qfile))
        if compiled == 0:
            print "Built: %s/%s.qrc -> %s/qrc_%s.py" % (path, qfile, path, qfile)
        else:
            print "Warning: Cannot build  %s%s.qrc"  % (path, qfile)

    def makeui(self, ufile, path):
        compiled = os.system("pyuic4 %s/%s.ui -o %s/ui_%s.py" % (path, ufile, path, ufile))
        if compiled == 0:
            print "Compiled %s/%s.ui -> %s/ui_%s.py" % (path, ufile, path, ufile)
        else:
            print "Warning: Cannot build %s/ui_%s.py"  % (path, ufile)


    def run(self):
        build.run(self)
        try:
            ufiles = [(  ufile[:-3], "%s/ui" % TOOL ) for ufile 
                      in os.listdir("%s/ui" % TOOL) if ufile.endswith('.ui')]
            for ui in ufiles:
                if not ui[0] in (".", ".."):
                    self.makeui(ui[0], ui[1])
        except TypeError,e:
            print "No .ui files to build",e


        try:
            qfiles = [(  qfile[:-4], "%s/qrc" % TOOL) for qfile 
                      in os.listdir("%s/qrc" % TOOL) if qfile.endswith('.qrc')]
            for qrc in qfiles:
                if not qrc[0] in (".", ".."):
                    self.makeqrc(qrc[0], qrc[1])
        except TypeError:
            print "No .qrc files to build"


datas = [('components', ['*']), ('datasources', ['*'])]


## metadata for distutils
SETUPDATA=dict(
    name = "nexdatas.configtool",
    version = ITOOL.__version__,
    author = "Jan Kotanski, Eugen Wintersberger , Halil Pasic",
    author_email = "jankotan@gmail.com, eugen.wintersberger@gmail.com, halil.pasic@gmail.com",
    description = ("Configuration tool  for creating components"),
    license = "GNU GENERAL PUBLIC LICENSE, version 3",
    keywords = "configuration writer Tango component nexus data",
    url = "http://code.google.com/p/nexdatas/",
    packages=[TOOL],
    data_files = datas,
    scripts = ['ComponentDesigner.pyw'],
#    package_data={'ndts': ['TDS']},
    long_description= read('README'),
    cmdclass = {"build" : toolBuild}
)

## the main function
def main():
    setup(**SETUPDATA)
        
if __name__ == '__main__':
    main()

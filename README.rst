Welcome to nxsconfigtool's documentation!
=========================================

Authors: Jan Kotanski, Eugen Wintersberger, Halil Pasic

Component Designer is a GUI configuration tool dedicated to create components 
as well as datasources which constitute the XML configuration strings of 
Nexus Data Writer (NXS). The created XML elements can be saved 
in the extended Nexus XML format in Configuration Tango Server or in disk files.


Installation from sources
=========================


Install the dependencies:

    PyQt4, PyTango (optional) 

PyTango? is only needed if one wants to use Configuration Server

Download the latest NXS Configuration Tool version from

    NXS Component Designer 

and extract the sources.

One can also download the lastest version directly from the git repository by

git clone https://github.com/jkotan/nexdatas.configtool/

Next, run the installation script

$ python setup.py install


General overview
================


The NXS Component Designer program allows to creates components as well as 
datasources which constitute the XML configuration strings of 
Nexus Data Writer (NXS). The created XML elements can be saved 
in the extended Nexus XML format in Configuration Tango Server or in disk files.
 
The File menu is used to create new or load existing components and datasources. 
It also allows to save the currently edited XML elements in the local file system. 

The Edit menu offers the cut copy paste and apply options of edited component items. 

The Component Items menu contains adding new or loading existing component 
items as well as component merging and clearing. 

The options in the Server menu allows to connect to Configuration Server and 
fetch or store the created configuration XML elements in it. 

The View menu offers switches to show and hide the collection dock window 
with lists and to change display of the component tree columns. 

In the Window menu one can find standard window operations 
for applications with the multiple document interface. 

The Help menu offers information about the current Component Designer 
version as well as this detail help. 

Collection Dock Window contains lists of the currently open components 
and datasources. Selecting one of the components or datasources from 
the lists causes opening either Component Window or DataSource Window. 

All the most commonly used menu options are also available on Toolbar. 


Icons
=====

Icons fetched from http://findicons.com/pack/990/vistaico_toolbar.


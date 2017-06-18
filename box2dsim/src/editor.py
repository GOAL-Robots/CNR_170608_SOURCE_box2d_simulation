#!/usr/bin/env python
import copy
import math
import cPickle
import json
from PySide import QtCore, QtGui
import Box2D as b2
from Box2D.Box2D import b2_dynamicBody
from prompt_toolkit.layout import toolbars


class DataManager(object):
    pass


class MainWindow(QtGui.QMainWindow):
    def __init__(self, app):
        
        super(MainWindow, self).__init__()
        self.data_manager = DataManager()
              
        main = QtGui.QWidget(self)

        # windows 
           
        self.worldTable = QtGui.QTableWidget(self)
        self.drawingFrame = QtGui.QFrame(self)
        self.objectTables = QtGui.QWidget(self)
        self.objectMainTable = QtGui.QTableWidget(self)
        self.objectFixtureTable = QtGui.QTableWidget(self)

        self.setCentralWidget(main)
        mainLayout = QtGui.QHBoxLayout()
        main.setLayout(mainLayout)
                
        main.layout().addWidget(self.drawingFrame)
        main.layout().addWidget(self.worldTable)
        main.layout().addWidget(self.objectTables)
        
        self.drawingFrame.setFixedSize(600, 600)

        tablesLayout = QtGui.QVBoxLayout()
        self.objectTables.setLayout(tablesLayout)
        self.objectTables.layout().addWidget(self.objectMainTable)
        self.objectTables.layout().addWidget(self.objectFixtureTable)

        # toolbar
        toolBar = QtGui.QToolBar(self)
        self.addToolBar(toolBar)
   
        # main commands
        
        exitAction = QtGui.QAction('Exit', self)
        exitAction.setShortcut('Q')
        exitAction.triggered.connect(self.close)
        toolBar.addAction(exitAction)
 
        saveAction = QtGui.QAction('Save', self)
        saveAction.setShortcut('S')
        saveAction.triggered.connect(self.save)     
        toolBar.addAction(saveAction)

        loadAction = QtGui.QAction('Load', self)
        loadAction.setShortcut('L')
        loadAction.triggered.connect(self.load) 
        
        toolBar.addAction(loadAction)
        toolBar.addSeparator()

        # navigate/create/delete objects 
                
        newAction = QtGui.QAction('New', self)
        newAction.setShortcut('N')
        newAction.triggered.connect(self.newObject)    
        toolBar.addAction(newAction)
                
        prevAction = QtGui.QAction('Prev', self)
        prevAction.setShortcut('Left')
        prevAction.triggered.connect(self.prevObject)     
        toolBar.addAction(prevAction)
         
        nextAction = QtGui.QAction('Next', self)
        nextAction.setShortcut('Right')
        nextAction.triggered.connect(self.nextObject)   
        toolBar.addAction(nextAction)
 
        deleteAction = QtGui.QAction('delete', self)
        deleteAction.setShortcut('Delete')
        deleteAction.triggered.connect(self.deleteObject)    
        toolBar.addAction(deleteAction)
        
        toolBar.addSeparator()
      
        objects = QtGui.QActionGroup(self)
        objects.setExclusive(True)
        
        polygonAction = QtGui.QAction('Polygon', self)
        polygonAction.setShortcut('P')
        polygonAction.setCheckable(True)
        polygonAction.setChecked(True)
        polygonAction.triggered.connect(self.onPolygons)         
        toolBar.addAction(polygonAction)
        objects.addAction(polygonAction)
   
        circleAction = QtGui.QAction('Circle', self)
        circleAction.setShortcut('C')
        circleAction.setCheckable(True)
        circleAction.triggered.connect(self.onCircles)         
        toolBar.addAction(circleAction)
        objects.addAction(circleAction)
        
        jointAction = QtGui.QAction('Joint', self)
        jointAction.setShortcut('J')
        jointAction.setCheckable(True)
        jointAction.triggered.connect(self.onJoints)        
        toolBar.addAction(jointAction)
        objects.addAction(jointAction)
        
        self.addToolBarBreak()
        manualBar = QtGui.QToolBar(self)
        self.addToolBar(manualBar)
        

        polygonManual = QtGui.QActionGroup(self)
        polygonManual.setExclusive(True)
     
        addPointAction = QtGui.QAction('+', self)
        addPointAction.setShortcut('+')
        addPointAction.setCheckable(True)
        addPointAction.setChecked(True)
        addPointAction.triggered.connect(self.onAddPoints)         
        manualBar.addAction(addPointAction)
        polygonManual.addAction(addPointAction)   

        delPointAction = QtGui.QAction('-', self)
        delPointAction.setShortcut('-')
        delPointAction.setCheckable(True)
        delPointAction.triggered.connect(self.onDelPoints)         
        manualBar.addAction(delPointAction)
        polygonManual.addAction(delPointAction)  
        
    def save(self):
        print "Save"
    
    def load(self):
        print "Load"
        
    def newObject(self):
        print "New"
    
    def prevObject(self):
        print "Previous"
    
    def nextObject(self):
        print "next";
    
    def deleteObject(self):
        print "Delete"        
    
    def onPolygons(self):
        print "Poligoans"
        
    def onCircles(self):
        print "Circles"
        
    def onJoints(self):
        print "Joints"
 
    def onAddPoints(self):
        print "Add Points"
        
    def onDelPoints(self):
        print "Del Points"   
if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec_())


#!/usr/bin/env python
import copy
import math
import cPickle
import json
from PySide import QtCore, QtGui
import Box2D as b2
from Box2D.Box2D import b2_dynamicBody


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


    def save(self):
        print "Save"
    
    def load(self):
        print "Load"
        
#         polygonAction = QtGui.QAction('Polygon', self)
#         polygonAction.setShortcut('P')
#         polygonAction.setCheckable(True)
#         polygonAction.setChecked(True)
#         polygonAction.triggered.connect(self.drawing_frame.onPolygons)         
#         circleAction = QtGui.QAction('Circle', self)
#         circleAction.setShortcut('C')
#         circleAction.setCheckable(True)
#         circleAction.triggered.connect(self.drawing_frame.onCircles)         
#         jointAction = QtGui.QAction('Joint', self)
#         jointAction.setShortcut('C')
#         jointAction.setCheckable(True)
#         jointAction.triggered.connect(self.drawing_frame.onJoints)         
#         
#         newAction = QtGui.QAction('New', self)
#         newAction.setShortcut('N')
#         newAction.triggered.connect(self.drawing_frame.newShape)    
  
#                        
#         prevAction = QtGui.QAction('Prev', self)
#         prevAction.setShortcut('Left')
#         prevAction.triggered.connect(self.drawing_frame.prevShape)       
#         nextAction = QtGui.QAction('Next', self)
#         nextAction.setShortcut('Right')
#         nextAction.triggered.connect(self.drawing_frame.nextShape)   
#         
#         self.addPointsAction = QtGui.QAction('glue+', self)
#         self.addPointsAction.setShortcut('+')
#         self.addPointsAction.setCheckable(True)
#         self.addPointsAction.setChecked(True)
#         self.addPointsAction.triggered.connect(self.drawing_frame.onGluePlus)         
# 
#         self.delPointsAction = QtGui.QAction('glue-', self)
#         self.delPointsAction.setShortcut('-')
#         self.delPointsAction.setCheckable(True)
#         self.delPointsAction.triggered.connect(self.drawing_frame.onGlueMinus)         
#    
#         self.manualPolyModeAction = QtGui.QAction('Manual', self)
#         self.manualPolyModeAction.setShortcut('M')
#         self.manualPolyModeAction.setCheckable(True)
#         self.manualPolyModeAction.setChecked(True)
#         self.manualPolyModeAction.triggered.connect(self.drawing_frame.onPolyModeManual)         
# 
#         self.regularPolyModeAction = QtGui.QAction('Regular', self)
#         self.regularPolyModeAction.setShortcut('R')
#         self.regularPolyModeAction.setCheckable(True)
#         self.regularPolyModeAction.triggered.connect(self.drawing_frame.onPolyModeRegular)         
#         
#         self.vrtsBox = QtGui.QComboBox(self)
#         self.vrtsBox.addItems(["%d" % x for x in range(3,17) ])
#         self.vrtsBox.currentIndexChanged.connect(self.drawing_frame.onVrtxBoxChanged)
#         self.vrtsBox.setEnabled(False)    
#         self.angleBox = QtGui.QLineEdit(self)
#         validator = QtGui.QIntValidator()
#         self.angleBox.setValidator(validator)
#         self.angleBox.setMaxLength(4)   
#         self.angleBox.setEnabled(False)    
#         self.angleBox.textChanged.connect(self.drawing_frame.onAngleBoxChanged)
#         self.angleLabel = QtGui.QLabel("angle")
#         self.angleLabel.setEnabled(False)    
#         self.radiusBox = QtGui.QLineEdit(self)
#         validator = QtGui.QIntValidator()
#         self.radiusBox.setValidator(validator)
#         self.radiusBox.setMaxLength(4)   
#         self.radiusBox.setEnabled(False)    
#         self.radiusBox.textChanged.connect(self.drawing_frame.onRadiusBoxChanged)
#         self.radiusLabel = QtGui.QLabel("radius")
#         self.radiusLabel.setEnabled(False)    
# 
#         shapes = QtGui.QActionGroup(self)
#         shapes.addAction(polygonAction)
#         shapes.addAction(circleAction)
#         shapes.addAction(jointAction)
#         shapes.setExclusive(True)
#         
#         self.actionsGroup = QtGui.QActionGroup(self)
#         self.actionsGroup.addAction(self.addPointsAction)
#         self.actionsGroup.addAction(self.delPointsAction)   
#         
#         self.polyModeGroup = QtGui.QActionGroup(self)
#         self.polyModeGroup.addAction(self.manualPolyModeAction)
#         self.polyModeGroup.addAction(self.regularPolyModeAction)
# 
#         

#         toolBar.addSeparator()
#         toolBar.addAction(prevAction)
#         toolBar.addAction(nextAction)
#         toolBar.addSeparator()
#         toolBar.addAction(newAction)
#         toolBar.addAction(deleteAction)
#         toolBar.addAction(saveAction)
#         toolBar.addAction(loadAction)
#         toolBar.addSeparator()
#         toolBar.addAction(polygonAction)
#         toolBar.addAction(circleAction)
#         toolBar.addAction(jointAction) 
#         toolBar.addSeparator()
#         self.addToolBar(toolBar)
#         self.addToolBarBreak()
#         
#         self.manualBar = QtGui.QToolBar(self)
#         self.manualBar.addAction(self.manualPolyModeAction)
#         self.manualBar.addAction(self.addPointsAction)
#         self.manualBar.addAction(self.delPointsAction)
#         self.addToolBar(self.manualBar)
#           
#         self.regularBar = QtGui.QToolBar(self)
#         self.regularBar.addAction(self.regularPolyModeAction)
#         self.regularBar.addWidget(self.vrtsBox)
#         self.regularBar.addWidget(self.angleLabel)
#         self.regularBar.addWidget(self.angleBox)
#         self.regularBar.addWidget(self.radiusLabel)
#         self.regularBar.addWidget(self.radiusBox)
#         self.addToolBar(self.regularBar)
#                
#         self.modifyBar = QtGui.QToolBar(self)
#         self.addToolBar(self.modifyBar)


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec_())


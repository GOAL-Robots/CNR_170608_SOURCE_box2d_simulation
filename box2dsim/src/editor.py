#!/usr/bin/env python
import copy
import math
import json
from PySide import QtCore, QtGui
import Box2D as b2



def intersect(a, b):
    ''' create a set with all the elements intersecting two containers    
    '''
    
    return set(a) & set(b)

def toPoint(dVec): 
    ''' Convert from dictionary to QPointF
    
    :param dVec: dictionary with x an y 
    :type dVec: dict()
    
    :return: Qt point
    :rtype: QtCore.QPointF
    '''
    return QtCore.QPointF(dVec['x'], dVec['y'])  

def fromPoint(qVec):
    ''' Convert from QPointF to dictionary
    
    :param qVec: Qt point
    :type qVec: QtCore.QPointF  
    
    :return: dictionary with x an y 
    :rtype: dict()
    '''
    return {'x': qVec.x(), 'y': qVec.y()}

def toPointVect(dArray):
    ''' Convert form dictionary to vector of QPoints
    
    :param dictionary with x an y keys
    :type dArray: dict()
    
    :return: a list of QpointF
    :rtype: list(QtCore.QPointf)
    '''

    return [ QtCore.QPointF(x, y)  
            for x,y in zip(dArray['x'], dArray['y'])]
            
def fromPointVect(qArray):
    ''' Convert form a list of QPoint to dictionary
    
    :param qArray: a list of QpointF
    :type qArray: list(QtCore.QPointf)
    
    :return: dictionary with x an y keys
    :rtype:  dArray: dict()
    '''
    return {'x': [p.x() for p in qArray],  
            'y': [p.y() for p in qArray]}


class DataObject(object):
    
    def __init__(self):
        self.data = dict()
        
    def __call__(self):
        return self.data
      

class World(DataObject):
    
    def __init__(self):
        
        super(World, self).__init__()
        
        self.data["gravity"] = {"x":0, "y":0} 
        self.data["positionIterations"] = 2 
        self.data["velocityIterations"] = 6 
        self.data["stepsPerSecond"] = 60 
        self.data["allowSleep"] = True 
        self.data["autoClearForces"] = True 
        self.data["warmStarting"] = True 
        self.data["continuousPhysics"] = True 
        self.data["subStepping"] = False 

        
class Body(DataObject):
    
    def __init__(self):
        
        super(Body, self).__init__()

        self.data["name"] = ""
        self.data["allowSleep"] = True
        self.data["angle"] = 0.0
        self.data["angularDamping"] = 0.0
        self.data["angularVelocity"] = 0.0
        self.data["awake"] = True
        self.data["bullet"] = False
        self.data["fixedRotation"] = False
        self.data["linearDamping"] = 0.0
        self.data["linearVelocity"] = {"x":0, "y":0} 
        self.data["position"] = {"x":0, "y":0} 
        self.data["type"] = 2
        self.data["awake"] = True
        
        

class Fixture(DataObject):
    
    def __init__(self):
        
        super(Fixture, self).__init__()

        self.data["name"] = ""
        self.data["allowSleep"] = True
        self.data["angle"] = 0.0
        self.data["angularDamping"] = 0.0
        self.data["angularVelocity"] = 0.0
        self.data["awake"] = True
        self.data["bullet"] = False
        self.data["fixedRotation"] = False
        self.data["linearDamping"] = 0.0
        self.data["linearVelocity"] = {"x":0, "y":0} 
        self.data["position"] = {"x":0, "y":0} 
        self.data["type"] = 2
        self.data["awake"] = True
        
class Circle(DataObject):
    
    def __init__(self):
        
        super(Circle, self).__init__()
        
        self.data["center"] = {"x":0, "y":0} 
        self.data["radius"] = 0

class Polygon(DataObject):
    
    def __init__(self):
        
        super(Polygon, self).__init__()

        self.data["vertices"] = {"x":[], "y":[]} 
        
class Joint(DataObject):

    def __init__(self):
        
        super(Joint, self).__init__()
        
        self.data["type"] = "revolute"
        self.data["name"] = ""
        self.data["anchorA"] = {"x":0, "y":0}
        self.data["anchorB"] = {"x":0, "y":0}
        self.data["bodyA"] = 0
        self.data["bodyB"] = 0
        self.data["collideConnected"] = True
        self.data["enableLimit"] = True
        self.data["enableMotor"] = True
        self.data["jointSpeed"] = 0
        self.data["lowerLimit"] = 0
        self.data["maxMotorTorque"] = 0
        self.data["motorSpeed"] = 0
        self.data["refAngle"] = 0
        self.data["upperLimit"] = 0       
    
class DataManager(object):
    
    def __init__(self):
        
        self.world = World()
        self.polygons = []
        self.circles = []
        self.joints = []
        
        self.current_polygon = None
        self.current_circle = None        
        self.current_joint = None

    def addPolygon(self, body, fixture, poly):
        
        fixture()["polygon"] = poly()
        body()["fixture"] = fixture()
        self.polygons.append(body())
        self.current_polygon = len(self.polygons) - 1
    
    def addCircle(self, body, fixture, circle):
        
        fixture()["circle"] = circle()
        body()["fixture"] = fixture()
        self.circles.append(body())
        self.current_circle = len(self.circles) - 1

    def addJoint(self, joint):
        
        self.joints.append(joint())
        self.current_joint = len(self.joints) - 1

    def loadFromFile(self, filePathName):
        
        # load json into memory
        with open(filePathName, "r") as json_file:
            jsw = json.load(json_file)
        
        # load world
        for key in intersect(self.world.data.keys(), jsw.keys()):
                self.world.data[key] = jsw[key]
            
        # load bodies    
        for jw_body in jsw["body"]:
            dm_body = Body()()
            for key in intersect(dm_body.keys(), jw_body.keys()):
                    dm_body[key] = jw_body[key]
            dm_body_fixture = Fixture()()
            jw_body_fixture = jw_body["fixture"][0]
            for key in intersect(dm_body_fixture.keys(), jw_body_fixture.keys()):
                    dm_body_fixture[key] = jw_body_fixture[key]
            
            if "polygon" in jw_body_fixture.keys():
                jw_body_poly = jw_body_fixture["polygon"]
                dm_body_poly = Polygon()()
                for key in intersect(dm_body_poly.keys(),  jw_body_poly.keys()):
                        dm_body_poly[key] = jw_body_poly[key]
                dm_body_fixture["polygon"] = dm_body_poly
                self.polygons.append(dm_body)

            elif "circle" in jw_body_fixture.keys():
                jw_body_circle = jw_body_fixture["circle"]
                dm_body_circle = Polygon()()
                for key in intersect(dm_body_circle.keys(),  jw_body_circle.keys()):
                        dm_body_circle[key] = jw_body_circle[key]
                dm_body_fixture["circle"] = dm_body_circle
                self.circles.append(dm_body)
            
            if not "body" in self.world.data.keys() :
                self.world.data["body"] = []
            self.world.data["body"].append(dm_body)   
            
        
        # load joints
        for jw_joint in jsw["joint"]:
            dm_joint = Joint()()
            for key in intersect(dm_joint.keys(), jw_joint.keys()):
                dm_joint[key] = jw_joint[key]
            self.joints.append(dm_joint)
            if not "joint" in self.world.data.keys() :
                self.world.data["joint"] = []
            self.world.data["joint"].append(dm_joint)   

            
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
 
        deleteAction = QtGui.QAction('Delete', self)
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
        self.editBar = QtGui.QToolBar(self)
        self.addToolBar(self.editBar)
        

        polygonEdit = QtGui.QActionGroup(self)
        polygonEdit.setExclusive(True)
     
        self.manualAction = QtGui.QAction('Manual', self)
        self.manualAction.setShortcut('M')
        self.manualAction.setCheckable(True)
        self.manualAction.setChecked(True)
        self.manualAction.triggered.connect(self.onManual)         
        self.editBar.addAction(self.manualAction)  
        polygonEdit.addAction(self.manualAction)   
        self.editBar.addSeparator()
        
        self.regularAction = QtGui.QAction('Regular', self)
        self.regularAction.setShortcut('M')
        self.regularAction.setCheckable(True)
        self.regularAction.triggered.connect(self.onRegular)         
        self.editBar.addAction(self.regularAction)         
        polygonEdit.addAction(self.regularAction)   
        
        self.addToolBarBreak()
        self.manualBar = QtGui.QToolBar(self)
        self.addToolBar(self.manualBar)
             
        polygonManual = QtGui.QActionGroup(self)
        polygonManual.setExclusive(True)
        
        self.addPointAction = QtGui.QAction('Add points', self)
        self.addPointAction.setShortcut('+')
        self.addPointAction.setCheckable(True)
        self.addPointAction.setChecked(True)
        self.addPointAction.triggered.connect(self.onAddPoints)         
        self.manualBar.addAction(self.addPointAction)
        polygonManual.addAction(self.addPointAction)   

        self.delPointAction = QtGui.QAction('Delete points', self)
        self.delPointAction.setShortcut('-')
        self.delPointAction.setCheckable(True)
        self.delPointAction.triggered.connect(self.onDelPoints)         
        self.manualBar.addAction(self.delPointAction)
        polygonManual.addAction(self.delPointAction)  
        self.editBar.addSeparator()

        self.addToolBarBreak()
        self.regularBar = QtGui.QToolBar(self)
        self.addToolBar(self.regularBar)
        self.regularBar.setVisible(False)
  
        self.verticesBoxLabel = QtGui.QLabel("vertices")
        self.verticesBoxLabel.setEnabled(False)  
        self.regularBar.addWidget(self.verticesBoxLabel)
                 
        self.verticesBox = QtGui.QComboBox(self)
        self.verticesBox.addItems(["%d" % x for x in range(3,17) ])
        self.verticesBox.currentIndexChanged.connect(self.onVertNumberBoxChanged)
        self.verticesBox.setEnabled(False) 
        self.regularBar.addWidget(self.verticesBox)                  

        self.angleBoxLabel = QtGui.QLabel("angle")
        self.angleBoxLabel.setEnabled(False)    
        self.regularBar.addWidget(self.angleBoxLabel)          
        
        self.angleBox = QtGui.QLineEdit(self)
        validator = QtGui.QIntValidator()
        self.angleBox.setValidator(validator)
        self.angleBox.setMaxLength(4)   
        self.angleBox.setEnabled(False)
        self.angleBox.textChanged.connect(self.onAngleBoxChanged)
        self.regularBar.addWidget(self.angleBox)          

        self.radiusBoxLabel = QtGui.QLabel("radius")
        self.radiusBoxLabel.setEnabled(False)   
        self.regularBar.addWidget(self.radiusBoxLabel)          
 
        self.radiusBox = QtGui.QLineEdit(self)
        validator = QtGui.QIntValidator()
        self.radiusBox.setValidator(validator)
        self.radiusBox.setMaxLength(4)   
        self.radiusBox.setEnabled(False)    
        self.radiusBox.textChanged.connect(self.onRadiusBoxChanged)
        self.regularBar.addWidget(self.radiusBox)   
      
    def updateTables(self):
          
        
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
        self.editBar.setVisible(True)
        if self.manualAction.isChecked():
            self.manualBar.setVisible(True)
            self.regularBar.setVisible(False)
        else:
            self.manualBar.setVisible(False)
            self.regularBar.setVisible(True)     
    def onCircles(self):
        print "Circles"
        self.editBar.setVisible(False)
        self.manualBar.setVisible(False)
        self.regularBar.setVisible(False)
             
    def onJoints(self):
        print "Joints"
        self.editBar.setVisible(False)
        self.manualBar.setVisible(False)
        self.regularBar.setVisible(False)
        
    def onAddPoints(self):
        print "Add Points"
        
    def onDelPoints(self):
        print "Del Points"   
    
    def onManual(self):
        print "Manual" 
        self.manualBar.setVisible(True)
        self.regularBar.setVisible(False)

        self.addPointAction.setEnabled(True) 
        self.delPointAction.setEnabled(True) 
        self.verticesBoxLabel.setEnabled(False)
        self.verticesBox.setEnabled(False)
        self.angleBoxLabel.setEnabled(False)
        self.angleBox.setEnabled(False)
        self.radiusBoxLabel.setEnabled(False)
        self.radiusBox.setEnabled(False)
            
    def onRegular(self):
        print "Regular"  
        self.manualBar.setVisible(False)
        self.regularBar.setVisible(True)
       
        self.addPointAction.setEnabled(False) 
        self.delPointAction.setEnabled(False) 
        self.verticesBoxLabel.setEnabled(True)
        self.verticesBox.setEnabled(True)
        self.angleBoxLabel.setEnabled(True)
        self.angleBox.setEnabled(True)
        self.radiusBoxLabel.setEnabled(True)
        self.radiusBox.setEnabled(True)
        
        
    def onVertNumberBoxChanged(self):
        print "Change vertices"

    def onAngleBoxChanged(self):
        print "Change angle"
        
    def onRadiusBoxChanged(self):
        print "Change radius"
                             
if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec_())


#!/usr/bin/env python
import json
from PySide import QtCore, QtGui
import Box2D as b2
import math

#------------------------------------------------------------------------------ 
# Utilities

def distance(p1, p2):
    return math.sqrt( (p2.x()-p1.x())**2 + (p2.y()-p1.y())**2)

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
            for x, y in zip(dArray['x'], dArray['y'])]
            
def fromPointVect(qArray):
    ''' Convert form a list of QPoint to dictionary
    
    :param qArray: a list of QpointF
    :type qArray: list(QtCore.QPointf)
    
    :return: dictionary with x an y keys
    :rtype:  dArray: dict()
    '''
    return {'x': [p.x() for p in qArray],
            'y': [p.y() for p in qArray]}

def to_b2Vec2(dict_vertices):
    ''' cinvert form dict to b2Vec2
    
    :param dict_vertices: dictionary with an x and y array item
    :type dict_vertices: dict()
    
    :return: a list of b2Vec2
    :rtype: list(b2Vec2, ...)
    '''
    return [ b2.b2Vec2(x, y) for (x,y) in 
            zip(dict_vertices['x'],dict_vertices['y']) ]

def from_b2Vec2(b2_vertices):  # @DontTrace
    ''' cinvert form  b2Vec2 to dict
    
    :param b2_vertices: list of b2Vec2
    :type b2_vertices: list(b2Vec2, ...)
    
    :return: dictionary with an x and y array item
    :rtype: dict 
    '''
  
    return {'x':[x for x,_ in b2_vertices],
            'y':[y for _,y in b2_vertices] }


#------------------------------------------------------------------------------ 
# These classes define objects that manage a database of json box2d objects

class DataObject(object):
    ''' Defines a common dictionary and a functor operator
        for inherited types
    '''
    class Types(object):
        POLYGON = 1
        CIRCLE = 2
        JOINT = 3
    
    def __init__(self):
        self.data = dict()
        
    def __call__(self):
        return self.data
      

class World(DataObject):
    ''' Manage box2d world info
    '''
    
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
    ''' Manage box2d body info
    '''
    
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
    ''' Manage box2d fixture info
    '''
    
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
    ''' Manage box2d Circle shape info
    '''
    
    def __init__(self):
        
        super(Circle, self).__init__()
        
        self.data["center"] = {"x":0, "y":0} 
        self.data["radius"] = 0

class Polygon(DataObject):
    ''' Manage box2d Polygon shape info
    '''    
    def __init__(self):
        
        super(Polygon, self).__init__()

        self.data["vertices"] = {"x":[], "y":[]} 
        
class Joint(DataObject):
    ''' Manage box2d joint info
    '''
    def __init__(self):
        
        super(Joint, self).__init__()
        
        self.data["type"] = "revolute"
        self.data["name"] = ""
        self.data["localAnchorA"] = {"x":0, "y":0}
        self.data["localAnchorB"] = {"x":0, "y":0}
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
    ''' Use the database objects (see above) to manage
        all editor data
    '''
    
    def __init__(self):
        
        self.world = World()
        self.polygons = []
        self.circles = []
        self.joints = []
        
        self.curr_object_type = None
        self.curr_idx = None
        self.current_polygon = None
        self.current_circle = None        
        self.current_joint = None

    def getcurrPolyPoints(self):
        if self.current_polygon is not None:
            dPoints = self.current_polygon['fixture'][0]['polygon']['vertices']
            return dPoints
        return None

    def getAllPolyPoints(self):
        
        v_dPoints = []
        for poly in self.polygons:
            dPoints = poly['fixture'][0]['polygon']['vertices']
            v_dPoints.append( dPoints )
            
        return v_dPoints

    def addPolygon(self, body, fixture, poly):
        ''' Add a polygon body to the data
        
        :param body: contains body info
        :type body: Body
        
        :param fixture: contains info about the fixture
        :type fixture: Fixture
        
        :param poly: contains info about the polygon shape
        :type poly: Polygon
        '''
        
        fixture()["polygon"] = poly()
        body()["fixture"] = [fixture()]
        self.polygons.append(body())
        self.current_polygon = self.polygons[-1]
        self.curr_idx = len(self.polygons) - 1
    
    def addCircle(self, body, fixture, circle):
        ''' Add a circle body to the data
        
        :param body: contains body info
        :type body: Body
        
        :param fixture: contains info about the fixture
        :type fixture: Fixture
        
        :param poly: contains info about the circle shape
        :type poly: Circle
        '''
        
        fixture()["circle"] = circle()
        body()["fixture"] = fixture()
        self.circles.append(body())
        self.current_circle = self.circles[-1]
        self.curr_idx = len(self.circles) - 1

    def addJoint(self, joint):
        ''' Add a joint to the data
        
        :param joint: contains joint info
        :type joint: Body
        
        '''
        
        self.joints.append(joint())
        self.current_joint = self.joints[-1]
        self.curr_idx = len(self.joints) - 1
    
    def nextObject(self):
        
        if self.curr_object_type == DataObject.Types.POLYGON :
            if self.polygons is not None:
                self.curr_idx = (self.curr_idx + 1) % len(self.polygons)
                self.current_polygon = self.polygons[self.curr_idx]
                
        elif self.curr_object_type == DataObject.Types.CIRCLE :
            if self.circles is not None:
                self.curr_idx = (self.curr_idx + 1) % len(self.circles)
                self.current_circle = self.circles[self.curr_idx]
 
        elif self.curr_object_type == DataObject.Types.JOINT :
            if self.joints is not None:
                self.curr_idx = (self.curr_idx + 1) % len(self.joints)
                self.current_joint = self.joints[self.curr_idx]

    def prevObject(self):
        
        if self.curr_object_type == DataObject.Types.POLYGON :
            if self.polygons is not None:
                self.curr_idx = (self.cur_idx - 1) % len(self.polygons)
                self.current_polygon = self.polygons[self.curr_idx]
                
        elif self.curr_object_type == DataObject.Types.CIRCLE :
            if self.circles is not None:
                self.curr_idx = (self.cur_idx - 1) % len(self.circles)
                self.current_circle = self.circles[self.curr_idx]
 
        elif self.curr_object_type == DataObject.Types.JOINT :
            if self.joints is not None:
                self.curr_idx = (self.cur_idx - 1) % len(self.joints)
                self.current_joint = self.joints[self.curr_idx]
  

    def loadFromFile(self, filePathName):
        ''' Load data from json file
        
        :param filePathName: the path of the json file
        :type filePathName: string
        '''
        
        # load json into memory
        with open(filePathName, "r") as json_file:
            jsw = json.load(json_file)
        
        # load world
        for key in intersect(self.world.data.keys(), jsw.keys()):
                self.world()[key] = jsw[key]
            
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
                for key in intersect(dm_body_poly.keys(), jw_body_poly.keys()):
                        dm_body_poly[key] = jw_body_poly[key]
                dm_body_fixture["polygon"] = dm_body_poly
                self.polygons.append(dm_body)

            elif "circle" in jw_body_fixture.keys():
                jw_body_circle = jw_body_fixture["circle"]
                dm_body_circle = Polygon()()
                for key in intersect(dm_body_circle.keys(), jw_body_circle.keys()):
                        dm_body_circle[key] = jw_body_circle[key]
                dm_body_fixture["circle"] = dm_body_circle
                self.circles.append(dm_body)
            
            if not "body" in self.world().keys() :
                self.world()["body"] = []
            self.world()["body"].append(dm_body)   
                 
        # load joints
        for jw_joint in jsw["joint"]:
            dm_joint = Joint()()
            for key in intersect(dm_joint.keys(), jw_joint.keys()):
                dm_joint[key] = jw_joint[key]
            self.joints.append(dm_joint)
            if not "joint" in self.world.data.keys() :
                self.world.data["joint"] = []
            self.world.data["joint"].append(dm_joint)   

#------------------------------------------------------------------------------ 
# Defining the GUI

class Table(QtGui.QTableWidget):
    ''' A Table object to visualize the body2d data in the data_manager. 
        Customized from QTableWidget.
        
        include the recursive method addItems, if an item is a dictionary
        recursively build a Table object
    '''
    
    def __init__(self, rows=0, cols=0, deep=1, initial_width=600, parent=None):
        '''
        
        :param rows: the number of initial rowws
        :type rows: int
        
        :param cols: the number of columns
        :type cols: int
        
        :param deep: an index defining the initial depth of the created table object.
                     1 indicates that it is a top-level table.
        :type deep: int
        
        :param initial_width: the width of a top-level table row
        :type initial_width: int
        
        :param parent: the parent widget (form QWidget init)
        :type parent: QWidget
        '''
        
        super(Table, self).__init__(rows, cols, parent) 
        self.deep = deep
        self.horizontalHeader().hide()
        self.verticalHeader().hide()  
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.initial_width = initial_width
        
    def addWItems(self, mainTable, data, deep_discount=100):
        '''
        :param mainTable: the upper level table that contains this table as an item
        :type mainTable: Table
        
        :param deep_discount: at each depth level the table row width is lowered by this factor
        :type deep_discount: int
        
        :param data: the data to insert in this table
        :type data: dict
        '''
        
        for row, (key, value) in enumerate(data.iteritems()):
            mainTable.insertRow(row)
            mainTable.setRowCount(row + 1)
            mainTable.setItem(row, 0, QtGui.QTableWidgetItem(key))
            if type(value) is not type(dict()):
                mainTable.setItem(row, 1, QtGui.QTableWidgetItem(str(value)))
            else:
                table = Table(len(value.keys()), 2, mainTable.deep + 1)
                self.addWItems(table, value)                                
                table.resizeColumnsToContents()
                mainTable.setRowHeight(row, table.rowHeight(0) * 1.2 * len(value.keys()))
                mainTable.setCellWidget(row, 1, table)
            mainTable.setFixedWidth(self.initial_width - self.deep * deep_discount)
            mainTable.resizeColumnsToContents()   
              
    def updateTable(self, data, exclude=None):
        ''' update the contents of the table
        
        :param data: the data to insert in this table
        :type data: dict
        
        :param exclude: the item to exclude from insertion
        :type exclude: string
        '''
          
        selected_data = data
        if exclude is not None:
            selected_data = { key:value 
                             for  key, value in selected_data.iteritems() 
                             if key != exclude}
            
        self.addWItems(self, selected_data)
        self.update()
        
    def resizeEvent(self, event):
        ''' resize policy
        '''
        
        self.resizeRowsToContents()
        super(Table, self).resizeEvent(event)

#------------------------------------------------------------------------------ 

class Screen(QtGui.QFrame):
    def __init__(self, data_manager, parent=None):
        '''
        
        :param data_manager:
        :type data_manager:
        
        :param parent:
        :type parent:
        '''
        super(Screen, self).__init__(parent)
        
        self.parent_obj = parent
        self.data_manager = data_manager
        
        self.WINDOW_BOTTOM = 0.0 
        self.WINDOW_LEFT = 0.0
        self.WINDOW_WIDTH = 20.0
        self.WINDOW_HEIGHT = 20.0

    def scalePoint(self, point):

        w = float(self.size().width())
        h = float(self.size().height())
        return QtCore.QPointF(
                (point.x() / w) * self.WINDOW_WIDTH,
                self.WINDOW_HEIGHT - (point.y() / h) * self.WINDOW_HEIGHT)

    def test_polygon(self):
        # test 
        curr_polygon = self.data_manager.current_polygon
        curr_vertices = curr_polygon['fixture'][0]['polygon']['vertices']
        print curr_vertices
        if len(curr_vertices['x']) > 3:
            b2polygon = b2.b2PolygonShape(vertices=to_b2Vec2(curr_vertices))   
            if b2polygon is not None:
                corrected = from_b2Vec2(b2polygon.vertices) 
                curr_vertices['x'] = corrected['x']
                curr_vertices['y'] = corrected['y']
                curr_polygon['position']= {'x':b2polygon.centroid.x,  
                                           'y':b2polygon.centroid.y}             

    def rescalePoint(self, point):
        
        w = float(self.size().width())
        h = float(self.size().height())
        return QtCore.QPointF(
                point.x() * w / self.WINDOW_WIDTH,
                (self.WINDOW_HEIGHT - point.y()) * h / self.WINDOW_HEIGHT)
        
    def mousePressEvent(self, event):
        scaledPos = self.scalePoint(event.pos())
        if self.parent_obj.polygon_manual_addpoint == True:
            if self.data_manager.current_polygon is None:
                self.parent_obj.newObject()
                dPoints = self.data_manager.getcurrPolyPoints()
                dPoints['x'] = [scaledPos.x()]
                dPoints['y'] = [scaledPos.y()]
            else:
                dPoints = self.data_manager.getcurrPolyPoints()
                dPoints['x'].append(scaledPos.x())
                dPoints['y'].append(scaledPos.y())
            self.test_polygon()
        self.update()
                                                        
    def mouseReleaseEvent(self, event):
        scaledPos = self.scalePoint(event.pos())
        if self.parent_obj.polygon_manual_addpoint == True:
            dPoints = self.data_manager.getcurrPolyPoints()
            curr_pos = event.pos()
            if curr_pos.x() != dPoints['x'][-1] or \
                curr_pos.y() != dPoints['y'][-1] :
                dPoints['x'].append(scaledPos.x())
                dPoints['y'].append(scaledPos.y())
            self.test_polygon()
        self.update()
                                
    def mouseMoveEvent(self, event):
        scaledPos = self.scalePoint(event.pos())
        if self.parent_obj.polygon_manual_addpoint == True:
            dPoints = self.data_manager.getcurrPolyPoints()
            curr_pos = event.pos()
            last_pos = toPointVect(dPoints)[-1]
            if distance(curr_pos, last_pos) < 0.1 :
                dPoints['x'][-1] = scaledPos.x()
                dPoints['y'][-1] = scaledPos.y()
            self.test_polygon()
        self.update()

    def paintEvent(self, event):

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)         
        
        for vertices in self.data_manager.getAllPolyPoints():
            if len(vertices['x']) > 0:
                X = vertices['x'] + [vertices['x'][0]]
                Y = vertices['y'] + [vertices['y'][0]]
                vs = [QtCore.QPointF(x,y) for x,y in zip(X, Y)]
                
                for idx in xrange(1,len(vs)):
                    prev_point = vs[idx-1]
                    next_point = vs[idx]
                    painter.drawLine(
                        self.rescalePoint(prev_point),
                        self.rescalePoint(next_point))
           
#------------------------------------------------------------------------------ 
            
class MainWindow(QtGui.QMainWindow):
    ''' the GUI
    '''
    def __init__(self, app):
        
        super(MainWindow, self).__init__()
        self.data_manager = DataManager()
              
        main = QtGui.QWidget(self)
        
        self.polygon_manual_addpoint = True
        self.polygon_manual_delpoint = False
        self.circle_add = False

        # windows 
           
        self.drawingFrame = Screen(self.data_manager, self)
        self.objectTables = QtGui.QWidget(self)
        self.worldTable = Table(rows=0, cols=2, parent=self)
        self.worldTable.horizontalHeader().hide()
        self.worldTable.verticalHeader().hide()
        self.objectMainTable = Table(rows=0, cols=2, parent=self)
        self.objectMainTable.horizontalHeader().hide()
        self.objectMainTable.verticalHeader().hide()
        self.objectFixtureTable = Table(rows=0, cols=2, parent=self)
        self.objectFixtureTable.horizontalHeader().hide()
        self.objectFixtureTable.verticalHeader().hide()
        
        self.setCentralWidget(main)
        mainLayout = QtGui.QHBoxLayout()
        main.setLayout(mainLayout)
                
        main.layout().addWidget(self.drawingFrame)
        
        vWidget = QtGui.QWidget(self)
        vLayout = QtGui.QVBoxLayout()
        vLayout.addWidget(QtGui.QLabel("world"))
        vLayout.addWidget(self.worldTable)
        vWidget.setLayout(vLayout)
        main.layout().addWidget(vWidget)
        
        vWidget = QtGui.QWidget(self)
        vLayout = QtGui.QVBoxLayout()
        vLayout.addWidget(QtGui.QLabel("current object"))
        vLayout.addWidget(self.objectTables)
        vWidget.setLayout(vLayout)
        main.layout().addWidget(vWidget)
        
        self.drawingFrame.setFixedSize(600, 600)

        tablesLayout = QtGui.QVBoxLayout()
        self.objectTables.setLayout(tablesLayout)
        self.objectTables.layout().addWidget(self.objectMainTable)
        self.objectTables.layout().addWidget(self.objectFixtureTable)
        self.objectTables.setSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Expanding)
        
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
      
        self.objects = QtGui.QActionGroup(self)
        self.objects.setExclusive(True)
        
        self.polygonAction = QtGui.QAction('Polygon', self)
        self.polygonAction.setShortcut('P')
        self.polygonAction.setCheckable(True)
        self.polygonAction.setChecked(True)
        self.polygonAction.triggered.connect(self.onPolygons)         
        toolBar.addAction(self.polygonAction)
        self.objects.addAction(self.polygonAction)
   
        self.circleAction = QtGui.QAction('Circle', self)
        self.circleAction.setShortcut('C')
        self.circleAction.setCheckable(True)
        self.circleAction.triggered.connect(self.onCircles)         
        toolBar.addAction(self.circleAction)
        self.objects.addAction(self.circleAction)
        
        self.jointAction = QtGui.QAction('Joint', self)
        self.jointAction.setShortcut('J')
        self.jointAction.setCheckable(True)
        self.jointAction.triggered.connect(self.onJoints)        
        toolBar.addAction(self.jointAction)
        self.objects.addAction(self.jointAction)
        
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
        self.verticesBox.addItems(["%d" % x for x in range(3, 17) ])
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
        
        self.data_manager.curr_object_type = DataObject.Types.POLYGON
        
        self.updateTables()

      
    def updateTables(self):

        self.worldTable.setRowCount(0)            
        self.worldTable.updateTable(self.data_manager.world())
        
        if self.data_manager.curr_object_type == DataObject.Types.POLYGON:
            if self.data_manager.current_polygon is not None:
                self.objectMainTable.setRowCount(0)
                self.objectMainTable.updateTable(
                    self.data_manager.current_polygon, exclude="fixture")
                self.objectFixtureTable.setRowCount(0)
                self.objectFixtureTable.updateTable(
                    self.data_manager.current_polygon["fixture"][0])                
        
    def save(self):
        print "Save"
    
    def load(self):
        print "Load"
        
    def newObject(self):
        
        if self.objects.checkedAction() is self.polygonAction:
            self.data_manager.addPolygon(Body(), Fixture(), Polygon())
            self.updateTables()
    
    def prevObject(self):
        print "Previous"
        self.data_manager.prevObject()
    
    def nextObject(self):
        print "next";
        self.data_manager.nextObject()
    
    def deleteObject(self):
        print "Delete"        
    
    def onPolygons(self):
        print "Poligoans"
        self.data_manager.curr_object_type = DataObject.Types.POLYGON

        self.editBar.setVisible(True)        
        if self.manualAction.isChecked():
            self.manualBar.setVisible(True)
            self.regularBar.setVisible(False)
        else:
            self.manualBar.setVisible(False)
            self.regularBar.setVisible(True)
        
        self.polygon_manual_addpoint = True
        self.polygon_manual_delpoint = False
        self.circle_add = False
                 
    def onCircles(self):
        print "Circles"
        self.editBar.setVisible(False)
        self.data_manager.curr_object_type = DataObject.Types.CIRCLE

        self.manualBar.setVisible(False)
        self.regularBar.setVisible(False)
        
        self.polygon_manual_addpoint = False
        self.polygon_manual_delpoint = False
        self.circle_add = True
             
    def onJoints(self):
        print "Joints"
        self.data_manager.curr_object_type = DataObject.Types.JOINT

        self.editBar.setVisible(False)
        self.manualBar.setVisible(False)
        self.regularBar.setVisible(False)
        
    def onAddPoints(self):
        print "Add Points"
        
        self.polygon_manual_addpoint = True
        self.polygon_manual_delpoint = False
        
    def onDelPoints(self):
        print "Del Points"   
    
        self.polygon_manual_addpoint = False
        self.polygon_manual_delpoint = True
        
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
                             
#------------------------------------------------------------------------------ 
#------------------------------------------------------------------------------ 
                             
if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec_())


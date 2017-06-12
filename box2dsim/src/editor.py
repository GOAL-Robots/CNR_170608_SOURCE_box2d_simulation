#!/usr/bin/env python

import math
import copy
from PySide import QtCore, QtGui
import Box2D as b2
from Box2D.Box2D import b2_dynamicBody
import json
from pygments import highlight
import cPickle
from numpy import save

def distance(p1, p2):
    return math.sqrt( (p2.x()-p1.x())**2 + (p2.y()-p1.y())**2)

class World(object):
    
    def __init__(self):
        self.main = dict()
    
        self.main["gravity"] = (0,0) 
        self.main["allowSleep"] = True 
        self.main["autoClearForces"] = True 
        self.main["positionIterations"] = 2 
        self.main["velocityIterations"] = 6 
        self.main["stepsPerSecond"] = 60 
        self.main["warmStarting"] = True 
        self.main["continuousPhysics"] = True 
        self.main["subStepping"] = False 
    
    def serializeForJson(self):
        
        main_serialized = copy.deepcopy(self.main) 
        
        main_serialized["gravity"] = { 
             "x":self.main["gravity"][0],
             "y":self.main["gravity"][1] }
 
        return main_serialized
    
class Body(object):
    
    def __init__(self):
        
        self.main = dict()
        self.main["name"] = ""
        self.main["allowSleep"] = True
        self.main["angle"] = 0.0
        self.main["angularDamping"] = 0.0
        self.main["angularVelocity"] = 0.0
        self.main["awake"] = True
        self.main["bullet"] = False
        self.main["fixedRotation"] = False
        self.main["linearDamping"] = 0.0
        self.main["linearVelocity"] = (0.0, 0.0)
        self.main["position"] = (0.0, 0.0)
        self.main["type"] = 2
        self.main["awake"] = True
        self.main["fixture"] = [dict()]
        self.main["fixture"][0]["name"] = ""
        self.main["fixture"][0]["density"] = 1
        self.main["fixture"][0]["filter-categoryBits"] = 1
        self.main["fixture"][0]["filter-maskBits"] = 1
        self.main["fixture"][0]["filter-groupIndex"] = 1
        self.main["fixture"][0]["friction"] = 0.2
        self.main["fixture"][0]["restitution"] = 0.1
        self.main["fixture"][0]["sensor"] = True

    def serializeForJson(self):
        
        main_serialized = copy.deepcopy(self.main) 
        
        main_serialized["linearVelocity"] = { 
             "x":self.main["linearVelocity"][0],
             "y":self.main["linearVelocity"][1] }
        main_serialized["position"] = { 
             "x":self.main["position"][0],
             "y":self.main["position"][1] }
        
        return main_serialized
        
        
class Polygon(Body):

    def __init__(self):
        super(Polygon, self).__init__()
         
        self.main["fixture"][0]["polygon"] = dict()
        self.main["fixture"][0]["polygon"]["vertices"] = []
        
    def add_vertex(self, point):
        self.main["fixture"][0]["polygon"]["vertices"].append([point.x(), point.y()])
      
    def remove_vertex(self):
        self.main["fixture"][0]["polygon"]["vertices"] = self.main["fixture"][0]["polygon"]["vertices"][:-2]
              
    def to_b2Vec2(self):
        return [ b2.b2Vec2(x, y) for (x,y) in self.main["fixture"][0]["polygon"]["vertices"] ]
    
    def from_b2Vec2(self, b2_vrcs):
        self.main["fixture"][0]["polygon"]["vertices"] = [ [x, y] for (x,y) in b2_vrcs]
    
    def vertices(self):
        return self.main["fixture"][0]["polygon"]["vertices"]
    
    def serializeForJson(self):
        
        main_serialized = super(Polygon, self).serializeForJson()

        main_serialized["fixture"][0]["polygon"]["vertices"] = {"x":[], "y":[]}
        print self.main["fixture"][0]["polygon"]["vertices"]
        for x,y in self.main["fixture"][0]["polygon"]["vertices"]:
            main_serialized["fixture"][0]["polygon"]["vertices"]["x"].append(x)
            main_serialized["fixture"][0]["polygon"]["vertices"]["y"].append(y)
        
        return main_serialized
        
class Circle(Body):
    
    def __init__(self):
        super(Circle, self).__init__()
        self.main["fixture"][0]["circle"] = dict()
        self.main["fixture"][0]["circle"]["center"] = QtCore.QPoint(0,0)
        self.main["fixture"][0]["circle"]["radius"] = 0
        
    def center(self):
        return self.main["fixture"][0]["circle"]["center"]
      
    def setCenter(self, point):
        self.main["fixture"][0]["circle"]["center"] = point
      
    def radius(self):
        return self.main["fixture"][0]["circle"]["radius"] 
    
    def setRadius(self, rad):
        self.main["fixture"][0]["circle"]["radius"] = rad
     
    def serializeForJson(self):
        
        main_serialized = super(Circle, self).serializeForJson()   
        main_serialized["fixture"][0]["circle"]["radius"] = self.main["fixture"][0]["circle"]["radius"]
        main_serialized["fixture"][0]["circle"]["center"] = {"x":self.main["fixture"][0]["circle"]["center"].x(),  
                                     "y":self.main["fixture"][0]["circle"]["center"].y()}
        
        return main_serialized
    
    
class Joint(object):

    def __init__(self):
        self.main = dict()
        self.main["type"] = "revolute"
        self.main["name"] = ""
        self.main["anchorA"] = (0, 0)
        self.main["anchorB"] = (0, 0)
        self.main["bodyA"] = 0
        self.main["bodyB"] = 0
        self.main["collideConnected"] = True
        self.main["enableLimit"] = True
        self.main["enableMotor"] = True
        self.main["jointSpeed"] = 0
        self.main["lowerLimit"] = 0
        self.main["maxMotorTorque"] = 0
        self.main["motorSpeed"] = 0
        self.main["refAngle"] = 0
        self.main["upperLimit"] = 0
    
    def add_anchorA(self, point):
        self.main["anchorA"] = (point.x(), point.y())
    
    def add_anchorB(self, point):
        self.main["anchorB"] = (point.x(), point.y())
            
    def serializeForJson(self):
        
        main_serialized = copy.deepcopy(self.main) 
        main_serialized["anchorA"] = {"x":self.main["anchorA"].x(),  
                                     "y":self.main["anchorA"].y()}
        main_serialized["anchorB"] = {"x":self.main["anchorB"].x(),  
                                     "y":self.main["anchorB"].y()}
        
        return main_serialized     
  
def toPoint(list):
    return QtCore.QPoint(*list)  

class Types:

    POLYGON = 1
    CIRCLE = 2
    JOINT = 3


class DataTable(QtGui.QTableWidget):
    def __init__(self, obj):
        self.obj = obj
        if self.obj is  None:
           self.obj = Polygon() 
        self.rows = len(self.obj.main.keys())
        QtGui.QTableWidget.__init__(self, self.rows, 2)
        
        self.setmydata()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.itemChanged.connect(self.onItemChanged) 
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        
    def setmydata(self):
 
        m = 0
        for key,value in self.obj.main.iteritems():           
            name = QtGui.QTableWidgetItem(key)
            name.setFlags(QtCore.Qt.ItemIsEnabled)
            cont = QtGui.QTableWidgetItem(str(value))
            self.setItem(m, 0, name)
            self.setItem(m, 1, cont)
            m += 1   
            
    def onItemChanged(self, item):
        name = self.item(item.row(), 0).text()
        self.obj.main[name] = item.text()
        
class DataManager(object):

    def __init__(self):
        self.world = World()
        self.elements = dict()
        self.elements["polygons"] = []
        self.elements["circles"] = []
    
    def makeJson(self):
        
        world = self.world.serializeForJson()
        
        # clean
        polygons = copy.deepcopy(self.elements["polygons"])
        clean_list= []
        for i,p in  enumerate(polygons):
            if len(p.main["fixture"][0]["polygon"]["vertices"])<3:
                clean_list.append(i)
        for i in sorted(clean_list, reverse=True):
            del polygons[i]
                    
        bodies = [ obj.serializeForJson()  
                  for obj in (polygons + self.elements["circles"]) ]
        world["body"] = bodies
        
        json_file = open("body2d.json","w")
        json_file.write(json.JSONEncoder(True, True, True, False, False, True).encode(world))
    
    
        

class DrawingFrame(QtGui.QFrame):

    def __init__(self, tables, parent=None):
        
        super(DrawingFrame, self).__init__(parent)
        self.tables = tables
        self.parent = parent
    
        self.myPenWidth = 2
        self.myPenColor = QtCore.Qt.black
        self.myHighlightPenColor = QtCore.Qt.red

        self.new_shape = True
        self.shape_type = Types.POLYGON 
        self.current_shape = -1

        self.edit = False
       
        self.prevPoint = None
        self.currPoint = None

        width = 600
        height = 600 
        self.setFixedSize(width, height)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QtGui.QColor( 255, 255, 255 ) );
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
    def getCurrObj(self):
        
        o_type=None
        if self.shape_type == Types.POLYGON:
            o_type="polygons"
        elif self.shape_type == Types.CIRCLE:
            o_type="circles"
        elif self.shape_type == Types.JOINT:
            o_type="joints"
        
        try:
            return self.parent.data_manager.elements[o_type][self.current_shape]
        except:
            return None
        
    def updateTable(self):
        curr_obj = self.getCurrObj()
        
        if  curr_obj is not None:
            if self.tables.layout() is None:
                layout = QtGui.QHBoxLayout()
                self.tables.setLayout(layout)
                
            if self.tables.layout().count() > 0:
                self.tables.layout().removeItem(self.tables.layout().itemAt(0))        
            self.tables.layout().addWidget(DataTable(curr_obj))
            self.parent.resize(self.parent.layout.sizeHint())

    def setPen(self, painter, highlight=False):
        
        curr_pen = self.myPenColor
        curr_width = self.myPenWidth
        if highlight:
            curr_pen = self.myHighlightPenColor
            curr_width = self.myPenWidth*2

        painter.setPen(QtGui.QPen(curr_pen, 
                       curr_width,
                       QtCore.Qt.SolidLine,
                       QtCore.Qt.RoundCap, 
                       QtCore.Qt.RoundJoin))         
        

    def newShape(self):
        self.new_shape = True
        self.prevPoint = None
        self.nextPoint = None
        self.currPoint = None
        self.current_shape = -1
        self.updateTable()
        self.update()
      
    def deleteShape(self):
        container = None
        if self.shape_type == Types.POLYGON:
            container = self.parent.data_manager.elements["polygons"]
        elif self.shape_type == Types.CIRCLE:
            container = self.parent.data_manager.elements["circles"]
        elif self.shape_type == Types.JOINT:
            container = self.parent.data_manager.elements["joints"]
        
        del container[self.current_shape]
        
        self.prevPoint = None
        self.currPoint = None
        self.nextPoint = None
        self.current_shape = -1
        self.updateTable()
        self.update()
          
    def prevShape(self):
        
        self.prevPoint = None
        self.currPoint = None
        self.nextPoint = None
        self.current_shape -= 1 
        if self.current_shape < 0:
            self.current_shape = 0
        self.updateTable()
        self.update()
     
    def nextShape(self):
        
        self.prevPoint = None
        self.currPoint = None
        self.nextPoint = None

        len_shapes = 0 
        if self.shape_type == Types.POLYGON:
            len_shapes = len(self.parent.data_manager.elements["polygons"])
        elif self.shape_type == Types.CIRCLE:
            len_shapes = len(self.parent.data_manager.elements["circles"])
        elif self.shape_type == Types.JOINT:
            len_shapes = len(self.parent.data_manager.elements["joints"])
        self.current_shape += 1 
        if self.current_shape > len_shapes - 1:
            self.current_shape = 0
        self.updateTable()
        self.update()
    
    def switchToCircles(self):
        if self.shape_type != Types.CIRCLE:
            self.shape_type = Types.CIRCLE            
            self.new_shape = True
            self.prevPoint = None
            self.currPoint = None
            self.current_shape = -1
            self.updateTable()
            self.update()

    def switchToPolygons(self):
        if self.shape_type != Types.POLYGON:
            self.shape_type = Types.POLYGON
            self.new_shape = True
            self.prevPoint = None
            self.currPoint = None
            self.nextPoint = None
            self.current_shape = -1
            self.updateTable()
            self.update()


    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.new_shape == True:
                if self.shape_type == Types.POLYGON :
                    p = Polygon()
                    self.parent.data_manager.elements["polygons"].append(p)
                    self.parent.data_manager.elements["polygons"][self.current_shape].add_vertex(event.pos())
                    self.prevPoint = event.pos()
                if self.shape_type == Types.CIRCLE :
                    c = Circle()
                    self.parent.data_manager.elements["circles"].append(c)
                    self.parent.data_manager.elements["circles"][self.current_shape].setCenter(event.pos())
                
                self.new_shape = False

    def mouseMoveEvent(self, event):
        self.currPoint = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.shape_type == Types.POLYGON :
                curr_polygon = self.parent.data_manager.elements["polygons"][self.current_shape]
                self.currPoint = event.pos()
                curr_polygon.add_vertex(event.pos())
                
                # test 
                if len(curr_polygon.vertices())>=3 :
                    b2polygon = b2.b2PolygonShape(vertices=curr_polygon.to_b2Vec2())   
                      
                    if b2polygon is not None and len(b2polygon.vertices)>2:
                        curr_polygon.from_b2Vec2(b2polygon.vertices)    
           
                
                if  len(curr_polygon.vertices())==1:
                    print "zero"
                    self.deleteShape()
                    
                    
            if self.shape_type == Types.CIRCLE :
                if len(self.parent.data_manager.elements["circles"]) > 0:
                    c = self.parent.data_manager.elements["circles"][self.current_shape]
                    c.setRadius(distance(c.center(), event.pos()))
                    self.new_shape = True

            self.prevPoint = event.pos()
            self.update()
            self.updateTable()


    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        self.setPen(painter)
        
        polygons_length = len(self.parent.data_manager.elements["polygons"])
        for idx, polygon in enumerate(self.parent.data_manager.elements["polygons"]):
        
            if (self.shape_type == Types.POLYGON and (idx == self.current_shape 
                or (self.current_shape<0 and idx == (polygons_length -1) ) ) ):    
                self.setPen(painter, highlight=True)
            else:
                self.setPen(painter)
                
            vs = polygon.vertices()
            for idx in xrange(1,len(vs)):
                    prev_point = toPoint(vs[idx-1])
                    next_point = toPoint(vs[idx])
                    painter.drawLine(prev_point, next_point)
            
            painter.drawLine(toPoint(vs[-1]), toPoint(vs[0]))
        
        self.setPen(painter)

        circles_length = len(self.parent.data_manager.elements["circles"])
        for idx, circle in enumerate(self.parent.data_manager.elements["circles"]):
            
            if (self.shape_type == Types.CIRCLE and (idx == self.current_shape 
                or (self.current_shape<0 and idx == (circles_length -1) ) ) ):
                self.setPen(painter, highlight=True)
            else: 
                self.setPen(painter)

            painter.drawEllipse(circle.center(), circle.radius(), circle.radius())
 
 
        painter.setPen(QtGui.QPen(self.myPenColor, self.myPenWidth*0.1,
            QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
                   
        if self.prevPoint is not None and self.currPoint is not None:                
            if self.shape_type == Types.POLYGON :
    
                    painter.drawLine(self.prevPoint, self.currPoint)
    
            elif self.shape_type == Types.CIRCLE :
                  
                if len(self.parent.data_manager.elements["circles"]) > 0:
                    painter.drawLine(
                            self.parent.data_manager.elements["circles"][self.current_shape].center(), 
                            self.currPoint)

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        
        super(MainWindow, self).__init__()
        self.data_manager = DataManager()
              
        main = QtGui.QWidget(self)
        self.setCentralWidget(main)
        self.layout = QtGui.QHBoxLayout()
        main.setLayout(self.layout)
           
        self.worldTable = QtGui.QWidget(self)
        self.worldTable.setFixedSize(400,600)     
        self.tables = QtGui.QWidget(self)
        self.tables.setFixedSize(500,600)
        self.drawing_frame = DrawingFrame(self.tables,  self)
              
  
        exitAction = QtGui.QAction('Exit', self)
        exitAction.setShortcut('Q')
        exitAction.triggered.connect(self.close)
        
        polygonAction = QtGui.QAction('Polygon', self)
        polygonAction.setShortcut('P')
        polygonAction.setCheckable(True)
        polygonAction.setChecked(True)
        polygonAction.triggered.connect(self.drawing_frame.switchToPolygons)         
        circleAction = QtGui.QAction('Circle', self)
        circleAction.setShortcut('C')
        circleAction.setCheckable(True)
        circleAction.triggered.connect(self.drawing_frame.switchToCircles)         
        newAction = QtGui.QAction('New', self)
        newAction.setShortcut('N')
        newAction.triggered.connect(self.drawing_frame.newShape)  
          
        deleteAction = QtGui.QAction('Delete', self)
        deleteAction.setShortcut('Delete')
        deleteAction.triggered.connect(self.drawing_frame.deleteShape)  
        
        saveAction = QtGui.QAction('Save', self)
        saveAction.setShortcut('S')
        saveAction.triggered.connect(self.save)  
        
        loadAction = QtGui.QAction('Load', self)
        loadAction.setShortcut('L')
        loadAction.triggered.connect(self.load)   
                       
        prevAction = QtGui.QAction('Prev', self)
        prevAction.setShortcut('Left')
        prevAction.triggered.connect(self.drawing_frame.prevShape)   
             
        nextAction = QtGui.QAction('Next', self)
        nextAction.setShortcut('Right')
        nextAction.triggered.connect(self.drawing_frame.nextShape)   
              
        shapes = QtGui.QActionGroup(self)
        shapes.addAction(polygonAction)
        shapes.addAction(circleAction)
        shapes.setExclusive(True)

        toolBar = QtGui.QToolBar(self)
        toolBar.addAction(exitAction)
        toolBar.addAction(prevAction)
        toolBar.addAction(nextAction)
        toolBar.addAction(newAction)
        toolBar.addAction(deleteAction)
        toolBar.addAction(saveAction)
        toolBar.addAction(loadAction)
        toolBar.addAction(polygonAction)
        toolBar.addAction(circleAction)
        
        self.addToolBar(toolBar)
        
        layout = QtGui.QHBoxLayout()
        self.worldTable.setLayout(layout)
        self.worldTable.layout().addWidget(DataTable(self.data_manager.world))
        self.layout.addWidget(self.worldTable)
        self.layout.addWidget(self.drawing_frame)
        self.layout.addWidget(self.tables)
        self.setWindowTitle("")
        self.resize(self.layout.sizeHint())
    
    def save(self):
        sfile = open("data_dump", "w")
        cPickle.dump(self.data_manager, sfile)
        self.data_manager.makeJson()
    
    def load(self):
        lfile = open("data_dump", "r")
        self.data_manager = cPickle.load(lfile)

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


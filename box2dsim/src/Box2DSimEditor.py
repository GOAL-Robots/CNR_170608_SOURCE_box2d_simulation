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
from matplotlib.lines import VertexSelector

def distance(p1, p2):
    return math.sqrt( (p2.x()-p1.x())**2 + (p2.y()-p1.y())**2)

def clearLayout(layout):
     for i in reversed(range(layout.count())): 
        layout.itemAt(i).widget().setParent(None)

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
        
    def del_vertex(self, idx):
        del self.main["fixture"][0]["polygon"]["vertices"][idx]
        
    def setPosition(self, point):
        self.main["position"] = (point.x, point.y)

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
        self.main["fixture"][0]["circle"]["center"] = QtCore.QPointF(0,0)
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
    
    def addAnchorA(self, point):
        self.main["anchorA"] = (point.x(), point.y())
    
    def addAnchorB(self, point):
        self.main["anchorB"] = (point.x(), point.y())
     
    def setBodyA(self, name):
        self.main["bodyA"] = name
    
    def setBodyB(self, name):
        self.main["bodyB"] = name
                       
    def serializeForJson(self):
        
        main_serialized = copy.deepcopy(self.main) 
        if "anchorA" in main_serialized.keys():
            main_serialized["anchorA"] = {"x":self.main["anchorA"].x(),  
                                         "y":self.main["anchorA"].y()}
        if "anchorB" in main_serialized.keys():
            main_serialized["anchorB"] = {"x":self.main["anchorB"].x(),  
                                     "y":self.main["anchorB"].y()}
        
        return main_serialized     
  
def toPoint(lst):
    return QtCore.QPointF(*lst)  

class Types:

    POLYGON = 1
    CIRCLE = 2
    JOINT = 3

class GlueType:

    ADD = 1
    DELETE = 2

class PolyMode:
     
    MANUAL = 1
    REGULAR = 2   


class DataTable(QtGui.QTableWidget):
    def __init__(self, obj):

        self.obj = obj
        if self.obj is  None:
           self.obj = Polygon() 
        self.rows = len(self.obj.main.keys())
        QtGui.QTableWidget.__init__(self, self.rows, 2)
        
        self.itemChanged.connect(self.onItemChanged)         
        if self.setData() :
            #self.resizeColumnsToContents()
            self.resizeRowsToContents()
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setFixedSize(400, 600)
        
    def setData(self):
 
        contains_data = False
        for m, (key,value) in enumerate(self.obj.main.iteritems()):           
            name = QtGui.QTableWidgetItem(key)
            name.setFlags(QtCore.Qt.ItemIsEnabled)
            svalue = str(value)
            svalue = svalue.replace("{", "{\n")
            svalue = svalue.replace("},", "\n},")
            svalue = svalue.replace(",", ",\n")
            svalue = svalue.replace("[[", "[\n[")
            svalue = svalue.replace("}]", "\n}]")
            cont = QtGui.QTableWidgetItem(svalue)
            self.setItem(m, 0, name)
            self.setItem(m, 1, cont)
            
            if cont.data is not None:
                print key
                contains_data = True
    
        return contains_data

            
    def onItemChanged(self, item):
        name = self.item(item.row(), 0).text()
        self.obj.main[name] = eval(item.text())
        print self.obj.main[name]
        
class DataManager(object):

    def __init__(self):

        self.world = World()
        self.elements = dict()
        self.elements["polygons"] = []
        self.elements["circles"] = []
        self.elements["joints"] = []
   
    def getBodies(self):

        bodies = [ p.main["name"] for p in self.elements["polygons"] ]
        bodies = bodies + [ p.main["name"] for p in self.elements["circles"] ]
        
        bodies = filter(None, bodies)

        return bodies


    def makeJson(self, filename=None):
        
        world = self.world.serializeForJson()
        
        # clean
        polygons = copy.deepcopy(self.elements["polygons"])
        clean_list= []
        for i,p in  enumerate(polygons):
            if len(p.main["fixture"][0]["polygon"]["vertices"])<3:
                clean_list.append(i)
        for i in sorted(clean_list, reverse=True):
            del polygons[i]
                    
        bodies = [ obj.serializeForJson()  for obj in polygons]
        bodies += [ obj.serializeForJson()  for obj in self.elements["circles"]]
        world["body"] = bodies
        
        
        joints = [ obj.serializeForJson()  for obj in self.elements["joints"]]
        bodyIndices = { b["name"]:idx for idx,b in enumerate(bodies) }
        for joint in joints:
            joint["bodyA"] = bodyIndices[joint["bodyA"]]
            joint["bodyB"] = bodyIndices[joint["bodyB"]]
        world["joint"] = joints

        if filename is None:
            filename = "base.json"
        json_file = open(filename+".json","w")
        json_file.write(json.JSONEncoder(True, True, True, False, False, True).encode(world))
     
class DrawingFrame(QtGui.QFrame):

    def __init__(self, app, parent=None):
        
        super(DrawingFrame, self).__init__(parent)
        self.main_app = app
        self.parent = parent
        self.tables = self.parent.tables
        self.worldTable = self.parent.worldTable
    
        self.myPenWidth = 2
        self.myPenColor = QtCore.Qt.black
        self.myHighlightPenColor = QtCore.Qt.red

        self.new_shape = True
        self.current_shape = -1
        self.edit = False
        self.shape_type = Types.POLYGON        
        self.glue_type = GlueType.ADD
        self.poly_mode = PolyMode.MANUAL
        self.regular_radius = 1.0
        self.regular_vertices = 3
        self.regular_angle = 0
 
        self.prevPoint = None
        self.currPoint = None

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QtGui.QColor( 230, 230, 255 ) );
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.glue_type = GlueType.ADD
        
        self.WINDOW_BOTTOM = 0.0 
        self.WINDOW_LEFT = 0.0
        self.WINDOW_WIDTH = 20.0
        self.WINDOW_HEIGHT = 20.0

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
        
        if self.tables.layout() is not None:
            clearLayout(self.tables.layout())  
        layout = QtGui.QHBoxLayout()
        self.tables.setLayout(layout)    
        if curr_obj is not None:
            print self.current_shape, curr_obj
            data = DataTable(curr_obj)
            self.tables.layout().addWidget(data)
        self.parent.resize_all()
        
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
            if len(self.parent.data_manager.elements["polygons"])>0:
                container = self.parent.data_manager.elements["polygons"]
        elif self.shape_type == Types.CIRCLE:
            if len(self.parent.data_manager.elements["circles"])>0:
                container = self.parent.data_manager.elements["circles"]
        elif self.shape_type == Types.JOINT:
            if len(self.parent.data_manager.elements["joints"])>0:
                container = self.parent.data_manager.elements["joints"]
        
        if container is not None:
            del container[self.current_shape]
        else:    
            msgBox = QtGui.QMessageBox()
            msgBox.setText("There is no component left")
            msgBox.exec_()
            self.newShape()
        
        self.prevPoint = None
        self.currPoint = None
        self.nextPoint = None
        self.current_shape = len(container)-1
        self.updateTable()
        self.update()
          
    def prevShape(self):
        
        container = None
        
        if self.shape_type == Types.POLYGON:
            if len(self.parent.data_manager.elements["polygons"])>0:
                container = self.parent.data_manager.elements["polygons"]
        elif self.shape_type == Types.CIRCLE:
            if len(self.parent.data_manager.elements["circles"])>0:
                container = self.parent.data_manager.elements["circles"]
        elif self.shape_type == Types.JOINT:
            if len(self.parent.data_manager.elements["joints"])>0:
                container = self.parent.data_manager.elements["joints"]
                
        self.prevPoint = None
        self.currPoint = None
        self.nextPoint = None
        self.current_shape -= 1
        self.current_shape %= len(container) 
        

        self.updateTable()
        self.update()
     
    def nextShape(self):
        
        container = None
        
        if self.shape_type == Types.POLYGON:
            if len(self.parent.data_manager.elements["polygons"])>0:
                container = self.parent.data_manager.elements["polygons"]
        elif self.shape_type == Types.CIRCLE:
            if len(self.parent.data_manager.elements["circles"])>0:
                container = self.parent.data_manager.elements["circles"]
        elif self.shape_type == Types.JOINT:
            if len(self.parent.data_manager.elements["joints"])>0:
                container = self.parent.data_manager.elements["joints"]
        
        self.prevPoint = None
        self.currPoint = None
        self.nextPoint = None


        self.current_shape += 1 
        self.current_shape %= len(container)
        
        print self.current_shape
        
        self.updateTable()
        self.update()
    
    def onCircles(self):
        if self.shape_type != Types.CIRCLE:
            self.shape_type = Types.CIRCLE            
            self.new_shape = True
            self.prevPoint = None
            self.currPoint = None
            self.current_shape = -1
            self.parent.manualBar.setVisible(False)
            self.parent.regularBar.setVisible(False)
            self.parent.modifyBar.setVisible(False)
            self.updateTable()
            self.update()

    def onPolygons(self):
        if self.shape_type != Types.POLYGON:
            self.shape_type = Types.POLYGON
            self.new_shape = True
            self.prevPoint = None
            self.currPoint = None
            self.nextPoint = None
            self.current_shape = -1
            self.parent.manualBar.setVisible(True)
            self.parent.regularBar.setVisible(True)
            self.parent.modifyBar.setVisible(True)
            self.updateTable()
            self.update()

    def onJoints(self):
        if self.shape_type != Types.JOINT:
            self.shape_type = Types.JOINT
            self.new_shape = True
            self.prevPoint = None
            self.currPoint = None
            self.nextPoint = None
            self.current_shape = -1
            self.parent.manualBar.setVisible(False)
            self.parent.regularBar.setVisible(False)
            self.parent.modifyBar.setVisible(False)
            self.updateTable()
            self.update()
    
    def onGluePlus(self):
        self.glue_type = GlueType.ADD

    
    def onGlueMinus(self):
        self.glue_type = GlueType.DELETE
    
    def onPolyModeRegular(self):
        if self.poly_mode != PolyMode.REGULAR:
            self.poly_mode = PolyMode.REGULAR
            self.parent.vrtsBox.setEnabled(True)          
            self.parent.angleBox.setEnabled(True)          
            self.parent.radiusBox.setEnabled(True)          
            self.parent.radiusLabel.setEnabled(True)          
            self.parent.angleLabel.setEnabled(True)          
            self.parent.addPointsAction.setEnabled(False)           
            self.parent.delPointsAction.setEnabled(False)           
            self.newShape()

    def onPolyModeManual(self):
        if self.poly_mode != PolyMode.MANUAL:
            self.poly_mode = PolyMode.MANUAL
            self.parent.vrtsBox.setEnabled(False)    
            self.parent.angleBox.setEnabled(False)          
            self.parent.radiusBox.setEnabled(False) 
            self.parent.radiusLabel.setEnabled(False)          
            self.parent.angleLabel.setEnabled(False)          
            self.parent.addPointsAction.setEnabled(True)           
            self.parent.delPointsAction.setEnabled(True)         
            self.newShape()
    
    def onVrtxBoxChanged(self, text):
        self.regular_vertices = eval(self.parent.vrtsBox.currentText())
    
    def onRadiusBoxChanged(self):
        if len(self.parent.radiusBox.text()) > 0:
            self.regular_radius = eval(self.parent.radiusBox.text())
            
    def onAngleBoxChanged(self):
        if len(self.parent.angleBox.text()) > 0:
            self.regular_angle = eval(self.parent.angleBox.text())
       
    def mousePressEvent(self, event):
        scaled_pos = self.scalePoint(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            if self.new_shape == True:
                if self.shape_type == Types.POLYGON: 
                    if self.poly_mode == PolyMode.REGULAR:
                        p = Polygon()
                        angle = 2*b2.b2_pi/float(self.regular_vertices)
                        init_angle = self.regular_angle*(b2.b2_pi)/180.0
                        for i in range(self.regular_vertices):
                            vertex = QtCore.QPointF(
                                scaled_pos.x() + self.regular_radius*math.cos(init_angle + i*angle),
                                scaled_pos.y() + self.regular_radius*math.sin(init_angle + i*angle),
                                )
                            p.add_vertex(vertex)  
                        
                        self.parent.data_manager.elements["polygons"].append(p)
                        self.newShape()

                    elif ( self.glue_type == GlueType.ADD and 
                         self.poly_mode == PolyMode.MANUAL):
                        
                        # Manual add points  

                        p = Polygon()
                        p.add_vertex(scaled_pos)
                        self.parent.data_manager.elements["polygons"].append(p)
                        self.prevPoint = event.pos()
                        
                        self.new_shape = False

                if self.shape_type == Types.CIRCLE:

                    # add circles  

                    c = Circle()
                    c.setCenter(scaled_pos)
                    self.parent.data_manager.elements["circles"].append(c)

                if self.shape_type == Types.JOINT :
                    
                    # add joints  

                    j = Joint()
                    items = self.parent.data_manager.getBodies()

                    bodyA, okPressed = QtGui.QInputDialog.getItem(None, "BodyA", 'BodyA', items)
                    if okPressed: j.setBodyA(bodyA)

                    bodyB, okPressed = QtGui.QInputDialog.getItem(None, "BodyB", 'BodyB', items)
                    if okPressed: j.setBodyB(bodyB)
                    
                    exists_bodyA = False
                    exists_bodyB = False

                    for b in self.parent.data_manager.elements["polygons"] \
                            + self.parent.data_manager.elements["circles"]: 
                        if b.main["name"] == bodyA:
                            exists_bodyA = True
                            
                            j.main["anchorA"] = QtCore.QPointF(
                                    scaled_pos.x() - b.main["position"][0],   
                                    scaled_pos.y() - b.main["position"][1])                        
                        elif b.main["name"] == bodyB:
                            exists_bodyB = True
                            j.main["anchorB"] = QtCore.QPointF(
                                    scaled_pos.x() - b.main["position"][0],   
                                    scaled_pos.y() - b.main["position"][1]) 
                                                 
                    if not exists_bodyA:
                        del j.main["anchorA"]   
                        j.main["bodyA"] = None   
                    if not exists_bodyB:
                        del j.main["anchorB"] 
                        j.main["bodyB"] = None   
                                       
                    self.parent.data_manager.elements["joints"].append(j)
                    self.updateTable()
                    self.update()

              
            elif (self.shape_type == Types.POLYGON and 
                  self.glue_type==GlueType.DELETE and 
                  self.poly_mode == PolyMode.MANUAL):
                           
                # Manual delete points  

                polygons = self.parent.data_manager.elements["polygons"]
                if len(polygons)>0:
                    curr_polygon = polygons[self.current_shape]
                    for i, v in enumerate(curr_polygon.vertices()):
                        if distance(toPoint(v), scaled_pos) < 0.4:
                            curr_polygon.del_vertex(i)
                    if len(curr_polygon.vertices()) == 0:
                           self.newShape() 
                    
                    # test   
                    if len(curr_polygon.vertices())>=3 :
                        b2polygon = b2.b2PolygonShape(vertices=curr_polygon.to_b2Vec2())   
                          
                        if b2polygon is not None and len(b2polygon.vertices)>2:
                            curr_polygon.from_b2Vec2(b2polygon.vertices) 
                            curr_polygon.setPosition(b2polygon.centroid)


    def mouseMoveEvent(self, event):
        self.currPoint = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        scaled_pos = self.scalePoint(event.pos())
        if event.button() == QtCore.Qt.LeftButton:
            if (self.shape_type == Types.POLYGON and 
                self.poly_mode == PolyMode.MANUAL and
                self.glue_type==GlueType.ADD):
                   
                polygons =  self.parent.data_manager.elements["polygons"]            
                
                if len(polygons) == 0:
                    self.newShape()
                else:
                    
                    curr_polygon = polygons[self.current_shape]
                    if len(curr_polygon.vertices()) >= 2:
                        if curr_polygon.vertices()[-1] == curr_polygon.vertices()[-2]:
                            curr_polygon.del_vertex(-1)
                                
                    self.currPoint = event.pos()
                    curr_polygon.add_vertex(scaled_pos)
                    
                    # test 
                    if len(curr_polygon.vertices())>=3 :
                        b2polygon = b2.b2PolygonShape(vertices=curr_polygon.to_b2Vec2())   
                          
                        if b2polygon is not None and len(b2polygon.vertices)>2:
                            curr_polygon.from_b2Vec2(b2polygon.vertices) 
                            curr_polygon.setPosition(b2polygon.centroid)             

            if self.shape_type == Types.CIRCLE :
                if len(self.parent.data_manager.elements["circles"]) > 0:
                    c = self.parent.data_manager.elements["circles"][self.current_shape]
                    c.setRadius(distance(c.center(), scaled_pos))
                    self.new_shape = True

            self.prevPoint = event.pos()
            self.updateTable()
            self.update()

    def scalePoint(self, point):

        return QtCore.QPointF( 
                (point.x()/600.0)*float(self.WINDOW_WIDTH),
                self.WINDOW_HEIGHT - (point.y()/600.0)*float(self.WINDOW_HEIGHT) )


    def rescalePoint(self, point):

        return QtCore.QPointF( 
                point.x()*600.0/float(self.WINDOW_WIDTH),
                (self.WINDOW_HEIGHT -  point.y())*600.0/float(self.WINDOW_HEIGHT) )
    
    def rescale(self, x):

        return x*600.0/(float(self.WINDOW_WIDTH)*
                (float(self.WINDOW_WIDTH)/float(self.WINDOW_HEIGHT)))
       
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
                    painter.drawLine(
                            self.rescalePoint(prev_point),
                            self.rescalePoint(next_point))
            
            painter.drawLine(
                    self.rescalePoint(toPoint(vs[-1])), 
                    self.rescalePoint(toPoint(vs[0])))
        
        self.setPen(painter)

        circles_length = len(self.parent.data_manager.elements["circles"])
        for idx, circle in enumerate(self.parent.data_manager.elements["circles"]):
            
            if (self.shape_type == Types.CIRCLE and (idx == self.current_shape 
                or (self.current_shape<0 and idx == (circles_length -1) ) ) ):
                self.setPen(painter, highlight=True)
            else: 
                self.setPen(painter)

            painter.drawEllipse(
                    self.rescalePoint(circle.center()), 
                    self.rescale(circle.radius()), 
                    self.rescale(circle.radius()))
        
        joints_length = len(self.parent.data_manager.elements["joints"])
        for idx, joint in enumerate(self.parent.data_manager.elements["joints"]):
            
            if (self.shape_type == Types.JOINT and (idx == self.current_shape 
                or (self.current_shape<0 and idx == (joints_length -1) ) ) ):
                self.setPen(painter, highlight=True)
            else: 
                self.setPen(painter)

                    
            for b in self.parent.data_manager.elements["polygons"] \
                    + self.parent.data_manager.elements["circles"]: 
                if b.main["name"] == joint.main["bodyA"]:
                    bodyApos = b.main["position"]
                elif b.main["name"] ==  joint.main["bodyB"]:
                    bodyBpos = b.main["position"]

            jcenter = toPoint(
                    [ bodyApos[0] + joint.main["anchorA"].x(),
                    bodyApos[1] + joint.main["anchorA"].y() ] )
            
            jA = toPoint(bodyApos)
            jB = toPoint(bodyBpos)
            
            painter.drawLine(
                    self.rescalePoint(jcenter), 
                    self.rescalePoint(jA))
            painter.drawLine(
                    self.rescalePoint(jcenter), 
                    self.rescalePoint(jB))
            painter.drawEllipse(
                    self.rescalePoint(jcenter), 
                    self.myPenWidth*4,
                    self.myPenWidth*4)
 
        painter.setPen(QtGui.QPen(self.myPenColor, self.myPenWidth*0.1,
            QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
                   
        if self.prevPoint is not None and self.currPoint is not None:                
            if self.shape_type == Types.POLYGON and self.parent.addPointsAction.isChecked():
    
                    painter.drawLine(
                            self.prevPoint, 
                            self.currPoint)
    
            elif self.shape_type == Types.CIRCLE :
                  
                if len(self.parent.data_manager.elements["circles"]) > 0:
                    center = self.parent.data_manager.elements["circles"][self.current_shape].center() 
                    painter.drawLine(
                            self.rescalePoint(center), 
                            self.currPoint )

class MainWindow(QtGui.QMainWindow):
    def __init__(self, app):
        
        super(MainWindow, self).__init__()
        self.data_manager = DataManager()
              
        main = QtGui.QWidget(self)
        self.setCentralWidget(main)
        self.layout = QtGui.QHBoxLayout()
        main.setLayout(self.layout)
           
        self.worldTable = QtGui.QWidget(self)
        self.tables = QtGui.QWidget(self)
        self.drawing_frame = DrawingFrame(app,  self)
        self.resize_all()
        
        exitAction = QtGui.QAction('Exit', self)
        exitAction.setShortcut('Q')
        exitAction.triggered.connect(self.close)
        
        polygonAction = QtGui.QAction('Polygon', self)
        polygonAction.setShortcut('P')
        polygonAction.setCheckable(True)
        polygonAction.setChecked(True)
        polygonAction.triggered.connect(self.drawing_frame.onPolygons)         
        circleAction = QtGui.QAction('Circle', self)
        circleAction.setShortcut('C')
        circleAction.setCheckable(True)
        circleAction.triggered.connect(self.drawing_frame.onCircles)         
        jointAction = QtGui.QAction('Joint', self)
        jointAction.setShortcut('C')
        jointAction.setCheckable(True)
        jointAction.triggered.connect(self.drawing_frame.onJoints)         
        
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
        
        self.addPointsAction = QtGui.QAction('glue+', self)
        self.addPointsAction.setShortcut('+')
        self.addPointsAction.setCheckable(True)
        self.addPointsAction.setChecked(True)
        self.addPointsAction.triggered.connect(self.drawing_frame.onGluePlus)         

        self.delPointsAction = QtGui.QAction('glue-', self)
        self.delPointsAction.setShortcut('-')
        self.delPointsAction.setCheckable(True)
        self.delPointsAction.triggered.connect(self.drawing_frame.onGlueMinus)         
   
        self.manualPolyModeAction = QtGui.QAction('Manual', self)
        self.manualPolyModeAction.setShortcut('M')
        self.manualPolyModeAction.setCheckable(True)
        self.manualPolyModeAction.setChecked(True)
        self.manualPolyModeAction.triggered.connect(self.drawing_frame.onPolyModeManual)         

        self.regularPolyModeAction = QtGui.QAction('Regular', self)
        self.regularPolyModeAction.setShortcut('R')
        self.regularPolyModeAction.setCheckable(True)
        self.regularPolyModeAction.triggered.connect(self.drawing_frame.onPolyModeRegular)         
        
        self.vrtsBox = QtGui.QComboBox(self)
        self.vrtsBox.addItems(["%d" % x for x in range(3,17) ])
        self.vrtsBox.currentIndexChanged.connect(self.drawing_frame.onVrtxBoxChanged)
        self.vrtsBox.setEnabled(False)    
        self.angleBox = QtGui.QLineEdit(self)
        validator = QtGui.QIntValidator()
        self.angleBox.setValidator(validator)
        self.angleBox.setMaxLength(4)   
        self.angleBox.setEnabled(False)    
        self.angleBox.textChanged.connect(self.drawing_frame.onAngleBoxChanged)
        self.angleLabel = QtGui.QLabel("angle")
        self.angleLabel.setEnabled(False)    
        self.radiusBox = QtGui.QLineEdit(self)
        validator = QtGui.QIntValidator()
        self.radiusBox.setValidator(validator)
        self.radiusBox.setMaxLength(4)   
        self.radiusBox.setEnabled(False)    
        self.radiusBox.textChanged.connect(self.drawing_frame.onRadiusBoxChanged)
        self.radiusLabel = QtGui.QLabel("radius")
        self.radiusLabel.setEnabled(False)    

        shapes = QtGui.QActionGroup(self)
        shapes.addAction(polygonAction)
        shapes.addAction(circleAction)
        shapes.addAction(jointAction)
        shapes.setExclusive(True)
        
        self.actionsGroup = QtGui.QActionGroup(self)
        self.actionsGroup.addAction(self.addPointsAction)
        self.actionsGroup.addAction(self.delPointsAction)   
        
        self.polyModeGroup = QtGui.QActionGroup(self)
        self.polyModeGroup.addAction(self.manualPolyModeAction)
        self.polyModeGroup.addAction(self.regularPolyModeAction)


        toolBar = QtGui.QToolBar(self)
        toolBar.addAction(exitAction)
        toolBar.addSeparator()
        toolBar.addAction(prevAction)
        toolBar.addAction(nextAction)
        toolBar.addSeparator()
        toolBar.addAction(newAction)
        toolBar.addAction(deleteAction)
        toolBar.addAction(saveAction)
        toolBar.addAction(loadAction)
        toolBar.addSeparator()
        toolBar.addAction(polygonAction)
        toolBar.addAction(circleAction)
        toolBar.addAction(jointAction) 
        toolBar.addSeparator()
        self.addToolBar(toolBar)
        self.addToolBarBreak()
        
        self.manualBar = QtGui.QToolBar(self)
        self.manualBar.addAction(self.manualPolyModeAction)
        self.manualBar.addAction(self.addPointsAction)
        self.manualBar.addAction(self.delPointsAction)
        self.addToolBar(self.manualBar)
          
        self.regularBar = QtGui.QToolBar(self)
        self.regularBar.addAction(self.regularPolyModeAction)
        self.regularBar.addWidget(self.vrtsBox)
        self.regularBar.addWidget(self.angleLabel)
        self.regularBar.addWidget(self.angleBox)
        self.regularBar.addWidget(self.radiusLabel)
        self.regularBar.addWidget(self.radiusBox)
        self.addToolBar(self.regularBar)
               
        self.modifyBar = QtGui.QToolBar(self)
        self.addToolBar(self.modifyBar)

        layout = QtGui.QHBoxLayout()
        self.worldTable.setLayout(layout)
        self.worldTable.layout().addWidget(DataTable(self.data_manager.world))
        self.layout.addWidget(self.worldTable)
        self.layout.addWidget(self.drawing_frame)
        self.layout.addWidget(self.tables)
        self.layout.addStretch(1)
        self.setWindowTitle("")
        #self.resize(self.layout.sizeHint())
    
    def resize_all(self):
        self.worldTable.resize(300,600)
        self.tables.resize(300,600)
        self.drawing_frame.setFixedSize(600,600)
        self.resize(1200, 600) 
    
    def save(self):
        filename = "copy"
        sfile = open(filename+".dump", "w")
        cPickle.dump(self.data_manager, sfile)
        self.data_manager.makeJson(filename)
    
    def load(self):
        filename = "copy"
        lfile = open(filename+".dump", "r")
        self.data_manager = cPickle.load(lfile)
        self.drawing_frame.updateTable()
        self.drawing_frame.update()

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec_())

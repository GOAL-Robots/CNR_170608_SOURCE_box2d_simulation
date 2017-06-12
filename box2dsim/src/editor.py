#!/usr/bin/env python

import math
from PySide import QtCore, QtGui


def distance(p1, p2):
    return math.sqrt( (p2.x()-p1.x())**2 + (p2.y()-p1.y())**2)

class Polygon(object):

    def __init__(self):
        self.vertices = []

    def add_vertex(self, point):
        self.vertices.append(point)

class Circle(object):
    
    def __init__(self):
        self.center = QtCore.QPoint(0,0)
        self.radius = 0

class Shapes:

    POLYGON = 1
    CIRCLE = 2


class DataManager(object):

    def __init__(self):
        self.polygons = []
        self.circles = []


class DrawingFrame(QtGui.QWidget):

    def __init__(self, data_manager, parent=None):
        
        super(DrawingFrame, self).__init__(parent)
        self.data_manager = data_manager

    
        self.myPenWidth = 2
        self.myPenColor = QtCore.Qt.black

        self.new_shape = True
        self.shape_type = Shapes.POLYGON 
        self.current_shape = -1

        self.edit = False
       
        self.prevPoint = None
        self.currPoint = None

        w = 500
        h = 500    
        self.resize(w, h)
    
    def setShapeNum(idx):
        self.current_shape = idx
        
    def newShape(self):
        self.new_shape = True
        self.prevPoint = None
        self.currPoint = None
        self.current_shape = -1

    def switchToCircles(self):
        if self.shape_type != Shapes.CIRCLE:
            self.shape_type = Shapes.CIRCLE
            self.new_shape = True
            self.prevPoint = None
            self.currPoint = None
            self.current_shape = -1
    
    def switchToPolygons(self):
        if self.shape_type != Shapes.POLYGON:
            self.shape_type = Shapes.POLYGON
            self.new_shape = True
            self.prevPoint = None
            self.currPoint = None
            self.current_shape = -1


    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.new_shape == True:
                if self.shape_type == Shapes.POLYGON :
                    p = Polygon()
                    self.data_manager.polygons.append(p)
                    self.data_manager.polygons[self.current_shape].add_vertex(event.pos())
                    self.prevPoint = event.pos()
                if self.shape_type == Shapes.CIRCLE :
                    c = Circle()
                    self.data_manager.circles.append(c)
                    self.data_manager.circles[self.current_shape].center = event.pos()
                
                self.new_shape = False

    def mouseMoveEvent(self, event):
        self.currPoint = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.shape_type == Shapes.POLYGON :
                self.data_manager.polygons[self.current_shape].add_vertex(event.pos())
            if self.shape_type == Shapes.CIRCLE :
                if len(self.data_manager.circles) > 0:
                    c = self.data_manager.circles[self.current_shape]
                    c.radius = distance(c.center, event.pos())
                    self.new_shape = True

            self.prevPoint = event.pos()
            self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.setPen(QtGui.QPen(self.myPenColor, self.myPenWidth,
            QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
            
        for polygon in self.data_manager.polygons:
            vs = polygon.vertices
            for idx in xrange(1,len(vs)):
                    prev_point = vs[idx-1]
                    next_point = vs[idx]
                    painter.drawLine(prev_point, next_point)
            painter.drawLine(vs[-1], vs[0])
        
        for circle in self.data_manager.circles:
            painter.drawEllipse(circle.center, circle.radius, circle.radius)
 
 
        painter.setPen(QtGui.QPen(self.myPenColor, self.myPenWidth*0.1,
            QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
                       
        if self.shape_type == Shapes.POLYGON :

            if self.prevPoint is not None and self.currPoint is not None:
                painter.drawLine(self.prevPoint, self.currPoint)

        elif self.shape_type == Shapes.CIRCLE :
              
            if len(self.data_manager.circles) > 0:
                painter.drawLine(
                        self.data_manager.circles[self.current_shape].center, 
                        self.currPoint)

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.data_manager = DataManager()
        main = QtGui.QWidget(self)
        self.setCentralWidget(main)
        layout = QtGui.QVBoxLayout()
        main.setLayout(layout)
        self.drawing_frame = DrawingFrame(self.data_manager, self)
        
        exitAction = QtGui.QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        
        polygonAction = QtGui.QAction('Polygon', self)
        polygonAction.setShortcut('Ctrl+P')
        polygonAction.setCheckable(True)
        polygonAction.setChecked(True)
        polygonAction.triggered.connect(self.drawing_frame.switchToPolygons)         
        circleAction = QtGui.QAction('Circle', self)
        circleAction.setShortcut('Ctrl+C')
        circleAction.setCheckable(True)
        circleAction.triggered.connect(self.drawing_frame.switchToCircles)         
        newAction = QtGui.QAction('New', self)
        newAction.setShortcut('Ctrl+N')
        newAction.triggered.connect(self.drawing_frame.newShape)         
        shapes = QtGui.QActionGroup(self)
        shapes.addAction(polygonAction)
        shapes.addAction(circleAction)
        shapes.setExclusive(True)

        toolBar = QtGui.QToolBar(self)
        toolBar.addAction(exitAction)
        toolBar.addAction(newAction)
        toolBar.addAction(polygonAction)
        toolBar.addAction(circleAction)
        
        self.addToolBar(toolBar)
        
        layout.addWidget(self.drawing_frame)
        self.setWindowTitle("")
        self.resize(500, 500)


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


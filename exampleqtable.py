import sys
from PySide.QtCore import *
from PySide.QtGui import *

data = {'row1': 1, 'row2': 2}
 
class MyTable(QTableWidget):
    def __init__(self, data, *args):
        QTableWidget.__init__(self, *args)
        self.data = data
        self.setmydata()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.itemChanged.connect(self.onItemChanged) 

    def setmydata(self):
 
        m = 0
        for key,value in self.data.iteritems():           
            cont = QTableWidgetItem("%d" % value)
            self.setItem(m, 0, cont)
            m += 1

    def onItemChanged(self, item):
        print item.data(0)
 
def main(args):
    app = QApplication(args)
    table = MyTable(data, 5, 1)
    table.show()
    sys.exit(app.exec_())
 
if __name__=="__main__":
    main(sys.argv)

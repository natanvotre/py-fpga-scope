import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class DockDemo(QMainWindow):
    def __init__(self,parent=None):
        super(DockDemo, self).__init__(parent)
        layout=QHBoxLayout()
        bar=self.menuBar()
        file=bar.addMenu('File')
        file.addAction('New')
        file.addAction('Save')
        file.addAction('quit')

        self.items=QDockWidget('Dockable',self)
        self.items2=QDockWidget('Dockable',self)

        self.listWidget=QListWidget()
        self.listWidget.addItem('Item1')
        self.listWidget.addItem('Item2')
        self.listWidget.addItem('Item3')
        self.listWidget.addItem('Item4')

        self.listWidget2=QListWidget()
        self.listWidget2.addItem('Item1')
        self.listWidget2.addItem('Item2')
        self.listWidget2.addItem('Item4')

        self.items.setWidget(self.listWidget)
        self.items2.setWidget(self.listWidget2)
        self.items.setFloating(False)
        self.items2.setFloating(False)
        self.setCentralWidget(QTextEdit())
        self.addDockWidget(Qt.RightDockWidgetArea,self.items)
        self.addDockWidget(Qt.RightDockWidgetArea, self.items2)

        self.setLayout(layout)
        self.setWindowTitle('Dock')

if __name__ == '__main__':
    app=QApplication(sys.argv)
    demo=DockDemo()
    demo.show()
    sys.exit(app.exec_())

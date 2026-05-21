## This is the class file where all the useful custom widgets are defined. You can import this file in your main GUI file and use the widgets defined here.
## These widgets will be entirely based on PyQt6, so you can use all the features of PyQt6 to create your custom widgets.


from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor



class LedWidget(QWidget):
    '''
    A simple single circular LED widget that can be turned on (bright green) or off (dim green).


    '''
    def __init__(self, parent=None):
        super().__init__(parent)

        self.state = False
        self.setFixedSize(30, 30)

    def setState(self, on: bool):
        self.state = on
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.state:
            color = QColor(0, 255, 0)     # bright green
        else:
            color = QColor(40, 60, 40)    # dim green

        painter.setBrush(color)
        painter.drawEllipse(2, 2, 26, 26)
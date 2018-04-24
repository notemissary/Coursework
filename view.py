# -*- coding: utf-8 -*-
"""
Created on Mon Dec 25 23:21:47 2017

@author: noname
"""
import sys
from PyQt5 import QtWidgets, QtGui, QtCore, uic
import model as m
import data_rc

k = 0
filename = 'V_log.txt'
sys.stderr = open(filename, 'w')


class QDot(QtWidgets.QLabel):
    def __init__(self, position, parent=None):
        super().__init__(parent)
        self.__parent = parent
        self.__move = False
        self.setText('')
        self.setMouseTracking(True)
        self.color = QtGui.QColor(255, 0, 0)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setFixedWidth(9)
        self.setFixedHeight(9)
        self.move(position.x()-5, position.y()-5)
        self.setStyleSheet('''background-color: {};
                              font: 7pt "Verdana";
                              color: rgb(255, 255, 255);'''.format('rgb'+str(self.color.getRgb())))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.__move = True
        elif event.button() == QtCore.Qt.RightButton:
            menu = QtWidgets.QMenu(self.__parent)
            actionColor = QtWidgets.QAction('Color', self)
            actionColor.triggered.connect(self.set_color)
            menu.addAction(actionColor)
            menu.addSeparator()
            actionDelete = QtWidgets.QAction('Delete', self)
            actionDelete.triggered.connect(self.self_delete)
            menu.addAction(actionDelete)
            globalCursorPos = QtGui.QCursor().pos()
            mouseScreen = app.desktop().screenNumber(globalCursorPos)
            mouseScreenGeometry = app.desktop().screen(mouseScreen).geometry()
            localCursorPos = globalCursorPos - mouseScreenGeometry.topLeft()
            menu.move(localCursorPos)
            menu.show()

    def self_delete(self):
        self.__parent.del_dot(self)

    def set_color(self):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.color = color
            self.setStyleSheet('''background-color: {};
                                  font: 7pt "Verdana";
                                  color: rgb(255, 255, 255);'''.format('rgb'+str(self.color.getRgb())))

    def mouseMoveEvent(self, event):
        self.__parent.coords_label.setText("({}, {})".format(self.pos().x(), self.pos().y()))
        if self.__move:
            self.move(self.mapToParent(event.pos()))
            self.raise_()

    def mouseReleaseEvent(self, event):
        self.__move = False
        if not (0 <= self.pos().x() <= self.__parent.width()
                and 0 <= self.pos().y() <= self.__parent.height()-20):
            self.__parent.del_dot(self)


class GUI(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dotSize = None
        self.posit = None
        uic.loadUi('gui.ui', self)
        self.vertexes = dict()
        self.ver_label = QtWidgets.QLabel("Vertexes: {}".format(len(self.vertexes.keys())), self)
        self.status_label = QtWidgets.QLabel("Not ready", self)
        self.coords_label = QtWidgets.QLabel('', self)
        self.statusbar.addWidget(self.status_label, 2)
        self.statusbar.addWidget(self.coords_label, 1)
        self.statusbar.addPermanentWidget(self.ver_label, 1)
        self.pauseFlag = False
        self.runningFlag = False
        self.pen = True
        self.setFixedSize(self.size())
        self.point = QtCore.QObject()
        self.color = None
        self.loop = QtCore.QEventLoop()
        self.oImage = QtGui.QImage(":/data/board.png")
        self.oImage.scaled(self.width(), self.height())
        self.plt = QtGui.QPalette()
        self.plt.setBrush(self.plt.Window, QtGui.QBrush(self.oImage))
        self.setPalette(self.plt)
        self.A = QtWidgets.QLabel()
        self.figure = None
        self.show()
        self.startButton.clicked.connect(self.start)
        self.speed.valueChanged.connect(self.speed_change)
        self.pauseButton.clicked.connect(self.pause)
        self.stopButton.clicked.connect(self.stop)
        self.groupBox.toggled.connect(self.hide_group_box)
        self.radio = list()

    def del_dot(self, dot):
        global k
        for i in self.vertexes.keys():
            if self.vertexes[i] == dot:
                dot.deleteLater()
                del self.vertexes[i]
                break
        temp = dict()
        for i, j in enumerate(self.vertexes.keys()):
            temp[i] = self.vertexes[j]
            temp[i].setText('{}'.format(i))
        self.vertexes = temp
        k -= 1
        self.coords_label.setText('')

    def hide_group_box(self, b):
        if b:
            self.groupBox.setFixedHeight(211)
        else:
            self.groupBox.setFixedHeight(18)

    def no_event(self, *args):
        pass

    def stop(self):
        global k
        k = 0
        for i in self.vertexes:
            self.vertexes[i].deleteLater()
        self.vertexes.clear()
        self.dotSize = None
        self.posit = None
        self.pauseFlag = True
        self.runningFlag = False
        self.pen = True
        self.point.deleteLater()
        self.point = QtCore.QObject()
        self.color = None
        self.loop = QtCore.QEventLoop()
        self.oImage = QtGui.QImage(":/data/board.png")
        self.plt = QtGui.QPalette()
        self.plt.setBrush(self.plt.Window, QtGui.QBrush(self.oImage))
        self.setPalette(self.plt)
        self.spinBox.setValue(0)

    def pause(self):
        self.pauseFlag = True

    def speed_change(self):
        self.speed_label.setText(str(self.speed.value())+'%')

    def start(self):
        if self.lineEdit.text():
            allowed_vertexes = list(map(int, self.lineEdit.text().split(',')))
        else:
            allowed_vertexes = [0]
        if isinstance(self.point, QDot):
            self.dotSize = 1
            self.pen = True
            self.runningFlag = True
            self.loop = QtCore.QEventLoop()
            i = -1
            end_val = 0
            if self.spinBox.value() and not self.pauseFlag:
                end_val = self.spinBox.value()
                i = 0
            self.posit = self.point.pos()
            self.pauseFlag = False
            while i < end_val:
                QtCore.QTimer.singleShot((1000 // self.speed.value())-10, self.loop.quit)
                self.loop.exec_()
                if self.pauseFlag:
                    break
                x, y, ver = m.Fractal(self.posit.x(), self.posit.y(), self.vertexes, allowed_vertexes).coordinates()
                self.posit = QtCore.QPoint(x, y)
                self.color = ver.color
                self.update()
                if end_val:
                    self.spinBox.setValue(self.spinBox.value()-1)
                    i += 1
                else:
                    self.spinBox.setValue(self.spinBox.value()+1)

    def mousePressEvent(self, e):
        if self.runningFlag or \
                any(map(lambda x: isinstance(self.childAt(e.pos()), x), [QtWidgets.QGroupBox, QtWidgets.QLabel,
                                                                         QtWidgets.QStatusBar])):
            return
        global k
        if e.button() == QtCore.Qt.LeftButton:
            self.posit = e.pos()
            self.vertexes[k] = QDot(e.pos(), parent=self)
            self.vertexes[k].setText('{}'.format(k))
            self.vertexes[k].show()
            k += 1

        elif e.button() == QtCore.Qt.RightButton:
            self.point.deleteLater()
            self.point = QDot(e.pos(), self)
            self.point.show()
        self.update()

    def closeEvent(self, *args, **kwargs):
        self.stop()
        self.close()

    def paintEvent(self, ev):
        qp = QtGui.QPainter(self.oImage)
        qp.setRenderHint(QtGui.QPainter.Antialiasing)
        if self.color:
            self.color.setAlpha(85)
            pen = QtGui.QPen(self.color)
            qp.setPen(pen)
            qp.drawPoint(self.posit)
            self.plt.setBrush(self.plt.Window, QtGui.QBrush(self.oImage))
            self.setPalette(self.plt)
        self.ver_label.setText("Vertexes: {}".format(len(self.vertexes.keys())))
        self.ver_label.setStyleSheet("color: red")
        self.status_label.setText("Not ready")
        self.status_label.setStyleSheet("color: red;")
        if len(self.vertexes.keys()) > 2:
            self.ver_label.setStyleSheet("color: green;")
            if isinstance(self.point, QDot) and self.lineEdit.text():
                self.status_label.setText('Ready')
                self.status_label.setStyleSheet("color: green;")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = GUI()
    sys.exit(app.exec_())

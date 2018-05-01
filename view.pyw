# -*- coding: utf-8 -*-
"""
Created on Mon Dec 25 23:21:47 2017

This file contains realization of GUI for the Chaos Game method.

@author: Dyma Volodymyr Sergiyovoich
"""
import sys
import ctypes
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from ctypes import wintypes
import model as m
import data_rc

# If you don't want using .pyw files, just rename it to the .py file and uncomment the following line
# ctypes.WinDLL('kernel32', use_last_error=True).SetConsoleTitleW("Developer Console")
lpBuffer = wintypes.LPWSTR()
AppUserModelID = ctypes.windll.shell32.GetCurrentProcessExplicitAppUserModelID
AppUserModelID(ctypes.cast(ctypes.byref(lpBuffer), wintypes.LPWSTR))
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(AppUserModelID)

k = 0


class QDot(QtWidgets.QLabel):
    """QDot class

    This class is used for placing draggable dots which are used either as vertices or an initial point

    :param position: position where to place the dot
    :param parent: parent of the given QObject
    """
    def __init__(self, position, parent=None):
        super().__init__(parent)
        assert isinstance(position, QtCore.QPoint), 'position must be QtCore.QPoint object'
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
        if self.__parent.runningFlag:
            return
        if event.button() == QtCore.Qt.LeftButton:
            self.__move = True
        elif event.button() == QtCore.Qt.RightButton:
            menu = QtWidgets.QMenu(self.__parent)
            action_color = QtWidgets.QAction('Color', self)
            menu.addAction(action_color)
            menu.addSeparator()
            action_delete = QtWidgets.QAction('Delete', self)
            menu.addAction(action_delete)
            global_cursor_pos = QtGui.QCursor().pos()
            mouse_screen = app.desktop().screenNumber(global_cursor_pos)
            mouse_screen_geometry = app.desktop().screen(mouse_screen).geometry()
            local_cursor_pos = global_cursor_pos - mouse_screen_geometry.topLeft()
            menu.move(local_cursor_pos)
            menu.show()
            action_color.triggered.connect(self.set_color)
            action_delete.triggered.connect(self.self_delete)

    def self_delete(self):
        """Delete dot

        Calls parent's del_dot method
        """
        self.__parent.del_dot(self)

    def set_color(self):
        """Dot color

        Set currently chosen dot color
        """
        color = QtWidgets.QColorDialog().getColor(initial=QtCore.Qt.white, parent=self.__parent)
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
        if self.__parent.runningFlag:
            return
        self.__move = False
        if not (0 <= self.pos().x() <= self.__parent.width()
                and 0 <= self.pos().y() <= self.__parent.height()-20):
            self.__parent.del_dot(self)


class GUI(QtWidgets.QMainWindow):
    """GUI class

    This is the main window of the application. It controls all the interactions with the user and represents
    information.

    :param parent: parent of the given QObject
    """
    def __init__(self, parent=None):
        super().__init__(parent, flags=QtCore.Qt.Window)
        uic.loadUi('gui.ui', self)
        self.textEdit.viewport().setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.textEdit_2.viewport().setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.textEdit_3.viewport().setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.textEdit_4.viewport().setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.textEdit_2.hide()
        self.textEdit_3.hide()
        self.textEdit_4.hide()
        self.textEdit_2.first_time = True
        self.textEdit_3.first_time = True
        self.textEdit_4.first_time = True
        self.vertexes = dict()
        self.ver_label = QtWidgets.QLabel("Vertices: {}".format(len(self.vertexes.keys())), self)
        self.status_label = QtWidgets.QLabel("Not ready", self)
        self.coords_label = QtWidgets.QLabel('', self)
        self.coords_label.setStyleSheet("""color: white;
                                           font: 10pt "Verdana";""")
        self.statusbar.addWidget(self.status_label, 2)
        self.statusbar.addWidget(self.coords_label, 1)
        self.statusbar.addPermanentWidget(self.ver_label, 1)
        self.groupBox.prevHeight = 20
        self.ready = False
        self.posit = None
        self.end_val = 0
        self.spinBox.endless = True
        self.pauseFlag = False
        self.runningFlag = False
        self.point = QtCore.QObject()
        self.color = None
        self.loop = QtCore.QEventLoop()
        self.oImage = QtGui.QImage(":/board.png")
        self.oImage.scaled(self.width(), self.height())
        self.plt = QtGui.QPalette()
        self.plt.setBrush(self.plt.Window, QtGui.QBrush(self.oImage))
        self.setPalette(self.plt)
        self.show()
        self.spinBox.valueChanged.connect(self.spin_box_value)
        self.startButton.clicked.connect(self.start)
        self.speed.valueChanged.connect(self.speed_change)
        self.pauseButton.clicked.connect(self.pause)
        self.stopButton.clicked.connect(self.stop)
        self.groupBox.toggled.connect(self.hide_group_box)

    def spin_box_value(self, val):
        """Track changing spinBox value

        This method tracks changing the spin box value to decide if it should run until it reaches the given value

        :param val: value of the spinBox
        """
        if not self.runningFlag:
            if val != 0:
                self.end_val = self.spinBox.value()
                self.spinBox.endless = False
            else:
                self.end_val = 0
                self.spinBox.endless = True

    def del_dot(self, dot):
        """Delete dot

        Deletes a given QDot object and cleans up after. Shifts numbering of the other dots.

        :param dot: QDot object
        """
        assert isinstance(dot, QDot), 'dot type must be QDot object'
        global k
        for i in self.vertexes.keys():
            if self.vertexes[i] == dot:
                dot.deleteLater()
                del self.vertexes[i]
                break
        temp = dict()
        for i, j in enumerate(self.vertexes):
            temp[i] = self.vertexes[j]
            temp[i].setText('{}'.format(i))
        self.vertexes = temp
        k -= 1
        self.coords_label.setText('')

    def hide_group_box(self):
        """Hides group box

        :param args: any value
        """
        t = self.groupBox.height()
        self.groupBox.setFixedHeight(self.groupBox.prevHeight)
        self.groupBox.prevHeight = t

    def stop(self):
        """Stop running

        Stops the running algorithm and cleans up the working area
        """
        global k
        k = 0
        for i in self.vertexes:
            self.vertexes[i].deleteLater()
        self.vertexes.clear()
        self.spinBox.setDisabled(False)
        self.lineEdit.setDisabled(False)
        self.lineEdit_2.setDisabled(False)
        self.posit = None
        self.pause()
        self.runningFlag = False
        self.point.deleteLater()
        self.point = QtCore.QObject()
        self.color = None
        self.loop = QtCore.QEventLoop()
        self.oImage = QtGui.QImage(":/board.png")
        self.plt = QtGui.QPalette()
        self.plt.setBrush(self.plt.Window, QtGui.QBrush(self.oImage))
        self.setPalette(self.plt)
        self.spinBox.setValue(0)
        self.end_val = 0
        self.spinBox.endless = True
        m.prevVer1 = 0

    def pause(self):
        """Pause running"""
        self.pauseFlag = True
        self.textEdit_4.hide()

    def speed_change(self):
        """Change running speed

        Changes the speed of the algorithm.
        """
        self.speed_label.setText(str(self.speed.value())+'%')

    def start(self):
        """Start algorithm

        Starts algorithm of Chaos Game method.
        """
        if not self.ready or (self.runningFlag and not self.pauseFlag):
            return
        self.textEdit_3.hide()
        self.spinBox.setDisabled(True)
        self.lineEdit.setDisabled(True)
        self.lineEdit_2.setDisabled(True)
        if self.textEdit_4.first_time:
            self.textEdit_4.first_time = False
            self.textEdit_4.show()
        allowed_vertexes = list(map(int, self.lineEdit.text().split(',')))
        r1, r2 = tuple(map(int, self.lineEdit_2.text().split(':')))
        relation = r1 / r2
        if isinstance(self.point, QDot):
            if self.pauseFlag:
                self.pauseFlag = False
            self.loop = QtCore.QEventLoop()
            i = -1
            if not self.spinBox.endless:
                i = 0
            self.posit = self.point.pos()
            self.runningFlag = True
            while i < self.end_val:
                QtCore.QTimer.singleShot((1000 // self.speed.value())-10, self.loop.quit)
                self.loop.exec_()
                if self.pauseFlag:
                    break
                x, y, ver = m.Fractal(self.posit.x(), self.posit.y(), self.vertexes,
                                      allowed_vertexes, relation).coordinates()
                self.posit = QtCore.QPoint(x, y)
                self.color = ver.color
                self.update()
                if self.spinBox.endless:
                    self.spinBox.setValue(self.spinBox.value() + 1)
                else:
                    self.spinBox.setValue(self.spinBox.value() - 1)
                    i += 1

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

    def closeEvent(self, *args):
        self.stop()
        self.close()

    def paintEvent(self, ev):
        qp = QtGui.QPainter(self.oImage)
        qp.setRenderHint(QtGui.QPainter.Antialiasing)
        if self.color:
            pen = QtGui.QPen(self.color)
            qp.setPen(pen)
            qp.drawPoint(self.posit)
            self.plt.setBrush(self.plt.Window, QtGui.QBrush(self.oImage))
            self.setPalette(self.plt)
        self.ver_label.setText("Vertices: {}".format(len(self.vertexes.keys())))
        self.ver_label.setStyleSheet("""color: red;
                                     font: 10pt "Verdana";""")
        self.status_label.setText("Not ready")
        self.status_label.setStyleSheet("""color: red;
                                           font: 10pt "Verdana";""")
        if not self.runningFlag and len(self.vertexes.keys()) > 2:
            self.ready = False
            self.ver_label.setStyleSheet("""color: green;
                                            font: 10pt "Verdana";""")
            if isinstance(self.point, QDot):
                self.textEdit.hide()
                if self.textEdit_2.first_time:
                    self.textEdit_2.first_time = False
                    self.textEdit_2.show()
                if self.lineEdit.text() and self.lineEdit_2.text():
                    t1 = self.lineEdit.text().split(',')
                    t2 = self.lineEdit_2.text().split(':')
                    try:
                        t2 = list(map(lambda x: 0 < int(x), t2))
                        if not ((all(map(lambda x: 0 <= int(x) < 6, t1))
                                or all(t2)) and len(t2) == 2):
                            return
                        else:
                            self.textEdit_2.hide()
                            if self.textEdit_3.first_time:
                                self.textEdit_3.first_time = False
                                self.textEdit_3.show()
                            self.ready = True
                            self.status_label.setText('Ready')
                            self.status_label.setStyleSheet("""color: green;
                                                               font: 10pt "Verdana";""")
                    except ValueError:
                        return
        elif self.runningFlag:
            self.ver_label.setStyleSheet("""color: green;
                                            font: 10pt "Verdana";""")
            self.status_label.setText("Running")
            self.status_label.setStyleSheet("""color: green;
                                               font: 10pt "Verdana";""")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = GUI()
    sys.exit(app.exec_())

import cv2
import sys
import os
from datetime import datetime
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import QCoreApplication

class ShowVideo(QtCore.QObject):
    flag = 0

    cap = cv2.VideoCapture(0)

    ret, image = cap.read()
    height, width = image.shape[:2]

    VideoSignal1 = QtCore.pyqtSignal(QtGui.QImage)
    VideoSignal2 = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, parent=None):
        super(ShowVideo, self).__init__(parent)

    @QtCore.pyqtSlot()
    def startVideo(self):
        push_button1.setEnabled(False)
        push_button2.setEnabled(True)
        push_button3.setEnabled(True)
        global image
        fourcc = cv2.VideoWriter_fourcc(*'DIVX')

        if not os.path.exists(os.getcwd()+'\\'+datetime.now().now().strftime("%Y_%m_%d")):
            os.makedirs(os.getcwd()+'\\'+datetime.now().now().strftime("%Y_%m_%d"))

        out = cv2.VideoWriter(datetime.now().now().strftime("%Y_%m_%d")+'\\'+datetime.now().now().strftime("%H시%M분%S초")+'.avi', fourcc, 20.0, (640, 480))

        self.run_video = True
        if self.run_video == True:
            while self.run_video:
                ret, image = self.cap.read()
                color_swapped_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                qt_image1 = QtGui.QImage(color_swapped_image.data,
                                        self.width,
                                        self.height,
                                        color_swapped_image.strides[0],
                                        QtGui.QImage.Format_RGB888)
                self.VideoSignal1.emit(qt_image1)

                out.write(image)

                loop = QtCore.QEventLoop()
                QtCore.QTimer.singleShot(25, loop.quit) #25 ms
                loop.exec_()

    def pause(self):
        self.run_video=False
        push_button1.setEnabled(True)
        push_button2.setEnabled(False)

class ImageViewer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)
        self.image = QtGui.QImage()
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(0, 0, self.image)
        self.image = QtGui.QImage()

    def initUI(self):
        self.setWindowTitle('Test')

    @QtCore.pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        if image.isNull():
            print("Viewer Dropped frame!")

        self.image = image
        if image.size() != self.size():
            self.setFixedSize(image.size())
        self.update()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    thread = QtCore.QThread()
    thread.start()
    vid = ShowVideo()
    vid.moveToThread(thread)

    image_viewer1 = ImageViewer()

    vid.VideoSignal1.connect(image_viewer1.setImage)

    push_button1 = QtWidgets.QPushButton('▶')
    push_button2 = QtWidgets.QPushButton('||')
    push_button3 = QtWidgets.QPushButton('■')

    push_button2.setEnabled(False)
    push_button3.setEnabled(False)

    push_button1.clicked.connect(vid.startVideo)
    push_button2.clicked.connect(vid.pause)
    push_button3.clicked.connect(QCoreApplication.instance().quit)

    vertical_layout = QtWidgets.QVBoxLayout()
    horizontal_layout = QtWidgets.QHBoxLayout()
    horizontal_layout.addWidget(image_viewer1)
    vertical_layout.addLayout(horizontal_layout)
    vertical_layout.addWidget(push_button1)
    vertical_layout.addWidget(push_button2)
    vertical_layout.addWidget(push_button3)

    layout_widget = QtWidgets.QWidget()
    layout_widget.setLayout(vertical_layout)

    main_window = QtWidgets.QMainWindow()
    main_window.setCentralWidget(layout_widget)
    main_window.show()
    sys.exit(app.exec_())
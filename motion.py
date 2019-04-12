import sys
import cv2
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
import numpy as np


class skripsi(QtWidgets.QMainWindow):
    def __init__(self):
        super (skripsi,self).__init__()
        uic.loadUi('design2.ui',self)
        self.image=None

        self.btnRef.clicked.connect(self.load_image)
        self.btnRef.setStyleSheet("background-color: green ; color:white")

        self.btnStop.clicked.connect(self.stop_webcam)
        self.btnStop.setStyleSheet("background-color: red ")

        self.label_8.setStyleSheet("color:red")

        self.btnDetec.setCheckable(True)
        self.btnDetec.toggled.connect(self.detec_webcam_motion)
        self.btnDetec.setStyleSheet("color:blue")

        self.motion_Enabled = False
        self.motionFrame = None

    def detec_webcam_motion(self,status):
        if status:
            self.motion_Enabled = True
            self.btnDetec.setText("Stop Detection")
        else:
            self.motion_Enabled = False
            self.btnDetec.setText("Detection")

    def gray(self,ret):
        gray = cv2.cvtColor(self.image.copy(), cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        self.motionFrame = gray
        self.arrayEdit.setText(str(gray))
        self.displayImage(self.motionFrame, 2)

    def load_image(self):
        self.capture = cv2.VideoCapture("sampel.mp4")
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 221)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 321)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(60)
        fps = int(self.capture.get(cv2.CAP_PROP_FPS))
        self.lineFps.setText(str(fps))
        self.lineFps.setStyleSheet("color:black")
        frame = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.lineFrame.setText(str(frame))
        self.lineFrame.setStyleSheet("color:black")

    def update_frame(self):
        ret,self.image = self.capture.read()
        self.image = cv2.flip(self.image,1)

        if (self.motion_Enabled):
            detected_motion = self.detect_motion(self.image.copy())
            self.displayImage(detected_motion,1)
            self.gray(self.image)
        else:
            self.displayImage(self.image,1)
            self.gray(self.image)

    def detect_motion(self,input_image):
        self.text = "No Motion"
        gray = cv2.cvtColor(input_image,cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        abs_diff = cv2.absdiff(self.motionFrame,gray)
        thresh = cv2.threshold(abs_diff,int(self.lineTh.text()),255,cv2.THRESH_BINARY)[1]

        self.displayImage(thresh,3)
        self.diffLabel.setText(str(abs_diff))

        thresh = cv2.dilate(thresh,None,iterations = 5)
        cnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)


        try:
            hierarchy = hierarchy[0]
        except:
            hierarchy = []

        heigh,width,channels = input_image.shape

        min_x,min_y = width,heigh
        max_x = max_y = 0

        for contour,hier in zip(cnts,hierarchy):
            (x,y,w,h) = cv2.boundingRect(contour)
            min_x,max_x = min(x,min_x),max(x+w,max_x)
            min_y,max_y = min(y,min_y),max(y+h,max_y)

        if max_x - min_x > 35 and max_y - min_y > 70 :
            cv2.rectangle(input_image,(min_x,min_y),(max_x,max_y),(0,255,0),3)
            self.text = "Motion Detection"

        cv2.putText(input_image,"".format(self.warnText.setText(self.text)), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,255,0),2)
        self.warnText.setStyleSheet("color:red")

        return input_image

    def stop_webcam(self):
        self.timer.stop()

    def displayImage(self,img,window = 1):
        qformat = QImage.Format_Indexed8

        if len(img.shape) == 3:
            if img.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888

        outImage = QImage(img,img.shape[1],img.shape[0],img.strides[0],qformat)
        outImage = outImage.rgbSwapped()

        if window == 1:
            self.refLabel.setPixmap(QPixmap.fromImage(outImage))
            self.refLabel.setScaledContents(True)
        if window == 2:
            self.grayLabel.setPixmap(QPixmap.fromImage(outImage))
            self.grayLabel.setScaledContents(True)
        if window == 3:
            self.thresLabel.setPixmap(QPixmap.fromImage(outImage))
            self.thresLabel.setScaledContents(True)

if __name__ == '__main__':
        app = QtWidgets.QApplication(sys.argv)
        window = skripsi()
        window.setWindowTitle('MOTION DETECTION')
        window.show()
        sys.exit(app.exec_())
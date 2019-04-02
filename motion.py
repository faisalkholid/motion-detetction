import sys
from _socket import gaierror

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
        self.btnStop.clicked.connect(self.stop_webcam)

        self.btnDetec.setCheckable(True)
        self.btnDetec.toggled.connect(self.detec_webcam_motion)
        self.motion_Enabled=False

        # self.btnRefer.clicked.connect(self.set_motion_image)
        self.motionFrame=None

    def detec_webcam_motion(self,status):
        if status:
            self.motion_Enabled=True
            self.btnDetec.setText("Stop Motion")
        else:
            self.motion_Enabled = False
            self.btnDetec.setText("Detec Motion")

    def gray(self,ret):
        gray = cv2.cvtColor(self.image.copy(), cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        self.motionFrame = gray
        self.arrayEdit.setText(str(gray))
        self.displayImage(self.motionFrame, 2)

    # def set_motion_image(self):
    #     gray = cv2.cvtColor(self.image.copy(),cv2.COLOR_BGR2GRAY)
    #     gray = cv2.GaussianBlur(gray,(21,21),0)
    #     self.motionFrame=gray
    #     thresh = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)[1]
    #     self.displayImage(thresh, 4)
    #     self.displayImage(self.motionFrame,3)

    def load_image(self):
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)

    def update_frame(self):
        ret,self.image=self.capture.read()
        self.image = cv2.flip(self.image,1)

        if (self.motion_Enabled):
            detected_motion=self.detect_motion(self.image.copy())
            self.displayImage(detected_motion,1)
            self.gray(self.image)
        else:
            self.displayImage(self.image,1)
            self.gray(self.image)

    def detect_motion(self,input_image):
        self.text = "No motion"
        gray = cv2.cvtColor(input_image,cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray,(21,21),0)
        self.displayImage(self.motionFrame, 2)
        framediff=cv2.absdiff(self.motionFrame,gray)
        thresh = cv2.threshold(framediff,40,255,cv2.THRESH_BINARY)[1]
        self.displayImage(thresh,5)
        # self.treshText.setText(str())
        self.diffLabel.setText(str(framediff))

        thresh = cv2.dilate(thresh,None,iterations=5)
        cnts, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        try:
            hierarchy=hierarchy[0]
        except:
            hierarchy=[]

        heigh,width,channels=input_image.shape

        min_x,min_y=width,heigh
        max_x=max_y=0

        for contour,hier in zip(cnts,hierarchy):
            (x,y,w,h)=cv2.boundingRect(contour)
            min_x,max_x=min(x,min_x),max(x+w,max_x)
            min_y,max_y=min(y,min_y),max(y+h,max_y)

        if max_x - min_x > 80 and max_y-min_y > 80 :
            cv2.rectangle(input_image,(min_x,min_y),(max_x,max_y),(0,255,0),3)
            self.text="Motion Detection"

        cv2.putText(input_image,"".format(self.warnText.setText(self.text)), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,255,0),2)

        return input_image

    def stop_webcam(self):
        self.timer.stop()

    def displayImage(self,img,window=1):
        qformat=QImage.Format_Indexed8

        if len(img.shape) == 3:
            if img.shape[2] == 4:
                qformat=QImage.Format_RGBA8888
            else:
                qformat=QImage.Format_RGB888

        outImage=QImage(img,img.shape[1],img.shape[0],img.strides[0],qformat)
        outImage=outImage.rgbSwapped()

        if window == 1:
            self.refLabel.setPixmap(QPixmap.fromImage(outImage))
            self.refLabel.setScaledContents(True)
        if window == 2:
            self.grayLabel.setPixmap(QPixmap.fromImage(outImage))
            self.grayLabel.setScaledContents(True)
        if window == 3:
            self.referLabel.setPixmap(QPixmap.fromImage(outImage))
            self.referLabel.setScaledContents(True)
        if window == 4:
            self.thresLabel.setPixmap(QPixmap.fromImage(outImage))
            self.thresLabel.setScaledContents(True)
        if window == 5:
            self.currLabel.setPixmap(QPixmap.fromImage(outImage))
            self.currLabel.setScaledContents(True)


if __name__ == '__main__':
        app = QtWidgets.QApplication(sys.argv)
        window = skripsi()
        window.setWindowTitle('MOTION DETECTION')
        window.show()
        sys.exit(app.exec_())
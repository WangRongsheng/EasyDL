from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPixmap,QIcon

from PyQt5.QtWidgets import QMenu, QPushButton, QApplication, QMainWindow, QAction, QFileDialog, QLabel, QDesktopWidget, QVBoxLayout, QGridLayout,QGroupBox,QWidget,QBoxLayout, QDockWidget
from PyQt5.QtCore import QCoreApplication
import sys
import os
import json
import requests
import base64
import cv2

from PyQt5 import QtWidgets

def chngdir(s):
    cfile=''
    for i in s:
        if i == '\\':
            cfile += '/'
        else:
            cfile += i
    return cfile

def makenImgName(path):
    fileName=path
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&AK' \
           '&SK'
    response = requests.get(host)
    content = response.json()
    access_token = content["access_token"]
    imgpath = fileName
    image = open(r'{}'.format(imgpath), 'rb').read()
    data = {'image': base64.b64encode(image).decode()}
    request_url = "https://aip.baidubce.com/rpc/2.0/ai_custom_pro/v1/classification/rmb-wrs" + "?access_token=" + access_token
    response = requests.post(request_url, data=json.dumps(data))
    content = response.json()
    content_result = content['results']
    return content_result


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title="EasyDL"
        #self.top=50
        #self.left=50
        self.width=1200
        self.height=800
        self.curimg=None
        self.curdir=None
        self.setWindowIcon(QtGui.QIcon("logo.png"))
        self.labelimg = QLabel(self)
        #self.setStyleSheet("background-color: orange;")
        self.setWindowTitle(self.title)
        #self.setGeometry(self.top, self.left, self.width, self.height)
        self.setFixedSize(self.width, self.height)
        self.cadir =os.getcwd()
        self.appLayoutCreation()
        self.VBox = QVBoxLayout()
        self.VBox.addWidget(self.layout)

        self.wid = QWidget(self)
        self.wid.setLayout(self.VBox)
        self.setCentralWidget(self.wid)


        self.create_menubar()
        self.InitWindow()

    def create_menubar(self):
        mainmenu = self.menuBar()
        fileMenu = mainmenu.addMenu("File")

        #open image
        openfbtn=QAction('Open Image',self)
        openfbtn.triggered.connect(self.openf)
        fileMenu.addAction(openfbtn)

    def InitWindow(self):
        self.showMaximized()

    def openf(self):
        options=QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Image", "","All Files (*);;Image Files (*.png *.jpg *.jpeg)", options=options)
        res={}
        res=makenImgName(fileName)
        num=0
        for res_content in res:
            num=num+1

        if fileName:
            self.curimg=fileName
            self.imgfiles=None
            self.imgtop=-1
            self.display_img(fileName)

        errorKey = 1
        cnt=0

        cimg = cv2.imread(fileName)

        for res_content in res:
            cnt=cnt+1
            if res_content['name'] == '1' and res_content['score'] < 0.8:
                errorKey=1
            if res_content['name'] == '5':
                errorKey=5
            if res_content['name'] == '10':
                errorKey=10
            if res_content['name'] == '20':
                errorKey=20
            if res_content['name'] == '50':
                errorKey=50
            if res_content['name'] == '100':
                errorKey=100
            message = QtWidgets.QMessageBox.warning(self, "结果", "EasyDL识别结果为：{}元！".format(errorKey),
                                                        QtWidgets.QMessageBox.Cancel)
            break

    def openF(self):
        dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if dir:
            self.curdir=dir
            self.imgfiles = []
            self.imgtop=0
            self.curimg=None
            for file in os.listdir(self.curdir):
                if file.endswith(".jpeg") or file.endswith(".jpg") or file.endswith(".png") or file.endswith(".JPEG") or file.endswith(".JPG") or file.endswith(".PNG"):
                    self.imgfiles.append(self.curdir+'/'+file)
            self.display_img(self.imgfiles[self.imgtop])

    def lftimg(self):
        if self.curimg==None:
            if self.imgtop==0:
                self.imgtop=len(self.imgfiles)-1
            else:
                self.imgtop-=1
            self.display_img(self.imgfiles[self.imgtop])
    def rhtimg(self):
        if self.curimg==None:
            if self.imgtop==len(self.imgfiles)-1:
                self.imgtop=0
            else:
                self.imgtop+=1
            self.display_img(self.imgfiles[self.imgtop])

    def appLayoutCreation(self):
        self.leftimg=QPushButton("<",self)
        self.leftimg.setToolTip("<h3>Left Image</h3>")
        self.leftimg.clicked.connect(self.lftimg)

        self.rightimg = QPushButton(">", self)
        self.rightimg.setToolTip("<h3>Right Image</h3>")
        self.rightimg.clicked.connect(self.rhtimg)


        self.layout=QGroupBox("")
        self.layoutbox=QGridLayout()

        self.layoutbox.addWidget(self.labelimg, 0, 1, 3, 5)


        self.layoutbox.addWidget(self.leftimg, 4, 0)
        self.layoutbox.addWidget(self.rightimg, 4, 6)



        self.layout.setLayout(self.layoutbox)



    def display_img(self,filename):
        img=QPixmap(filename)
        img= img.scaled(480, 480, QtCore.Qt.KeepAspectRatio)
        self.labelimg.setPixmap(img)
        self.labelimg.setAlignment(QtCore.Qt.AlignCenter)



App=QApplication(sys.argv)
window=Window()
sys.exit(App.exec())
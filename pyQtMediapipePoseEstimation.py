from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog,QMessageBox
from PyQt5.QtGui import QImage
import sqlite3
import cv2, imutils
import mediapipe as mp
import numpy as np
import csv

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10,10,640,480))
        font = QtGui.QFont()
        font.setPointSize(36)
        self.label.setFont(font)
        self.label.setObjectName("label")

        self.txtEklendi = QtWidgets.QLabel(self.centralwidget)
        self.txtEklendi.setText("")
        font_txtEklendi = QtGui.QFont()
        font_txtEklendi.setPointSize(13)
        self.txtEklendi.setFont(font_txtEklendi)
        self.txtEklendi.setObjectName("txtEklendi")
        self.txtEklendi.setGeometry(QtCore.QRect(660, 200, 101, 22))


        #Combobox
        self.cmb_class_name = QtWidgets.QComboBox(self.centralwidget)
        self.cmb_class_name.setGeometry(QtCore.QRect(660, 90, 101, 22))
        self.cmb_class_name.setObjectName("cmb_class_name")
        self.cmb_class_name.setPlaceholderText("Seçiniz")

        cmb_list = ["asfcsd"]
        self.cmb_class_name.addItems(cmb_list)


        #DB
        self.conn = sqlite3.connect('filename.db')
        self.c = self.conn.cursor()

        # Class İsimlerinin olduğu Txt kutusu
        self.txtClassName = QtWidgets.QLineEdit(self.centralwidget)
        self.txtClassName.resize(100,30)
        self.txtClassName.setGeometry(QtCore.QRect(660, 10, 101, 22))
        self.txtClassName.setPlaceholderText("Yeni Class İsmi")

        #Resim Yükleme Butonu
        self.btn_load_image = QtWidgets.QPushButton(self.centralwidget)
        self.btn_load_image.setObjectName("btn_load_image")
        self.btn_load_image.setGeometry(QtCore.QRect(250, 530, 101, 22))

        #Class Ekleme Butonu
        self.btn_class_save = QtWidgets.QPushButton(self.centralwidget)
        self.btn_class_save.setObjectName("btn_class_save")
        self.btn_class_save.setGeometry(QtCore.QRect(660, 40, 101, 22))

        #Resim İlerleme Butonu
        self.btnNext = QtWidgets.QPushButton(self.centralwidget)
        self.btnNext.setObjectName("btnNext")
        self.btnNext.setGeometry(QtCore.QRect(350, 530, 101, 22))

        #Resim Kayıt etme butonu
        self.btnSave = QtWidgets.QPushButton(self.centralwidget)
        self.btnSave.setObjectName("btnSave")
        self.btnSave.setGeometry(QtCore.QRect(450, 530, 101, 22))

        #

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 0, 0))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionNext = QtWidgets.QAction(MainWindow)
        self.actionNext.setObjectName("actionNext")
        self.menuFile.addAction(self.actionNext)
        self.menuFile.addAction(self.actionSave)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.actionNext.triggered.connect(lambda: self.clicked("Next clicked"))
        self.actionSave.triggered.connect(lambda: self.clicked("Save clicked"))

        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))

        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        
        self.actionNext.setText(_translate("MainWindow", "Next"))
        self.actionNext.setShortcut(_translate("MainWindow", "Ctrl+N"))


        self.txtClassName.setText(_translate("MainWindow", ""))

        #Buton Aksiyonları
        self.btnNext.clicked.connect(self.nextImage)
        self.btnNext.setText(_translate("MainWindow", "Nextİmage"))

        self.btn_class_save.clicked.connect(self.save_class_cmb)
        self.btn_class_save.setText(_translate("MainWindow", "Class Ekle"))

        self.btnSave.clicked.connect(self.savePhoto)
        self.btnSave.setText(_translate("MainWindow", "Save"))

        self.btn_load_image.setText(_translate("MainWindow", "Open"))
        self.btn_load_image.clicked.connect(self.loadImage)


        #Global Degisgenler
        self.filename = list() # Will hold the image address location
        self.dosyaSayisi=len(self.filename)
        self.sayac = 0
        self.eklendi=list()
        self.tmp = None # Will hold the temporary image for display
        self.brightness_value_now = 0 # Updated brightness value
        self.blur_value_now = 0 # Updated blur value
        self.angles=list()
        self.className=[]


    def clicked(self, text):
        if text=="Save clicked":
            self.savePhoto()
        elif text=="Next clicked":
            self.nextImage()
        
    def save_class_cmb(self):
        if len(self.txtClassName.text())>0:
            self.cmb_class_name.addItem(self.txtClassName.text())
        else:
            pass

    def calculate_angle(self,a,b,c):
        a = np.array(a) 
        b = np.array(b) 
        c = np.array(c) 
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle >180.0:
            angle = 360-angle
            
        return angle 

    def pose(self,image):
        mp_drawing = mp.solutions.drawing_utils
        mp_pose = mp.solutions.pose
        angles = []

        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5,model_complexity=2) as pose:
                img=cv2.imread(image)
                frame = cv2.resize(img,(800,800))
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(image)
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                try:
                    landmarks = results.pose_landmarks.landmark

                    try:
                        elbowL = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                    except:
                        print("elbowL bulunamadı")
                        pass

                    try:
                        shoulderL = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]  
                    except:
                        print("shoulderL bulunamadı")
                        pass
                    try:
                        hipL = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y] 
                    except:
                        print("hipL bulunamadı")
                        pass
                    try:
                        elbowR = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                        print("elbowR bulunamadı")
                    except:
                        pass

                    try:
                        shoulderR = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    
                    except:
                        print("shoulderR bulunamadı")
                        pass

                    try:
                        hipR = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y] 
                    except:
                        print("hipR bulunamadı")

                        pass

            
                    try:
                        wristL = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                    except:
                        print("wristL bulunamadı")

                        pass
                
                    try:
                        wristR = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    except:
                        print("wristR bulunamadı")

                        pass

                    try:
                        kneeL = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                    except:
                        print("kneeL bulunamadı")

                        pass

                    try:
                        kneeR = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                    
                    except:
                        print("kneeR bulunamadı")

                        pass

                    
                    try:
                        ankleL = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                    
                    except:
                        print("ankleL bulunamadı")

                        pass
                    try:
                        ankleR = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
                    
                    except:
                        print("ankleR bulunamadı")

                    
                    try:

                        shoulderLangle = self.calculate_angle(elbowL, shoulderL, hipL)
                        shoulderRangle = self.calculate_angle(elbowR, shoulderR, hipR)
                        print("shoulderRangle")
                    except:
                        print("shoulderRangle")
                        pass

                    try:

                
                        elbowLangle = self.calculate_angle(shoulderL, elbowL, wristL)
                        elbowRangle = self.calculate_angle(shoulderR, elbowR, wristR)
                        print("elbowRangle")

                    
                    except:
                        print("nelbowRangle")
                        pass

                    try:
                        hipLangle = self.calculate_angle(shoulderL, hipL, kneeL)
                        hipRangle = self.calculate_angle(shoulderR, hipR, kneeR)
                        print("hipRangle")

                        
                    
                    except:
                        print("nhipRangle")
                        pass
                    # Calculate angle

                    try:

                        kneeLangle = self.calculate_angle(hipL, kneeL, kneeL)
                        kneeRangle = self.calculate_angle(hipR, kneeR, kneeR)
                        print("kneeRangle")
                    
                    except:
                        print("nkneeRangle")

                        pass 


                    print("shoulderLangle: ",shoulderLangle,"  shoulderRangle: ",shoulderRangle,"   elbowLangle: ",
                    elbowLangle,"   elbowLangle:",elbowRangle,"   hipLangle: ",
                    hipLangle,"   hipRangle: ",hipRangle,"   kneeLangle:  ",
                    kneeLangle,"   kneeRangle: ",kneeRangle)

                    

                except:
                    pass
            
                        # Render detections
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                        mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                        mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                        )  
                self.angles=[self.cmb_class_name.currentText(),shoulderLangle,shoulderRangle,elbowLangle,elbowRangle,hipLangle,hipRangle,kneeLangle,kneeRangle]
            
        
                self.setPhoto(image)

    def loadImage(self):
        if self.cmb_class_name.currentText()=="":
            pass
        else:
            try:
                print("loadImage  Tetiklendi")
                db_filname=[]

                self.filename = QFileDialog.getOpenFileNames(filter="Image (*.*)")[0]
                sorgu=self.c.execute("SELECT resimAd FROM resimler").fetchall()

                print(sorgu)
                for i,a in enumerate(sorgu):
                    print(1,"----------------------")
                    db_filname.append(a[0])
                print(db_filname)
                for item in self.filename:
                    print("----------------------")
                    if item in db_filname:
                        print(item," db de varmış knk")
                        continue
                
                    print("insert")
                    self.c.execute("INSERT INTO resimler(class,resimAd,eklendi) VALUES(?,?,?)", (self.cmb_class_name.currentText(),item,0))
                    print(item," db ye ekledim")
                self.conn.commit()

                    
                
                print("bitti")
                try:
                    hepsi = self.c.execute("SELECT * FROM resimler").fetchall()
                    print(hepsi[1][2])
                    final_sayi=list()
                    
                    for i,a in enumerate(hepsi):
                        final_sayi.append(a[0])
                        self.className.append(a[1])
                        self.filename.append(a[2])
                        self.eklendi.append(a[3])

                    self.dosyaSayisi=len(final_sayi)	

                except:
                    pass
                self.txtClassName.setText(self.className[self.sayac])
                if self.eklendi[self.sayac]==0:
                    self.txtEklendi.setText("eklenmedi")
                elif self.eklendi[self.sayac]==1:
                    self.txtEklendi.setText("eklendi")
                else:
                    self.txtEklendi.setText("Farklı bir değer Bulundu Veri Tabanını Kontrol edin")
                self.pose(self.filename[0])
                

            except:
                pass

    def nextImage(self):
        print("next teyim")
        try:
            if self.cmb_class_name.currentText()=="":
                pass
            else:

                if self.dosyaSayisi<1:
                    pass
                elif self.sayac<self.dosyaSayisi:
                    print("elifteyim")
                    self.sayac +=1
                    self.pose(self.filename[self.sayac])
                    self.txtClassName.setText(self.className[self.sayac])

                    if self.eklendi[self.sayac]==0:
                        self.txtEklendi.setText("eklenmedi")
                    elif self.eklendi[self.sayac]==1:
                        self.txtEklendi.setText("eklendi")
                    else:
                        self.txtEklendi.setText("Farklı bir değer Bulundu Veri Tabanını Kontrol edin")
                elif self.sayac==self.dosyaSayisi and self.sayac > self.dosyaSayisi:
                            
                    QMessageBox.about(self, "Hata", "Bütün resimlere baktınız")

        except:
            pass
        

    def setPhoto(self,image):

        self.tmp = image
        image = imutils.resize(image,width=440,height=480)
        frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1],frame.shape[0],frame.strides[0],QImage.Format_RGB888)
        self.label.setPixmap(QtGui.QPixmap.fromImage(image))

    def savePhoto(self):
        print("savePhoto dayim")
        try:
            if self.cmb_class_name.currentText()=="":
                pass
            else:
                if self.sayac <= self.dosyaSayisi:
                    row=self.angles

                    with open("kordinat.csv",mode="a",newline="") as f:
                            csv_writer = csv.writer(f,delimiter=",",quotechar='"',
                                                        quoting=csv.QUOTE_MINIMAL)
                            csv_writer.writerow(row)
                    self.c.execute("Update resimler set eklendi = ? where id = ?",(1,self.sayac+1))
                    self.c.execute("INSERT INTO acilar(shoulderLangle,shoulderRangle,elbowLangle,elbowRangle,hipLangle,hipRangle,kneeLangle,kneeRangle) VALUES(?,?,?,?,?,?,?,?)",
                        (self.angles[1],self.angles[2],self.angles[3],self.angles[4],
                        self.angles[5],self.angles[6],self.angles[7],self.angles[8]))
                    self.conn.commit()
                    
                    self.eklendi[self.sayac]==1
                    self.txtEklendi.setText("eklendi")

                    self.pose(self.filename[self.sayac])
                    row.clear
                    self.angles.clear
        except:
            pass
        



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
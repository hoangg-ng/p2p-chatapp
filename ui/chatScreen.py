from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets 
from client.peer import * 
import time

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)


class Ui_ChatScreen(QDialog):

    def __init__(self, username, password, serverChannel, previousWindow):
        super(Ui_ChatScreen, self).__init__()
        self.username = username
        self.password = password
        self.channel = serverChannel
        self.peer = PeerClient(username, ui = self)
        self.previousWindow = previousWindow
    
    def browserFiles(self):
        print("dit me")
        fname, _ = QFileDialog.getOpenFileName(self, 'Open File', QDir.rootPath())
        self.te_file.setText(fname)
    
    def chatR(self,name):
        self.onayB.setVisible(True)
        self.retB.setVisible(True)
        global flagQ
        flagQ = [name, 0]
        print("Chat geldi")
        self.onaytext.setText("Chat request: " + str(name))

    def getUsername(self):
        return self.te_username.text()

    def getMessage(self):
        mess=self.te_message.toPlainText()
        self.te_message.setText('')
        return mess

    def setupUi(self, ChatScreen):

        ChatScreen.setObjectName(_fromUtf8("ChatScreen"))
        ChatScreen.resize(1000, 750)
        self.tb_chatscreen = QTextBrowser(ChatScreen)
        self.tb_chatscreen.setGeometry(QtCore.QRect(40, 80, 591, 491))
        self.tb_chatscreen.setObjectName(_fromUtf8("tb_chatscreen"))
        self.te_message = QTextEdit(ChatScreen)
        self.te_message.setGeometry(QtCore.QRect(40, 580, 471, 31))
        self.te_message.setObjectName(_fromUtf8("te_message"))
        self.btn_send = QPushButton(ChatScreen)
        self.btn_send.setGeometry(QtCore.QRect(520, 580, 111, 31))
        self.btn_send.setObjectName(_fromUtf8("btn_send"))
        self.textBrowser = QTextBrowser(ChatScreen)
        self.textBrowser.setGeometry(QtCore.QRect(680, 30, 256, 541))
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.label = QLabel(ChatScreen)
        self.label.setGeometry(QtCore.QRect(60, 36, 75, 16))
        
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        
        self.te_username = QLineEdit(ChatScreen)
        self.te_username.setGeometry(QtCore.QRect(280, 30, 231, 31))
        self.te_username.setObjectName(_fromUtf8("te_username"))

        self.te_file = QLineEdit(ChatScreen)
        self.te_file.setGeometry(QtCore.QRect(40,620, 200, 30))
        self.te_file.setObjectName(_fromUtf8("te_file"))
        
        self.filebutton = QPushButton(ChatScreen)
        self.filebutton.setGeometry(QtCore.QRect(250, 620, 100, 30))
        self.filebutton.setObjectName(_fromUtf8("filebutton"))

        self.sendfile_btn = QPushButton(ChatScreen)
        self.sendfile_btn.setGeometry(QtCore.QRect(350, 620, 100, 30))
        self.sendfile_btn.setObjectName(_fromUtf8("sendfile"))
        # self.label_2 = QLabel(ChatScreen)
        # self.label_2.setGeometry(QtCore.QRect(320, 36, 51, 16))
        # font = QtGui.QFont()
        # font.setBold(True) 
        # font.setWeight(75)

        # self.label_2.setFont(font)
        # self.label_2.setObjectName(_fromUtf8("label_2"))
        # self.te_port = QTextEdit(ChatScreen)
        # self.te_port.setGeometry(QtCore.QRect(370, 30, 131, 31))
        # self.te_port.setObjectName(_fromUtf8("te_port"))
        
        self.btn_connect = QPushButton(ChatScreen)
        self.btn_connect.setGeometry(QtCore.QRect(520, 30, 111, 31))
        self.btn_connect.setObjectName(_fromUtf8("btn_connect"))
        self.btn_refresh = QPushButton(ChatScreen)
        self.btn_refresh.setGeometry(QtCore.QRect(845, 580, 91, 31))
        self.btn_refresh.setObjectName(_fromUtf8("btn_refresh"))

        self.btn_logout = QPushButton(ChatScreen)
        self.btn_logout.setGeometry(QtCore.QRect(680,580,91,31))
        self.btn_logout.setObjectName(_fromUtf8("btn_logout"))

        self.logout_message = QLabel(ChatScreen)
        self.logout_message.setGeometry(QtCore.QRect(130, 100, 731, 401))
        font2 = QtGui.QFont()
        font2.setPointSize(18)
        font2.setBold(True)
        font2.setWeight(75)
        self.logout_message.setFont(font2)
        self.logout_message.setObjectName(_fromUtf8("logout_message"))
        self.logout_message.setVisible(False)

        self.onaytext = QLabel(ChatScreen)
        self.onaytext.setGeometry(QtCore.QRect(650, 640, 450, 31))

        self.onaytext.setFont(font)
        self.onaytext.setText("Incoming Request")

        self.onayB = QPushButton(ChatScreen)
        self.onayB.setGeometry(QtCore.QRect(600, 690, 91, 31))
        self.onayB.setText("Accept")

        self.retB = QPushButton(ChatScreen)
        self.retB.setGeometry(QtCore.QRect(700, 690, 91, 31))
        self.retB.setText("Reject")


        self.btn_logout.clicked.connect(self.peer.logout)
        self.btn_send.clicked.connect(self.peer.send_messages)
        self.btn_connect.clicked.connect(self.peer.send_request_to_peer)

        self.onayB.clicked.connect(self.peer.accept_request)
        self.retB.clicked.connect(self.peer.reject_request)

        self.btn_refresh.clicked.connect(self.peer.refreshOnline)
        self.peer.refreshOnline()

        self.onayB.setVisible(False)
        self.retB.setVisible(False)

        
        self.filebutton.clicked.connect(self.peer.browserFile)
        self.sendfile_btn.clicked.connect(self.peer.sendFile)
        self.retranslateUi(ChatScreen)
        QtCore.QMetaObject.connectSlotsByName(ChatScreen)

    

    def retranslateUi(self, ChatScreen):
        ChatScreen.setWindowTitle(_translate("ChatScreen", "P2P Chat Application", None))
        self.btn_send.setText(_translate("ChatScreen", "Send", None))
        self.label.setText(_translate("ChatScreen", "Username :", None))
        # self.label_2.setText(_translate("ChatScreen", "PORT : ", None))
        self.btn_connect.setText(_translate("ChatScreen", "Connect", None))
        self.btn_refresh.setText(_translate("ChatScreen", "Refresh", None))
        self.btn_logout.setText(_translate("ChatSecreen", "Logout",None))
        self.logout_message.setText(_translate("ChatScreen", "YOU HAVE BEEN SUCCESSFULLY LOGGED OUT!", None))
        self.filebutton.setText(_translate("ChatScreen", "Browse", None))
        self.sendfile_btn.setText(_translate("ChatScreen","Send File", None))
    def listen(self):
        while True:
            time.sleep(1)
from ui.chatScreen import Ui_ChatScreen
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from central.server import *
from central.listenerTCP import *
from constants import *
from ui.home import Ui_MainWindow  
    

if __name__ == '__main__':

    app = QApplication(sys.argv)
    MainWindow  = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

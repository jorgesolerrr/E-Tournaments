from frontend.prove import MainWindow
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QGridLayout, QLineEdit, QTextEdit, QComboBox, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtCore import Qt
from middleware.middleware import Middleware



app = QApplication(sys.argv)
mdw = Middleware()

# Crear la ventana principal
ventana_principal = MainWindow(mdw)
ventana_principal.show()

# Ejecutar la aplicación
sys.exit(app.exec_())

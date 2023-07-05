from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QGridLayout, QLineEdit, QTextEdit, QComboBox, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtCore import Qt

import sys

from random import randint



class TournamentWindow(QMainWindow):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()

        #Crear ventana principal
        self.setWindowTitle('Torneo de Juegos')
        self.setGeometry(100, 100, 1200, 960)
        
        # Crear el layout principal
        self.layout_principal = QGridLayout()
        self.layout_principal.setSpacing(10)

        self.w =None

        self.label = QLabel('Simulador de Torneos')
        self.font = QFont("Comic Sans MS", 40)
        self.label.setMaximumHeight(100)
        self.label.setMaximumWidth(700)
        self.label.setFont(self.font)
        self.label.setGeometry(100, 100, 300, 100)
        self.label.setAlignment(Qt.AlignCenter)

        self.label_torneo = QLabel('Tipo de Torneo')
        self.font = QFont("Comic Sans MS", 30)
        self.label_torneo.setMaximumHeight(100)
        self.label_torneo.setMaximumWidth(700)
        self.label_torneo.setFont(self.font)
        self.label_torneo.setGeometry(100, 100, 300, 100)
        self.label_torneo.setAlignment(Qt.AlignCenter)
        
        self.results = QTableWidget()

        self.button_go_back = QPushButton("Atrás")
        self.button_go_back.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.button_go_back.clicked.connect(self.go_back)
        self.button_go_back.setMaximumHeight(40)
        self.button_go_back.setMaximumWidth(50)

        self.button_show_results = QPushButton("RESULTADOS")
        self.button_show_results.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.button_show_results.clicked.connect(self.show_results)
        self.button_show_results.setFont(QFont("Comic Sans MS", 10))
        self.button_show_results.setMaximumHeight(40)
        self.button_show_results.setMaximumWidth(300)



        # Agregar los widgets al layout principal
        self.layout_principal.addWidget(self.label, 0, 0, 1, 1)
        self.layout_principal.addWidget(self.label_torneo, 1, 0, 1, 1)
        self.layout_principal.addWidget(self.button_show_results, 2, 0, 1, 1)
        self.layout_principal.addWidget(self.button_go_back, 25, 1)

        # Crear el widget principal y asignarle el layout
        widget_principal = QWidget()
        widget_principal.setLayout(self.layout_principal)
        
        # Asignar el widget principal a la ventana principal
        self.setCentralWidget(widget_principal)

        # Agregar una hoja de estilo
        style = """
            QMainWindow {
                background-color: #21;
            }
            
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
            
            QTextEdit {
                font-size: 14px;
            }
            
            QComboBox {
                font-size: 14px;
            }
            
            QPushButton {
                background-color: #21
                padding: 10px 20px;
            border-radius: 5px;
            font-size: 14px;
        }
        
        QPushButton:hover {
            background-color: #1A7C7C;
        }
        
        QTextEdit[readOnly="true"] {
            background-color: #FFFFFF;
            border: none;
            border-radius: 5px;
            color: #555555;
        }
    """


        self.setStyleSheet(style)
        
        # Agregar una imagen de fondo
        self.setStyleSheet('background-image: url("C:/Users/Ernesto/Desktop/fon.jpg"); background-repeat: no-repeat; background-position: center;')

    def go_back(self, checked):
        if self.w is None:
            self.w = PlayersWindow()
            self.w.show()
            self.close()
    
    def show_results(self, checked):
        i=0
        lis = ["Juan", "Maria", "Jesus"]
        self.results.setRowCount(len(lis))
        self.results.setColumnCount(2)
        for item in lis: #sustituir self por los jugadores
            self.results.setItem(i, 0, QTableWidgetItem(item))#nombre del jugador
            self.results.setItem(i, 1, QTableWidgetItem("9"))#puntuacion
            i+=1
        self.layout_principal.addWidget(self.results, 3, 0)
        


class PlayersWindow(QMainWindow):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()

        #Crear ventana principal
        self.setWindowTitle('Torneo de Juegos')
        self.setGeometry(100, 100, 1200, 960)
        
        # Crear el layout principal
        self.layout_principal = QGridLayout()
        self.layout_principal.setSpacing(10)

        self.w = None

        self.label = QLabel('Simulador de Torneos')
        self.font = QFont("Comic Sans MS", 40)
        self.label.setMaximumHeight(100)
        self.label.setMaximumWidth(700)
        self.label.setFont(self.font)
        self.label.setGeometry(100, 100, 300, 100)
        self.label.setAlignment(Qt.AlignCenter)

        self.label_jugadores = QLabel('Cree jugadores')
        self.font = QFont("Comic Sans MS", 30)
        self.label_jugadores.setMaximumHeight(100)
        self.label_jugadores.setMaximumWidth(700)
        self.label_jugadores.setFont(self.font)
        self.label_jugadores.setGeometry(100, 100, 300, 100)
        self.label_jugadores.setAlignment(Qt.AlignCenter)

        self.texto_jugadores = QTextEdit()
        self.texto_jugadores.setPlaceholderText('Ingrese los nombres de los jugadores separados por coma')
        self.texto_jugadores.setStyleSheet('background-image: url("C:/Users/Ernesto/Desktop/si.jpg")')
        self.texto_jugadores.setMaximumHeight(100)
        self.texto_jugadores.setMaximumWidth(700)
        self.texto_jugadores.setAlignment(Qt.AlignCenter)


        self.button_continue = QPushButton("Crear Torneo")
        self.button_continue.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.button_continue.clicked.connect(self.show_new_window)
        self.button_continue.setStyleSheet('background-image: url("C:/Users/Ernesto/Desktop/trofeo.jpg")')
        self.button_continue.setMaximumHeight(180)
        self.button_continue.setMaximumWidth(180)

        self.button_go_back = QPushButton("Atrás")
        self.button_go_back.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.button_go_back.clicked.connect(self.go_back)
        self.button_go_back.setMaximumHeight(40)
        self.button_go_back.setMaximumWidth(50)



         # Agregar los widgets al layout principal
        self.layout_principal.addWidget(self.label, 0, 0, 1, 1)
        self.layout_principal.addWidget(self.label_jugadores, 1, 0, 1, 1)
        self.layout_principal.addWidget(self.texto_jugadores, 2, 0, 1, 1)
        self.layout_principal.addWidget(self.button_continue, 3, 0, 1, 2)
        self.layout_principal.addWidget(self.button_go_back, 5, 1)

        # Crear el widget principal y asignarle el layout
        widget_principal = QWidget()
        widget_principal.setLayout(self.layout_principal)
        
        # Asignar el widget principal a la ventana principal
        self.setCentralWidget(widget_principal)

        # Agregar una hoja de estilo
        style = """
            QMainWindow {
                background-color: #21;
            }
            
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
            
            QTextEdit {
                font-size: 14px;
            }
            
            QComboBox {
                font-size: 14px;
            }
            
            QPushButton {
                background-color: #21
                padding: 10px 20px;
            border-radius: 5px;
            font-size: 14px;
        }
        
        QPushButton:hover {
            background-color: #1A7C7C;
        }
        
        QTextEdit[readOnly="true"] {
            background-color: #FFFFFF;
            border: none;
            border-radius: 5px;
            color: #555555;
        }
    """


        self.setStyleSheet(style)
        
        # Agregar una imagen de fondo
        self.setStyleSheet('background-image: url("C:/Users/Ernesto/Desktop/fon.jpg"); background-repeat: no-repeat; background-position: center;')

    def show_new_window(self, checked):
        if self.w is None:
            self.w = TournamentWindow()
            self.w.show()
            self.close()

        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.

    def go_back(self, checked):
        if self.w is None:
            self.w = MainWindow()
            self.w.show()
            self.close()
        
        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        #Crear ventana principal
        self.setWindowTitle('Torneo de Juegos')
        self.setGeometry(100, 100, 1200, 960)
        
        # Crear el layout principal
        self.layout_principal = QGridLayout()
        self.layout_principal.setSpacing(10)

        self.label = QLabel('Simulador de Torneos')
        self.font = QFont("Comic Sans MS", 40)
        self.label.setMaximumHeight(100)
        self.label.setMaximumWidth(700)
        self.label.setFont(self.font)
        self.label.setGeometry(100, 100, 300, 100)
        self.label.setAlignment(Qt.AlignCenter)

        self.label_juego = QLabel('Seleccione Juego')
        self.font = QFont("Comic Sans MS", 30)
        self.label_juego.setMaximumHeight(100)
        self.label_juego.setMaximumWidth(700)
        self.label_juego.setFont(self.font)
        self.label_juego.setGeometry(100, 100, 300, 100)
        self.label_juego.setAlignment(Qt.AlignCenter)
        
        self.w = None
        # Modelo crear otro juego
        self.label_tictactoe = QLabel("TicTacToe")
        self.font = QFont("Comic Sans MS", 20)
        self.label_tictactoe.setMaximumHeight(20)
        self.label_tictactoe.setMaximumWidth(500)
        self.label_tictactoe.setFont(self.font)
        self.label_tictactoe.setAlignment(Qt.AlignCenter)
        self.button_tictactoe = QPushButton("")
        self.button_tictactoe.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.button_tictactoe.clicked.connect(self.show_new_window)
        self.button_tictactoe.setStyleSheet('background-image: url("C:/Users/Ernesto/Desktop/tictactoe.jpg");background-color: #21A0A0; border: none; color: white; padding: 10px 20px; border-radius: 5px; font-size: 14px;')
        self.button_tictactoe.setMaximumHeight(500)
        self.button_tictactoe.setMaximumWidth(500)


        # Agregar los widgets al layout principal
        self.layout_principal.addWidget(self.label, 0, 0, 1, 1)
        self.layout_principal.addWidget(self.label_juego, 1, 0, 1, 1)
        self.layout_principal.addWidget(self.button_tictactoe, 2, 0, 1, 1)
        self.layout_principal.addWidget(self.label_tictactoe, 3, 0, 1, 1)

        # Crear el widget principal y asignarle el layout
        widget_principal = QWidget()
        widget_principal.setLayout(self.layout_principal)
        
        # Asignar el widget principal a la ventana principal
        self.setCentralWidget(widget_principal)

        # Agregar una hoja de estilo
        style = """
            QMainWindow {
                background-color: #21;
            }
            
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
            
            QTextEdit {
                font-size: 14px;
            }
            
            QComboBox {
                font-size: 14px;
            }
            
            QPushButton {
                background-color: #21
                padding: 10px 20px;
            border-radius: 5px;
            font-size: 14px;
        }
        
        QPushButton:hover {
            background-color: #1A7C7C;
        }
        
        QTextEdit[readOnly="true"] {
            background-color: #FFFFFF;
            border: none;
            border-radius: 5px;
            color: #555555;
        }
    """


        self.setStyleSheet(style)
        
        # Agregar una imagen de fondo
        self.setStyleSheet('background-image: url("C:/Users/Ernesto/Desktop/fon.jpg"); background-repeat: no-repeat; background-position: center;')

    def show_new_window(self, checked):
        if self.w is None:
            self.w = PlayersWindow()
            self.w.show()
            self.close()

        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.
    


if __name__ =='__main__':
    # Crear la aplicación
    app = QApplication(sys.argv)
    
    # Crear la ventana principal
    ventana_principal = MainWindow()
    ventana_principal.show()
    
    # Ejecutar la aplicación
    sys.exit(app.exec_())
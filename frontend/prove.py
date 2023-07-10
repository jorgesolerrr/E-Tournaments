from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QGridLayout, QLineEdit, QTextEdit, QComboBox, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QFont, QCursor
from PyQt5.QtCore import Qt

import requests
import sys

from random import randint
from middleware.middleware import Middleware

global players

class TournamentWindow(QMainWindow):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self, mdw, players, port_tour, ids, name_tour):
        super().__init__()
        self.mdw = mdw
        self.players = players
        self.port_tour = port_tour
        self.ids = ids
        self.name_tour = name_tour
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
            self.w = PlayersWindow(self.mdw)
            self.w.show()
            self.close()
    
    def show_results(self, checked):
        i=0
        players = [player for player in self.players]
        self.results.setRowCount(len(players))
        self.results.setColumnCount(2)

        stats = requests.get(f'http://127.0.0.1:{self.port_tour}/GetServerData',params= {"replicated": False}).json()
        data=None
        for torn in stats["tournaments"]:
           
            if torn["name"] == self.name_tour:
                data = torn["statistics"]["score"]

        for id in self.ids: #sustituir self por los jugadores
            self.results.setItem(i, 0, QTableWidgetItem(players[id]))#nombre del jugador
            self.results.setItem(i, 1, QTableWidgetItem(str(data[str(id)])))#puntuacion
            i+=1
       
        self.layout_principal.addWidget(self.results, 3, 0)
        


class PlayersWindow(QMainWindow):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self, mdw):
        super().__init__()
        self.mdw = mdw
        self.players = []
        self.port_tour = str
        self.ids = []
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
        self.texto_jugadores.setMaximumWidth(1000)
        self.texto_jugadores.setAlignment(Qt.AlignCenter)

        self.text_torneo = QTextEdit()
        self.text_torneo.setPlaceholderText('Ingrese el nombre del torneo')
        self.text_torneo.setStyleSheet('background-image: url("C:/Users/Ernesto/Desktop/si.jpg")')
        self.text_torneo.setMaximumHeight(100)
        self.text_torneo.setMaximumWidth(100)
        self.text_torneo.setAlignment(Qt.AlignCenter)


        self.button_league = QPushButton("Torneo Liga")
        self.button_league.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.button_league.clicked.connect(self.create_tour_league)
        self.button_league.setStyleSheet('background-image: url("C:/Users/Ernesto/Desktop/trofeo.jpg")')
        self.button_league.setMaximumHeight(180)
        self.button_league.setMaximumWidth(180)

        self.button_playoffs = QPushButton("Torneo Eliminatorias")
        self.button_playoffs.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.button_playoffs.clicked.connect(self.create_tour_playoffs)
        self.button_playoffs.setStyleSheet('background-image: url("C:/Users/Ernesto/Desktop/trofeo.jpg")')
        self.button_playoffs.setMaximumHeight(180)
        self.button_playoffs.setMaximumWidth(180)

        self.button_continue = QPushButton("Continuar")
        self.button_continue.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.button_continue.clicked.connect(self.show_new_window)


        self.button_go_back = QPushButton("Atrás")
        self.button_go_back.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        self.button_go_back.clicked.connect(self.go_back)
        self.button_go_back.setMaximumHeight(40)
        self.button_go_back.setMaximumWidth(50)



         # Agregar los widgets al layout principal
        self.layout_principal.addWidget(self.label, 0, 0, 1, 1)
        self.layout_principal.addWidget(self.label_jugadores, 1, 0, 1, 1)
        self.layout_principal.addWidget(self.texto_jugadores, 2, 0, 1, 4)
        self.layout_principal.addWidget(self.text_torneo , 2, 5, 1, 6)
        self.layout_principal.addWidget(self.button_league, 1, 0, 5, 1)
        self.layout_principal.addWidget(self.button_playoffs, 1, 1, 5, 4)
        self.layout_principal.addWidget(self.button_continue, 5, 7)
        self.layout_principal.addWidget(self.button_go_back, 5, 0)

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
            self.w = TournamentWindow(self.mdw, self.players, self.port_tour, self.ids, self.text_torneo.toPlainText())
            self.w.show()
            self.close()

        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.
    
    def create_tour_playoffs(self, checked):
        self.players = (self.texto_jugadores.toPlainText()).split(',')
        aux = []
        i = 0
        for player in self.players:
            aux.append({'id': i, 'type':"random"})
            self.ids.append(i)
            i += 1
        game_schemma = {"amount_players": 2, "name": "TicTacToe"}
        self.mdw.CreateTournament(self.text_torneo.toPlainText(),"playoffs",game_schemma, aux)
        self.port_tour = self.mdw.executeTournament(self.text_torneo.toPlainText())

    def create_tour_league(self, checked):
        self.players = (self.texto_jugadores.toPlainText()).split(',')
        aux = []
        i = 0
        for player in self.players:
            aux.append({'id': i, 'type':"random"})
            self.ids.append(i)
            i += 1
        game_schemma = {"amount_players": 2, "name": "TicTacToe"}
        self.mdw.CreateTournament(self.text_torneo.toPlainText(),"league",game_schemma, aux)
        self.port_tour = self.mdw.executeTournament(self.text_torneo.toPlainText())

    def go_back(self, checked):
        if self.w is None:
            self.w = MainWindow(self.mdw)
            self.w.show()
            self.close()
        
        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.


class MainWindow(QMainWindow):

    def __init__(self,mdw):
        super().__init__()
        self.mdw = mdw
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
            self.w = PlayersWindow(self.mdw)
            self.w.show()
            self.close()

        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.
    


if __name__ =='__main__':
    # Crear la aplicación
    app = QApplication(sys.argv)
    mdw = Middleware()
    # Crear la ventana principal
    ventana_principal = MainWindow(mdw)
    ventana_principal.show()
    
    # Ejecutar la aplicación
    sys.exit(app.exec_())
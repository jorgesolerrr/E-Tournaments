import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configurar la ventana principal
        self.setWindowTitle('Torneo de Juegos')
        self.setGeometry(100, 100, 800, 600)
        
        # Crear el layout principal
        self.layout_principal = QGridLayout()
        self.layout_principal.setSpacing(10)
        
        # Crear los widgets de la interfaz
        self.label_juego = QLabel('Juego:')
        self.combo_juego = QComboBox()
        self.combo_juego.addItem('Juego 1')
        self.combo_juego.addItem('Juego 2')

        self.label_jugadores = QLabel('Jugadores:')
        self.texto_jugadores = QTextEdit()
        self.texto_jugadores.setPlaceholderText('Ingrese los nombres de los jugadores separados por coma')
        self.texto_jugadores.setMaximumHeight(80)
        
        self.label_tipo_torneo = QLabel('Tipo de torneo:')
        self.combo_tipo_torneo = QComboBox()
        self.combo_tipo_torneo.addItem('Todos contra todos')
        self.combo_tipo_torneo.addItem('Eliminación directa')
        self.combo_tipo_torneo.addItem('Por grupos')
        
        self.boton_crear_torneo = QPushButton('Crear Torneo')
        self.boton_crear_torneo.clicked.connect(self.crear_torneo)
        
        self.label_resultados = QLabel('Resultados:')
        self.texto_resultados = QTextEdit()
        self.texto_resultados.setReadOnly(True)
        self.texto_resultados.setMaximumHeight(150)
        
        # Agregar los widgets al layout principal
        self.layout_principal.addWidget(self.label_juego, 0, 0)
        self.layout_principal.addWidget(self.combo_juego, 0, 1)
        self.layout_principal.addWidget(self.label_jugadores, 1, 0)
        self.layout_principal.addWidget(self.texto_jugadores, 1, 1)
        self.layout_principal.addWidget(self.label_tipo_torneo, 2, 0)
        self.layout_principal.addWidget(self.combo_tipo_torneo, 2, 1)
        self.layout_principal.addWidget(self.boton_crear_torneo, 3, 0, 1, 2)
       
        self.layout_principal.addWidget(self.label_resultados, 4, 0)
        self.layout_principal.addWidget(self.texto_resultados, 5, 0, 1, 2)
        
        # Crear el widget principal y asignarle el layout
        widget_principal = QWidget()
        widget_principal.setLayout(self.layout_principal)
        
        # Asignar el widget principal a la ventana principal
        self.setCentralWidget(widget_principal)
        
        # Agregar una hoja de estilo
        style = """
            QMainWindow {
                background-image: url('C:/Users/Ernesto/Desktop/fond.jpg');
                background-repeat: no-repeat;
                background-position: center center;
            }
            
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
            
            QTextEdit {
                font-size: 14px;
            }
            
            QComboBox {
                font-size: 14px;
            }
            
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            
            QPushButton:hover {
                background-color: #3E8E41;
            }
            
            QTextEdit[readOnly="true"] {
                background-color: #FFFFFF;
                border: none;
                border-radius: 5px;
                color: #555555;
            }
        """
        self.setStyleSheet(style)
    
    def crear_torneo(self):
        # Obtener los datos del formulario
        juego = self.combo_juego.currentText()
        jugadores = self.texto_jugadores.toPlainText().split(',')
        tipo_torneo = self.combo_tipo_torneo.currentText()
        
        # Realizar la lógica del torneo
        
        # Actualizar el widget de resultados
        self.texto_resultados.setText('Resultados del torneo:\n\n')
        for resultado in self.texto_resultados:
            self.texto_resultados.append(resultado)
        
if __name__ =='__main__':
    # Crear la aplicación
    app = QApplication(sys.argv)
    
    # Crear la ventana principal
    ventana_principal = VentanaPrincipal()
    ventana_principal.show()
    
    # Ejecutar la aplicación
    sys.exit(app.exec_())
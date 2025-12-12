import sys
import os
import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox, QListWidgetItem, QDialog

# importacion de pantallas
from login_screen import Ui_LoginScreen
from menu_screen import Ui_MenuScreen
from reporte_screen import Ui_ReporteScreen
from reportes_screen import Ui_ReportesScreen
from buscar_screen import Ui_BuscarScreen

ARCHIVO_DB = "basedatos_reportes.txt"
# separacion simbolo
SEPARADOR = "|||" 

# estilo dark
ESTILO_DARK = """
QMainWindow {
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #000000, stop:1 #2b2b2b);
}

QWidget {
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
    color: #ffffff;
}

/* Campo de texto */
QLineEdit, QTextEdit {
    background-color: #1e1e1e;
    color: #ffffff;           
    border: 1px solid #555555;
    border-radius: 5px;
    padding: 5px;
}

/* blanco brillante al escribir */
QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #ffffff;
}

/* botones principales */
QPushButton {
    background-color: #000000;  
    color: #ffffff;             
    border: 1px solid #ffffff;
    border-radius: 6px;
    padding: 8px 15px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #333333;
    border-color: #aaaaaa;
}

/* Listas */
QListWidget {
    background-color: #121212; 
    border: 1px solid #444;
    border-radius: 8px;
    color: white;
}
QListWidget::item {
    padding: 10px;
    border-bottom: 1px solid #333;
}
QListWidget::item:selected {
    background-color: #ffffff;
    color: #000000;       
}

QLabel {
    color: white;
}
"""

# clase para ventana detalles al dar doble click
class DetalleReporte(QDialog):
    def __init__(self, datos, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detalle del Reporte")
        self.resize(400, 500)
        self.setStyleSheet("QDialog { background-color: #f0f0f0; } QLabel { color: black; }")
        
        layout = QtWidgets.QVBoxLayout(self)

        lbl_titulo = QtWidgets.QLabel(datos['titulo'])
        lbl_titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #000;")
        lbl_titulo.setWordWrap(True)
        layout.addWidget(lbl_titulo)

        # lineas separadoras
        linea = QtWidgets.QFrame()
        linea.setFrameShape(QtWidgets.QFrame.HLine)
        linea.setStyleSheet("color: #ccc;")
        layout.addWidget(linea)

        # datos
        info = f" Fecha: {datos['fecha']}\n Tipo: {datos['tipo']}\n Prioridad: {datos['prioridad']}\n Estado: {datos['estado']}"
        lbl_info = QtWidgets.QLabel(info)
        lbl_info.setStyleSheet("font-size: 14px; color: #333; margin: 10px 0;")
        layout.addWidget(lbl_info)

        # descripcion
        layout.addWidget(QtWidgets.QLabel("Descripcion detallada:"))
        txt_desc = QtWidgets.QTextEdit()
        txt_desc.setPlainText(datos['descripcion'])
        txt_desc.setReadOnly(True)
        txt_desc.setStyleSheet("background: white; color: black; border: 1px solid #ccc;")
        layout.addWidget(txt_desc)
    
        #cerrar
        btn_cerrar = QtWidgets.QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("background-color: #333; color: white; padding: 10px;")
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)

#Conexion de clases de pantalla

class PantallaLogin(QtWidgets.QWidget, Ui_LoginScreen):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        # fondo transparente para el icono
        self.iconLabel.setStyleSheet("background: transparent;")

class PantallaMenu(QtWidgets.QWidget, Ui_MenuScreen):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

class PantallaCrear(QtWidgets.QWidget, Ui_ReporteScreen):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

class PantallaVer(QtWidgets.QWidget, Ui_ReportesScreen):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

class PantallaBuscar(QtWidgets.QWidget, Ui_BuscarScreen):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

#clase controlador principal
class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema Reportes")
        self.resize(450, 780)

            #sistema de pantallas para cambiar de pantalla sin abrir ventanas nuevas
        self.contenedor = QtWidgets.QWidget()
        self.setCentralWidget(self.contenedor)
        self.layout_stack = QtWidgets.QVBoxLayout(self.contenedor)
        self.layout_stack.setContentsMargins(0,0,0,0) # Sin margenes
        
        self.paginas = QtWidgets.QStackedWidget()
        self.layout_stack.addWidget(self.paginas)

        # Inicializar las pantallas
        self.ui_login = PantallaLogin()
        self.ui_menu = PantallaMenu()
        self.ui_crear = PantallaCrear()
        self.ui_ver = PantallaVer()
        self.ui_buscar = PantallaBuscar()

        # Agregarlas al libro de páginas
        self.paginas.addWidget(self.ui_login)
        self.paginas.addWidget(self.ui_menu)  
        self.paginas.addWidget(self.ui_crear)  
        self.paginas.addWidget(self.ui_ver)    
        self.paginas.addWidget(self.ui_buscar)

        # conexiones para hacer que los botones funcionen

        # Pantalla login
        self.ui_login.iniciosesion.clicked.connect(self.validar_usuario)
        self.ui_login.contra.returnPressed.connect(self.validar_usuario)

        # Pantalla menu
        self.ui_menu.nuevo_reporte.clicked.connect(lambda: self.ir_a(2))
        self.ui_menu.reportes.clicked.connect(self.preparar_lista_reportes) # Carga los datos antes de mostrar
        self.ui_menu.buscar.clicked.connect(lambda: self.ir_a(4))
        self.ui_menu.salir.clicked.connect(self.cerrar_sesion)
        # Botones auxiliar
        self.ui_menu.configuracion.clicked.connect(lambda: self.alerta("Info", "Seccion Proximamente."))
        self.ui_menu.ayuda.clicked.connect(lambda: self.alerta("Ayuda", "Soporte Tecnico"))

        # Pantalla crear reporte
        self.ui_crear.envarReporte.clicked.connect(self.guardar_en_txt)
        self.ui_crear.regresar.clicked.connect(lambda: self.ir_a(1))
        # Botones falsos -Proximamente
        self.ui_crear.adjuntarImagen.clicked.connect(lambda: self.alerta("Imagen", "Proximamente."))
        self.ui_crear.usarUbicacion.clicked.connect(lambda: self.alerta("GPS", "Ubicacion agregada: México."))
        self.ui_crear.guardarBorrador.clicked.connect(lambda: self.guardar_en_txt(borrador=True))

        # Pantalla para ver reportes
        self.ui_ver.regresar.clicked.connect(lambda: self.ir_a(1))
        self.ui_ver.refreshButton.clicked.connect(self.cargar_datos_txt) # Boton para actualizar
        self.ui_ver.exportButton.clicked.connect(self.exportar_txt)      # Boton para exportar
        self.ui_ver.listaReportes.itemDoubleClicked.connect(self.ver_detalle) # Double prew

        # Pantalla buscar
        self.ui_buscar.btn_volver.clicked.connect(lambda: self.ir_a(1))
        self.ui_buscar.btn_buscar_ejecutar.clicked.connect(self.ejecutar_busqueda)
        self.ui_buscar.clearButton.clicked.connect(self.limpiar_busqueda)
        self.ui_buscar.resultadosList.itemDoubleClicked.connect(self.ver_detalle)

    # funciones

    def ir_a(self, indice):
        self.paginas.setCurrentIndex(indice)

    def alerta(self, titulo, mensaje):
        """Muestra de notificacion"""
        msg = QMessageBox(self)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setIcon(QMessageBox.Information)
        #estilo de texto negro sobre fondo blanco 
        msg.setStyleSheet("QMessageBox { background-color: white; } QLabel { color: black; } QPushButton { color: white; background-color: black; }")
        msg.exec_()

    def validar_usuario(self):
        user = self.ui_login.txt_usuario.text()
        pwd = self.ui_login.contra.text()
        
        if user == "admin" and pwd == "1234":
            self.ui_login.txt_usuario.clear()
            self.ui_login.contra.clear()
            self.ir_a(1) #Para ir al menu
        else:
            self.alerta("Error de Acceso", "Usuario o contraseña incorrectos.\nIntenta con: admin / 1234")

    def cerrar_sesion(self):
        # Preguntar antes de salir
        msg = QMessageBox(self)
        msg.setWindowTitle("Salir")
        msg.setText("¿Estas seguro de cerrar sesion?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setStyleSheet("QMessageBox { background-color: white; } QLabel { color: black; }")
        
        if msg.exec_() == QMessageBox.Yes:
            self.ir_a(0)

    # Archivos txt

    def guardar_en_txt(self, borrador=False):
        """Toma de datos para txt"""
        # Obtener datos
        titulo = self.ui_crear.titulodelreporte.toPlainText().strip()
        desc = self.ui_crear.descripciondelreporte.toPlainText().strip()
        tipo = self.ui_crear.tipo_reporte.text().strip()
        prio = self.ui_crear.prioridad_reporte.text().strip()

        # Validacion simple
        if not titulo:
            self.alerta("Faltan datos", "Por favor escribe al menos un titulo")
            return

        # Preparar datos para TXT
        desc_segura = desc.replace("\n", "<br>") 
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        estado = "Borrador" if borrador else "Pendiente"

        # Rellenar vacíos
        if not tipo: tipo = "General"
        if not prio: prio = "Media"

        # linea de texto con separadores |||
        linea_final = f"{fecha}{SEPARADOR}{titulo}{SEPARADOR}{desc_segura}{SEPARADOR}{tipo}{SEPARADOR}{prio}{SEPARADOR}{estado}\n"

        # Escribir en el archivo
        try:
            with open(ARCHIVO_DB, "a", encoding="utf-8") as archivo:
                archivo.write(linea_final)
            
            self.alerta("Exito", "Reporte guardado correctamente.")
            
            # limpiar campos
            self.ui_crear.titulodelreporte.clear()
            self.ui_crear.descripciondelreporte.clear()
            self.ui_crear.tipo_reporte.clear()
            self.ui_crear.prioridad_reporte.clear()
            
            self.ir_a(1) # Volver al menú

        except Exception as e:
            self.alerta("Error Crítico", f"No se pudo guardar el archivo:\n{e}")

    def preparar_lista_reportes(self):
        """llamar a la carga de datos"""
        self.cargar_datos_txt()
        self.ir_a(3)

    def cargar_datos_txt(self):
        """leer el txt para llenar"""
        self.ui_ver.listaReportes.clear()
        
        if not os.path.exists(ARCHIVO_DB):
            self.ui_ver.totalLabel.setText("Total: 0")
            return

        total = 0
        pendientes = 0
        completados = 0

        try:
            with open(ARCHIVO_DB, "r", encoding="utf-8") as archivo:
                lineas = archivo.readlines()

            for linea in lineas:
                # Separar la linea
                partes = linea.strip().split(SEPARADOR)
                
                # Vereficacion de 6 lineas para no dar error
                if len(partes) >= 6:
                    fecha, titulo, desc, tipo, prio, estado = partes
                    desc_real = desc.replace("<br>", "\n")

                    # Creamos para guardarlo en un Diccionario
                    datos_item = {
                        "fecha": fecha, "titulo": titulo, "descripcion": desc_real,
                        "tipo": tipo, "prioridad": prio, "estado": estado
                    }
                    texto_visual = f"{titulo} | {tipo} | {estado}"
                    item = QListWidgetItem(texto_visual)
                    item.setData(QtCore.Qt.UserRole, datos_item)
                    self.ui_ver.listaReportes.addItem(item)
                    # Contador
                    total += 1
                    if "Pendiente" in estado:
                        pendientes += 1
                    else:
                        completados += 1
                    
            self.ui_ver.totalLabel.setText(f"Total: {total}")
            self.ui_ver.pendientesLabel.setText(f"Pendientes: {pendientes}")
            self.ui_ver.completadosLabel.setText(f"Hechos: {completados}")
            self.ui_ver.emptyLabel.setVisible(total == 0)

        except Exception as e:
            print(f"Error cargando lista: {e}")

    def ver_detalle(self, item):
        """Ventana preview."""
        datos = item.data(QtCore.Qt.UserRole)
        if datos:
            ventana = DetalleReporte(datos, self)
            ventana.exec_()

    def exportar_txt(self):
        """Creamos copia txt"""
        if not os.path.exists(ARCHIVO_DB):
            self.alerta("Error", "No hay datos para exportar.")
            return
            
        try:
            with open(ARCHIVO_DB, 'r', encoding='utf-8') as origen:
                contenido = origen.read()
            
            # quitando !!!
            contenido_bonito = contenido.replace(SEPARADOR, "  ---  ").replace("<br>", " ")
            
            nombre_export = "reportes_para_imprimir.txt"
            with open(nombre_export, 'w', encoding='utf-8') as destino:
                destino.write("Reporte Oficial\n")
                destino.write("-------------------------\n\n")
                destino.write(contenido_bonito)
            
            self.alerta("Exportado", f"Archivo generado: {nombre_export}")
        except Exception as e:
            self.alerta("Error", str(e))

    # logica para busqueda
    def ejecutar_busqueda(self):
        """buscar texto deltro de los archivos"""
        termino = self.ui_buscar.txt_busqueda.text().lower().strip() # conversion a minusculas
        self.ui_buscar.resultadosList.clear()
        
        if not os.path.exists(ARCHIVO_DB): return

        # filtros activados
        filtro_error = self.ui_buscar.filterError.isChecked()
        filtro_mejora = self.ui_buscar.filterMejora.isChecked()
        filtro_todos = self.ui_buscar.filterAll.isChecked()

        resultados = 0

        with open(ARCHIVO_DB, "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(SEPARADOR)
                if len(partes) >= 6:
                    fecha, titulo, desc, tipo, prio, estado = partes
                    desc_real = desc.replace("<br>", "\n")
                    
                    # Buscamos en titulo o descripción si coincide
                    coincide_texto = (termino in titulo.lower()) or (termino in desc_real.lower())
                    
                    # coincidencia con el tipo de reporte
                    coincide_tipo = True
                    if not filtro_todos:
                        if filtro_error and "Error" not in tipo: coincide_tipo = False
                        elif filtro_mejora and "Mejora" not in tipo: coincide_tipo = False

                    # Si ambas coinciden muestra
                    if coincide_texto and coincide_tipo:
                        datos = {"fecha": fecha, "titulo": titulo, "descripcion": desc_real, 
                                 "tipo": tipo, "prioridad": prio, "estado": estado}
                        
                        item = QListWidgetItem(f"{titulo} ({tipo})")
                        item.setData(QtCore.Qt.UserRole, datos)
                        self.ui_buscar.resultadosList.addItem(item)
                        resultados += 1

        self.ui_buscar.lbl_resultados.setText(f"Se encontraron {resultados} resultados.")
        if resultados == 0:
             self.alerta("Busqueda", "No se encontraron coincidencias.")

    def limpiar_busqueda(self):
        self.ui_buscar.txt_busqueda.clear()
        self.ui_buscar.resultadosList.clear()
        self.ui_buscar.lbl_resultados.setText("Esperando busqueda...")

# arranque para la app
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(ESTILO_DARK)
    ventana = MainApp()
    ventana.show()
    sys.exit(app.exec_())
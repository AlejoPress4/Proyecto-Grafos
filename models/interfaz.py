import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QMessageBox, QScrollArea
from PyQt5.QtCore import Qt
import networkx as nx
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class GraphVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Graph Visualization")
        self.setGeometry(100, 100, 800, 600)

        # Configuración de la interfaz gráfica
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Botones para cargar, organizar y guardar el grafo
        self.load_button = QPushButton("Load Graph")
        self.layout_button = QPushButton("Layout Graph")
        self.save_button = QPushButton("Save Graph")
        layout.addWidget(self.load_button)
        layout.addWidget(self.layout_button)
        layout.addWidget(self.save_button)

        # Crear área de desplazamiento (scroll)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)  # Permitir que el widget se redimensione
        layout.addWidget(self.scroll_area)

        # Área de visualización del grafo
        self.figure = Figure(figsize=(10, 8))  # Aumentar tamaño de la figura para más espacio
        self.canvas = FigureCanvas(self.figure)

        # Configuración del canvas y añadirlo al scroll
        self.scroll_area.setWidget(self.canvas)

        # Conectar los botones a sus funciones
        self.load_button.clicked.connect(self.load_graph)
        self.layout_button.clicked.connect(self.layout_graph)
        self.save_button.clicked.connect(self.save_graph)

        # Almacenar los datos cargados
        self.last_loaded_data = None

        # Variables para el desplazamiento y el zoom
        self.last_mouse_pos = None
        self.zoom_factor = 1.0  # Factor de zoom inicial
        self.offset_x = 0
        self.offset_y = 0

    def load_graph(self):
        """Abrir un archivo JSON para cargar el grafo."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                self.last_loaded_data = data
                self.draw_graph(data)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load graph: {str(e)}")

    def construct_graph(self, json_data):
        """Construir un grafo de NetworkX a partir de datos JSON."""
        G = nx.Graph()

        # Agregar nodos al grafo
        for node in json_data:
            G.add_node(node['name'], type=node['type'])

            # Agregar elementos (tanques) dentro de cada barrio
            if 'elements' in node:
                for element in node['elements']:
                    G.add_node(element['name'], type=element['type'])
                    for connection in element['connections']:
                        if connection.startswith('+'):
                            G.add_edge(element['name'], connection[1:], direction='right')
                        elif connection.startswith('-'):
                            G.add_edge(connection[1:], element['name'], direction='left')
                        else:
                            G.add_edge(element['name'], connection, direction='both')

        # Agregar conexiones entre barrios
        for node in json_data:
            for connection in node['connections']:
                if connection.startswith('+'):
                    G.add_edge(node['name'], connection[1:], direction='right')
                elif connection.startswith('-'):
                    G.add_edge(connection[1:], node['name'], direction='left')
                else:
                    G.add_edge(node['name'], connection, direction='both')

        return G

    def draw_graph(self, data):
        """Visualizar el grafo en el área de la figura."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        try:
            # Construir y dibujar el grafo
            graph = self.construct_graph(data)
            pos = nx.spring_layout(graph, k=0.5)  # Ajustar el parámetro k para espaciar más los nodos

            # Colorear las aristas según la dirección
            edge_colors = [
                'blue' if graph.edges[edge].get('direction') == 'right'
                else 'red' if graph.edges[edge].get('direction') == 'left'
                else 'black'
                for edge in graph.edges
            ]

            # Dibujar el grafo con colores
            nx.draw(graph, pos, with_labels=True, ax=ax, node_color='lightblue', edge_color=edge_colors, width=2)
            self.canvas.draw()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error drawing the graph: {str(e)}")

    def layout_graph(self):
        """Reorganizar el grafo y actualizar la visualización."""
        QMessageBox.information(self, "Info", "Reorganizing graph layout...")

        try:
            # Reorganizar el grafo con un mayor valor de k para más separación
            self.draw_graph(self.last_loaded_data)
        except AttributeError:
            QMessageBox.warning(self, "Warning", "No graph loaded to rearrange.")

    def save_graph(self):
        """Guardar la visualización actual del grafo como imagen."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Graph", "", "PNG Files (*.png)")
        if file_path:
            try:
                self.figure.savefig(file_path, format='png')
                QMessageBox.information(self, "Success", "Graph saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save graph: {str(e)}")

    def wheelEvent(self, event):
        """Implementar zoom al hacer scroll con el mouse."""
        scale_factor = 1.1
        if event.angleDelta().y() > 0:  # Zoom in
            self.zoom_factor *= scale_factor
        else:  # Zoom out
            self.zoom_factor /= scale_factor

        # Ajustar la visualización para que se mantenga centrada y escalada correctamente
        self.draw_graph(self.last_loaded_data)
        self.canvas.draw()

    def mousePressEvent(self, event):
        """Detectar el clic del ratón para comenzar el desplazamiento."""
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        """Desplazar el grafo cuando se mueve el ratón mientras se mantiene presionado el botón izquierdo."""
        if self.last_mouse_pos:
            dx = event.pos().x() - self.last_mouse_pos.x()
            dy = event.pos().y() - self.last_mouse_pos.y()

            # Actualizamos las barras de desplazamiento
            self.scroll_area.horizontalScrollBar().setValue(self.scroll_area.horizontalScrollBar().value() - dx)
            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().value() - dy)

            # Movemos el gráfico
            self.offset_x += dx
            self.offset_y += dy

            self.last_mouse_pos = event.pos()

    def mouseReleaseEvent(self, event):
        """Restablecer el estado de desplazamiento al soltar el botón del ratón."""
        self.last_mouse_pos = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    visualizer = GraphVisualizer()
    visualizer.show()
    sys.exit(app.exec_())

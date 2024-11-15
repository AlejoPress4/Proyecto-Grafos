import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QMessageBox
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

        # Área de visualización del grafo
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Conectar los botones a sus funciones
        self.load_button.clicked.connect(self.load_graph)
        self.layout_button.clicked.connect(self.layout_graph)
        self.save_button.clicked.connect(self.save_graph)

    def load_graph(self):
        """Abrir un archivo JSON para cargar el grafo."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                self.draw_graph(data)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load graph: {str(e)}")

    def construct_graph(self, json_data):
        """Construir un grafo de NetworkX a partir de datos JSON."""
        G = nx.Graph()

        # Agregar nodos al grafo
        for node in json_data:
            G.add_node(node['name'], type=node['type'])

        # Agregar aristas al grafo
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
            pos = nx.spring_layout(graph)

            # Colorear las aristas según la dirección
            edge_colors = [
                'blue' if graph.edges[edge].get('direction') == 'right'
                else 'red' if graph.edges[edge].get('direction') == 'left'
                else 'black'
                for edge in graph.edges
            ]

            nx.draw(graph, pos, with_labels=True, ax=ax, node_color='lightblue', edge_color=edge_colors)
            self.canvas.draw()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error drawing the graph: {str(e)}")

    def layout_graph(self):
        """Implementar la lógica para organizar automáticamente el grafo."""
        QMessageBox.information(self, "Info", "Graph layout functionality is not yet implemented.")

    def save_graph(self):
        """Guardar la visualización actual del grafo como imagen."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Graph", "", "PNG Files (*.png)")
        if file_path:
            try:
                self.figure.savefig(file_path, format='png')
                QMessageBox.information(self, "Success", "Graph saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save graph: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    visualizer = GraphVisualizer()
    visualizer.show()
    sys.exit(app.exec_())

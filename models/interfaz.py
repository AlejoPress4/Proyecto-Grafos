import sys
import json
import matplotlib.pyplot as plt
import networkx as nx
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QMessageBox, QTabWidget, QLineEdit, QInputDialog
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class WaterSystemGraphVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Tuberiaaaas")
        self.setGeometry(100, 100, 1000, 700)

        # Central widget with tab system
        self.central_widget = QWidget()
        self.tab_widget = QTabWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)

        # Graph visualization tab
        self.graph_tab = QWidget()
        graph_layout = QVBoxLayout()

        # Button for loading graph
        self.load_button = QPushButton("Cargar grafo")
        self.load_button.clicked.connect(self.load_graph)
        graph_layout.addWidget(self.load_button)

        # Button for adding a neighborhood
        self.add_neighborhood_button = QPushButton("Agregar Barrio")
        self.add_neighborhood_button.clicked.connect(self.add_neighborhood)
        graph_layout.addWidget(self.add_neighborhood_button)

        # Graph canvas
        self.graph_figure = Figure(figsize=(10, 8))
        self.graph_canvas = FigureCanvas(self.graph_figure)
        graph_layout.addWidget(self.graph_canvas)

        self.graph_tab.setLayout(graph_layout)
        self.tab_widget.addTab(self.graph_tab, "Vista del grafo")

        self.capacity_tab = QWidget()
        capacity_layout = QVBoxLayout()
        self.capacity_figure = Figure(figsize=(10, 8))
        self.capacity_canvas = FigureCanvas(self.capacity_figure)
        capacity_layout.addWidget(self.capacity_canvas)
        self.capacity_tab.setLayout(capacity_layout)

        self.last_loaded_data = None
        self.neighborhoods_data = []  # List to store the neighborhoods

    def load_graph(self):
        """Open a JSON file to load graph data with tanks and houses."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                self.last_loaded_data = data
                self.draw_graph(data)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load graph: {str(e)}")

    def draw_graph(self, data):
        """Visualize the graph structure with tanks and houses."""
        self.graph_figure.clear()
        ax = self.graph_figure.add_subplot(111)

        try:
            # Construct graph
            graph = self.construct_graph(data)
            pos = self.assign_positions(data, graph)

            # Differentiate tanks and houses
            tank_nodes = [n for n, attr in graph.nodes(data=True) if attr['type'] == 'tank']
            house_nodes = [n for n, attr in graph.nodes(data=True) if attr['type'] == 'house']

            # Color edges by direction
            edge_colors = [
                'blue' if graph.edges[edge].get('direction') == 'right'
                else 'red' if graph.edges[edge].get('direction') == 'left'
                else 'black'
                for edge in graph.edges
            ]

            # Create custom labels for nodes (tank and house labels)
            node_labels = {}
            for node in tank_nodes:
                # Get the corresponding node's information
                node_data = [element for neighborhood in data for element in neighborhood['elements'] if element['name'] == node]
                if node_data:
                    node_data = node_data[0]  # Get the first match
                    label = f"{node_data['name']}\nCap: {node_data['current_capacity']}L\nIn: {node_data['input_rate']}L/s\nOut: {node_data['output_rate']}L/s"
                    node_labels[node] = label

            for node in house_nodes:
                # Get the corresponding node's information for houses
                node_data = [element for neighborhood in data for element in neighborhood['elements'] if element['name'] == node]
                if node_data:
                    node_data = node_data[0]  # Get the first match
                    label = f"{node_data['name']}\nConexiones: {len(node_data.get('connections', []))}"
                    node_labels[node] = label

            # Draw graph with custom node labels
            nx.draw(graph, pos, with_labels=True, ax=ax,
                    node_color=['lightblue' if n in tank_nodes else 'lightgreen' for n in graph.nodes()],
                    edge_color=edge_colors,
                    width=1,
                    node_size=2000,
                    font_size=10,
                    arrows=False,
                    alpha=0.7,
                    labels=node_labels)  # Add custom labels to the nodes

            self.graph_canvas.draw()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error drawing the graph: {str(e)}")

    def construct_graph(self, json_data):
        """Build a NetworkX graph from JSON data."""
        G = nx.DiGraph()

        # Add nodes and edges
        for neighborhood in json_data:
            for element in neighborhood['elements']:
                G.add_node(element['name'], type=element['type'])
                for connection in element.get('connections', []):
                    if connection.startswith('+'):
                        G.add_edge(element['name'], connection[1:], direction='right')
                    elif connection.startswith('-'):
                        G.add_edge(connection[1:], element['name'], direction='left')
                    else:
                        G.add_edge(element['name'], connection, direction='both')

        return G

    def assign_positions(self, data, graph):
        """Assign positions to nodes to separate subgraphs visually."""
        positions = {}
        offset_x = 0  # Horizontal offset between subgraphs
        offset_y = 0  # Vertical offset

        for neighborhood in data:
            # Determine nodes in this subgraph
            subgraph_nodes = [element['name'] for element in neighborhood['elements']]

            # Create a layout for the subgraph
            subgraph = graph.subgraph(subgraph_nodes)
            subgraph_positions = nx.spring_layout(subgraph, k=5)

            # Offset the positions for separation
            for node, pos in subgraph_positions.items():
                positions[node] = (pos[0] + offset_x, pos[1] + offset_y)

            # Adjust offsets for the next subgraph
            offset_x += 3  # Increase horizontal spacing to separate subgraphs
            offset_y -= 3  # Adjust vertical position slightly for better separation

        return positions

    def add_neighborhood(self):
        """Add a new neighborhood with tanks and houses."""
        name, ok = QInputDialog.getText(self, 'Neighborhood Name', 'Enter the name of the new neighborhood:')
        if ok:
            new_neighborhood = {'name': name, 'elements': []}
            self.add_tank_to_neighborhood(new_neighborhood)
            self.add_house_to_neighborhood(new_neighborhood)

            self.neighborhoods_data.append(new_neighborhood)
            self.draw_graph(self.neighborhoods_data)  # Redraw the graph with the new neighborhood

    def add_tank_to_neighborhood(self, neighborhood):
        """Add a new tank to a given neighborhood."""
        tank_name, ok = QInputDialog.getText(self, 'Tank Name', 'Enter the tank name:')
        if ok:
            capacity, ok = QInputDialog.getInt(self, 'Tank Capacity', 'Enter the tank capacity (L):')
            if ok:
                input_rate, ok = QInputDialog.getInt(self, 'Input Rate', 'Enter the input rate (L/s):')
                if ok:
                    output_rate, ok = QInputDialog.getInt(self, 'Output Rate', 'Enter the output rate (L/s):')
                    if ok:
                        tank_data = {
                            'name': tank_name,
                            'type': 'tank',
                            'current_capacity': capacity,
                            'input_rate': input_rate,
                            'output_rate': output_rate,
                            'connections': []
                        }
                        neighborhood['elements'].append(tank_data)

    def add_house_to_neighborhood(self, neighborhood):
        """Add a new house to a given neighborhood."""
        house_name, ok = QInputDialog.getText(self, 'House Name', 'Enter the house name:')
        if ok:
            house_data = {
                'name': house_name,
                'type': 'house',
                'connections': []
            }
            neighborhood['elements'].append(house_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    visualizer = WaterSystemGraphVisualizer()
    visualizer.show()
    sys.exit(app.exec_())

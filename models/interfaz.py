import sys
import json
import matplotlib.pyplot as plt
import networkx as nx
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, 
                             QFileDialog, QMessageBox, QTabWidget, QLineEdit, QInputDialog, 
                             QDialog, QFormLayout, QSpinBox, QDialogButtonBox, QButtonGroup, QHBoxLayout, QRadioButton, QCheckBox)
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

        # Button for removing a neighborhood
        self.remove_neighborhood_button = QPushButton("Eliminar Barrio")
        self.remove_neighborhood_button.clicked.connect(self.remove_neighborhood)
        graph_layout.addWidget(self.remove_neighborhood_button)

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
                self.neighborhoods_data = data  # Update neighborhoods_data with loaded data
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
                    label = f"{node_data['name']}\nCap: {node_data.get('current_capacity', 'N/A')}L\nIn: {node_data.get('input_rate', 'N/A')}L/s\nOut: {node_data.get('output_rate', 'N/A')}L/s"
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
        """Add a new neighborhood with specified tanks, houses, and their connections."""
        # Prompt for neighborhood name
        name, ok = QInputDialog.getText(self, 'Nombre del barrio', 'Ingrese el nombre del nuevo barrio:')
        if not ok:
            return

        # Create custom dialog for specifying tanks and houses
        dialog = QDialog(self)
        dialog.setWindowTitle(f'Configure {name}')
        
        layout = QFormLayout(dialog)
        
        tank_spin = QSpinBox(dialog)
        tank_spin.setRange(1, 10)  # Limit to 10 tanks
        tank_spin.setValue(1)
        layout.addRow("Numero de tanques:", tank_spin)
        
        house_spin = QSpinBox(dialog)
        house_spin.setRange(1, 10)  # Limit to 10 houses
        house_spin.setValue(1)
        layout.addRow("Numero de casas:", house_spin)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, 
            Qt.Horizontal, dialog
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        # Show the dialog
        if dialog.exec_() == QDialog.Accepted:
            num_tanks = tank_spin.value()
            num_houses = house_spin.value()
            
            # Create new neighborhood dictionary
            new_neighborhood = {'name': name, 'elements': []}
            
            # Add tanks
            tanks = []
            for i in range(num_tanks):
                tank_data = self.create_tank_dialog(f"Tanque {i+1}")
                if tank_data:
                    tanks.append(tank_data)
                    new_neighborhood['elements'].append(tank_data)
            
            # Add houses
            houses = []
            for i in range(num_houses):
                house_data = self.create_house_dialog(f"Casa {i+1}")
                if house_data:
                    houses.append(house_data)
                    new_neighborhood['elements'].append(house_data)
            
            # Connection specification dialog
            if tanks or houses:
                self.specify_connections(tanks, houses, new_neighborhood)
            
            # Only add if some elements were created
            if new_neighborhood['elements']:
                self.neighborhoods_data.append(new_neighborhood)
                self.draw_graph(self.neighborhoods_data)

    def specify_connections(self, tanks, houses, neighborhood):
        """Dialog to specify connections between tanks and houses."""
        if not tanks and not houses:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Conexiones")
        layout = QVBoxLayout(dialog)

        # Create connection inputs
        connection_inputs = []
        for source in (tanks + houses):
            for target in (tanks + houses):
                if source != target:
                    # Create a checkbox for each possible connection
                    connection_cb = QCheckBox(f"Conectar {source['name']} con {target['name']}")
                    
                    # Add direction radio buttons
                    direction_group = QButtonGroup(dialog)
                    right_radio = QRadioButton("Derecha (->)")
                    left_radio = QRadioButton("Izquierda (<-)")
                    both_radio = QRadioButton("Ambas")
                    direction_group.addButton(right_radio)
                    direction_group.addButton(left_radio)
                    direction_group.addButton(both_radio)
                    both_radio.setChecked(True)  # Default to bidirectional

                    connection_cb.stateChanged.connect(
                        lambda state, cb=connection_cb, right=right_radio, left=left_radio, both=both_radio: 
                        self.toggle_direction_radios(state, right, left, both)
                    )

                    # Layout for this connection
                    conn_layout = QHBoxLayout()
                    conn_layout.addWidget(connection_cb)
                    conn_layout.addWidget(right_radio)
                    conn_layout.addWidget(left_radio)
                    conn_layout.addWidget(both_radio)

                    layout.addLayout(conn_layout)
                    connection_inputs.append({
                        'source': source,
                        'target': target,
                        'checkbox': connection_cb,
                        'right_radio': right_radio,
                        'left_radio': left_radio,
                        'both_radio': both_radio
                    })

        # Add OK and Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, 
            Qt.Horizontal, dialog
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        # Show the dialog
        if dialog.exec_() == QDialog.Accepted:
            for conn in connection_inputs:
                if conn['checkbox'].isChecked():
                    # Determine connection direction
                    if conn['right_radio'].isChecked():
                        connection = f"+{conn['target']['name']}"
                    elif conn['left_radio'].isChecked():
                        connection = f"-{conn['target']['name']}"
                    else:  # Both
                        connection = conn['target']['name']
                    
                    # Add connection to source
                    for element in neighborhood['elements']:
                        if element['name'] == conn['source']['name']:
                            if connection not in element.get('connections', []):
                                element.setdefault('connections', []).append(connection)

    def toggle_direction_radios(self, state, right_radio, left_radio, both_radio):
        """Enable/disable direction radios based on connection checkbox."""
        right_radio.setEnabled(state == Qt.Checked)
        left_radio.setEnabled(state == Qt.Checked)
        both_radio.setEnabled(state == Qt.Checked)
        
        # If unchecked, reset to both
        if state != Qt.Checked:
            both_radio.setChecked(True)

    def create_tank_dialog(self, default_name):
            """Create a dialog to input tank details."""
            dialog = QDialog(self)
            dialog.setWindowTitle('Detalles del Tanque')
            layout = QFormLayout(dialog)
            
            # Name input
            name_input = QLineEdit(default_name)
            layout.addRow("Nombre del tanque:", name_input)
            
            # Capacity input
            capacity_spin = QSpinBox()
            capacity_spin.setRange(100, 10000)
            capacity_spin.setValue(1000)
            capacity_spin.setSuffix(" L")
            layout.addRow("Capacidad Maxima (L):", capacity_spin)
            
            # Current capacity input
            current_capacity_spin = QSpinBox()
            current_capacity_spin.setRange(0, capacity_spin.value())
            current_capacity_spin.setValue(capacity_spin.value() // 2)
            current_capacity_spin.setSuffix(" L")
            layout.addRow("Capacidad Actual (L):", current_capacity_spin)
            
            # Input rate input
            input_rate_spin = QSpinBox()
            input_rate_spin.setRange(1, 100)
            input_rate_spin.setValue(50)
            input_rate_spin.setSuffix(" L/s")
            layout.addRow("Entrada (L/s):", input_rate_spin)
            
            # Output rate input
            output_rate_spin = QSpinBox()
            output_rate_spin.setRange(1, 100)
            output_rate_spin.setValue(40)
            output_rate_spin.setSuffix(" L/s")
            layout.addRow("Salida (L/s):", output_rate_spin)
            
            buttons = QDialogButtonBox(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel, 
                Qt.Horizontal, dialog
            )
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)
            
            if dialog.exec_() == QDialog.Accepted:
                return {
                    'name': name_input.text(),
                    'type': 'tank',
                    'max_capacity': capacity_spin.value(),
                    'current_capacity': current_capacity_spin.value(),
                    'input_rate': input_rate_spin.value(),
                    'output_rate': output_rate_spin.value(),
                    'connections': []
                }
            return None

    def create_house_dialog(self, default_name):
        """Create a dialog to input house details."""
        dialog = QDialog(self)
        dialog.setWindowTitle('Detalles Casa')
        layout = QFormLayout(dialog)
        
        # Name input
        name_input = QLineEdit(default_name)
        layout.addRow("Nombre de la casa:", name_input)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, 
            Qt.Horizontal, dialog
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            return {
                'name': name_input.text(),
                'type': 'house',
                'connections': []
            }
        return None

    def remove_neighborhood(self):
        """Remove a neighborhood from the list."""
        if not self.neighborhoods_data:
            QMessageBox.warning(self, "Error", "No neighborhoods to remove.")
            return
        
        # Create a dialog to select neighborhood to remove
        neighborhood_names = [neighborhood['name'] for neighborhood in self.neighborhoods_data]
        name, ok = QInputDialog.getItem(
            self, 
            "Eliminar barrio", 
            "Selecione el barrio:", 
            neighborhood_names, 
            0, 
            False
        )
        
        if ok:
            # Find and remove the selected neighborhood
            self.neighborhoods_data = [
                neighborhood for neighborhood in self.neighborhoods_data 
                if neighborhood['name'] != name
            ]
            
            # Redraw the graph if neighborhoods remain
            if self.neighborhoods_data:
                self.draw_graph(self.neighborhoods_data)
            else:
                # Clear the graph if no neighborhoods left
                self.graph_figure.clear()
                self.graph_canvas.draw()
            
            QMessageBox.information(self, "Success", f"Barrio '{name}' eliminado correctamente.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    visualizer = WaterSystemGraphVisualizer()
    visualizer.show()
    sys.exit(app.exec_())
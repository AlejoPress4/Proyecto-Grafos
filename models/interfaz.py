import sys
import networkx as nx
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import random
import json

from models.funtions import load_graph_from_json, calculate_max_flow, assign_graph_positions, _agregar_conexion

class WaterSystemGraphVisualizer(QMainWindow):
    file=""
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Sistema de Tuberías")
        self.setGeometry(100, 100, 1200, 800)

        # Widget central y layout principal
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        # Botón de carga de grafo
        load_button = QPushButton("Cargar Grafo")
        load_button.clicked.connect(self.load_graph)
        main_layout.addWidget(load_button)
        
        #Boton para agregar barrio
        add_button = QPushButton("Agregar Barrio")
        add_button.clicked.connect(self.agregar_barrio)
        main_layout.addWidget(add_button)
        
        #Boton para eliminar barrio
        delete_button = QPushButton("Eliminar Barrio")
        delete_button.clicked.connect(self.eliminar_barrio)
        main_layout.addWidget(delete_button)
        
        #Boton para agregar conexion
        add_connection_button = QPushButton("Agregar Conexión")
        add_connection_button.clicked.connect(self.agregar_conexion)
        main_layout.addWidget(add_connection_button)

        # Figura de matplotlib para visualización
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

        # Botón de flujo máximo
        max_flow_button = QPushButton("Calcular Flujo Máximo")
        max_flow_button.clicked.connect(self.show_max_flow)
        main_layout.addWidget(max_flow_button)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.graph = None
        self.original_data = None

    def load_graph(self):
        """Cargar grafo desde un archivo JSON"""
        self.file, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo JSON", "", "JSON Files (*.json)")
        
        if self.file:
            try:
                # Cargar grafo desde JSON
                self.graph, self.original_data = load_graph_from_json(self.file)
                
                # Visualizar grafo
                self.visualize_graph()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo cargar el grafo: {str(e)}")
                



    def agregar_barrio(self):
        """Agregar un nuevo barrio con tanques, casas y conexiones."""
        # Pedir nombre del barrio
        barrio_name, ok = QInputDialog.getText(self, "Nuevo Barrio", "Nombre del nuevo barrio:")
        if not ok or not barrio_name:
            return

        # Crear estructura básica del barrio
        nuevo_barrio = {
            "name": barrio_name,
            "elements": []
        }

        # Lista para almacenar los tanques y las casas temporalmente
        tanques = []
        casas = []

        # Agregar múltiples tanques
        while True:
            tanque_name, ok = QInputDialog.getText(self, "Nuevo Tanque", "Nombre del tanque (deja vacío para terminar):")
            if not ok or not tanque_name:
                break
            
            max_capacity, ok = QInputDialog.getInt(self, "Max Capacity", f"Capacidad máxima de {tanque_name}:")
            if not ok:
                break

            current_capacity, ok = QInputDialog.getInt(self, "Current Capacity", f"Capacidad actual de {tanque_name}:")
            if not ok:
                break


            # Agregar el tanque a la lista temporal
            tanques.append({
                "name": tanque_name,
                "type": "tank",
                "max_capacity": max_capacity,
                "current_capacity": current_capacity,
                "connections": []  # Las conexiones se agregarán después
            })

        # Agregar los tanques al barrio
        nuevo_barrio["elements"].extend(tanques)

        # Agregar múltiples casas
        while True:
            casa_name, ok = QInputDialog.getText(self, "Nueva Casa", "Nombre de la casa (deja vacío para terminar):")
            if not ok or not casa_name:
                break

            # Agregar la casa al barrio
            casas.append({
                "name": casa_name,
                "type": "house",
                "connections": []  # Las conexiones se agregarán después
            })

        # Agregar las casas al barrio
        nuevo_barrio["elements"].extend(casas)

        # Agregar las conexiones y sus capacidades
        while True:
            # Seleccionar un tanque
            tanque_name, ok = QInputDialog.getItem(self, "Seleccionar Tanque", "Selecciona un tanque para agregar conexiones:", 
                                                [tanque['name'] for tanque in tanques], 0, False)
            if not ok or not tanque_name:
                break

            # Seleccionar una casa para conectar
            casa_name, ok = QInputDialog.getItem(self, "Seleccionar Casa", f"Selecciona una casa para conectar a {tanque_name}:",
                                                [casa['name'] for casa in casas], 0, False)
            if not ok or not casa_name:
                break

            # Pedir la capacidad de la conexión
            capacity, ok = QInputDialog.getInt(self, "Capacidad de Conexión", f"Capacidad de la conexión de {tanque_name} a {casa_name}:")
            if not ok:
                break
            
            # Pedir la dirección de la conexión
            direction, ok = QInputDialog.getItem(self, "Dirección de Conexión", f"Selecciona la dirección de la conexión entre {tanque_name} y {casa_name}:",
                                                ["right", "left", "both"], 0, False)
            if not ok or not direction:
                break

            # Agregar la conexión al tanque
            for tanque in tanques:
                if tanque['name'] == tanque_name:
                    tanque['connections'].append({
                        "target": f"+{casa_name}" if direction == "right" else f"-{casa_name}" if direction == "left" else f"{casa_name}",
                        "capacity": capacity
                    })

            # Agregar la conexión a la casa
            for casa in casas:
                if casa['name'] == casa_name:
                    casa['connections'].append({
                        "target": f"-{tanque_name}" if direction == "right" else f"+{tanque_name}" if direction == "left" else f"{tanque_name}",
                        "capacity": capacity
                    })

            # Preguntar si el usuario quiere agregar más conexiones
            add_more, ok = QInputDialog.getItem(self, "Agregar Más Conexiones", "¿Quieres agregar más conexiones?", ["Sí", "No"], 0, False)
            if not ok or add_more == "No":
                break

        # Actualizar el grafo con el nuevo barrio (sin guardar el JSON)
    
        self.original_data.append(nuevo_barrio)
        self.save_json(self.original_data)
        self.update_graph()  # Redibujar el grafo

    def eliminar_barrio(self):
        """Eliminar un barrio existente del grafo y del JSON."""
        try:
            # Obtener los nombres de los barrios actuales
            barrio_names = [barrio['name'] for barrio in self.original_data]

            if not barrio_names:
                QMessageBox.warning(self, "No hay barrios", "No hay barrios disponibles para eliminar.")
                return

            # Mostrar un cuadro de diálogo para seleccionar un barrio
            barrio_name, ok = QInputDialog.getItem(self, "Seleccionar Barrio", "Selecciona un barrio para eliminar:",
                                                    barrio_names, 0, False)

            if not ok or not barrio_name:
                return

            # Buscar el barrio en self.original_data
            barrio_a_eliminar = None
            for barrio in self.original_data:
                if barrio['name'] == barrio_name:
                    barrio_a_eliminar = barrio
                    break

            if not barrio_a_eliminar:
                QMessageBox.warning(self, "Barrio no encontrado", "No se encontró el barrio seleccionado.")
                return

            # Eliminar los nodos y aristas correspondientes al barrio en el grafo
            for element in barrio_a_eliminar["elements"]:
                # Eliminar las conexiones en las aristas del grafo
                for connection in element["connections"]:
                    target_node = connection['target']
                    if target_node.startswith('+'):
                        target_node = target_node[1:]  # Eliminar el prefijo '+'
                    elif target_node.startswith('-'):
                        target_node = target_node[1:]  # Eliminar el prefijo '-'
                    
                    if self.graph.has_edge(element['name'], target_node):
                        self.graph.remove_edge(element['name'], target_node)
                    elif self.graph.has_edge(target_node, element['name']):
                        self.graph.remove_edge(target_node, element['name'])

            # Eliminar los nodos del barrio del grafo
            for element in barrio_a_eliminar["elements"]:
                self.graph.remove_node(element['name'])

            # Eliminar el barrio de la estructura de datos
            self.original_data.remove(barrio_a_eliminar)

            # Actualizar la visualización del grafo
            self.visualize_graph()

            # Guardar los cambios en el archivo JSON actualizado
            self.save_json(self.original_data)  # Pasar 'self.original_data' correctamente

            # Confirmación de eliminación
            QMessageBox.information(self, "Barrio Eliminado", f"El barrio '{barrio_name}' ha sido eliminado exitosamente.")

        except Exception as e:
            # En caso de error, mostrar mensaje y evitar que la aplicación se cierre
            QMessageBox.critical(self, "Error", f"Ocurrió un error al eliminar el barrio: {str(e)}")



    def save_json(self, data):
        """Guardar los cambios en el archivo JSON."""
        try:
            
            #file_path, _ = QFileDialog.getSaveFileName(self, "Guardar Archivo", "", "JSON Files (*.json)")
            if self.file:
                with open(self.file, 'w') as f:
                    json.dump(data, f, indent=4)  # Usar 'data' que pasamos desde 'eliminar_barrio'
                QMessageBox.information(self, "Archivo Guardado", "El archivo JSON se ha guardado exitosamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar el archivo JSON: {str(e)}")
            
    def visualize_graph(self):
        """Visualizar el grafo de tuberías"""
        if self.graph is None:
            return

        # Limpiar figura anterior
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Obtener posiciones de los nodos
        pos = assign_graph_positions(self.graph, self.original_data)


        # Separar tipos de nodos
        tanks = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'tank']
        houses = [n for n, d in self.graph.nodes(data=True) if d.get('type') == 'house']

        # Dibujar nodos
        nx.draw_networkx_nodes(self.graph, pos, nodelist=tanks, node_color='lightblue', node_size=700, ax=ax)
        nx.draw_networkx_nodes(self.graph, pos, nodelist=houses, node_color='lightgreen', node_size=700, ax=ax)

        # Dibujar aristas con dirección correcta y estilos
        for (u, v, data) in self.graph.edges(data=True):
            direction = data.get('direction', 'both')

            # Definir estilo de flecha
            if direction == 'right':
                arrowstyle = '->'
            elif direction == 'left':
                arrowstyle = '<-'
            else:
                arrowstyle = '<->'

            # Dibujar arista con estilo de flecha correcto
            nx.draw_networkx_edges(
                self.graph,
                pos,
                edgelist=[(u, v)],
                edge_color='gray',
                connectionstyle='arc3,rad=0.1',  # Añadir curvatura para mayor claridad
                arrows=True,
                arrowsize=20,
                ax=ax
            )

        # Etiquetas de las capacidades de las aristas
        edge_labels = {
            (u, v): f"{data.get('capacidad', 0)} L/s" for u, v, data in self.graph.edges(data=True)
        }
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_size=10, ax=ax)

        # Etiquetas de los nodos
        labels = {
            node: (f"{node}\nCap: {data.get('current_capacity', 0)}/{data.get('max_capacity', 0)}L" 
                if data.get('type') == 'tank' else node)
            for node, data in self.graph.nodes(data=True)
        }
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8, ax=ax)

        # Configuración final del gráfico
        ax.set_title("Sistema de Tuberías")
        ax.axis('off')

        # Dibujar canvas
        self.canvas.draw()



    def show_max_flow(self):
        """Calcular y mostrar flujo máximo"""
        if self.graph is None:
            QMessageBox.warning(self, "Error", "Primero cargue un grafo")
            return

        # Calcular flujo máximo
        max_flow, flow_dict = calculate_max_flow(self.graph)

        # Mostrar resultado
        QMessageBox.information(self, "Flujo Máximo", f"Flujo máximo: {max_flow} L/s")
        
        
        
        
    def update_graph(self):
        """Rebuild the graph from self.original_data with correct edge handling"""
        # Clear the existing graph
        self.graph = nx.DiGraph()
        
        # Rebuild the graph from original data
        for barrio in self.original_data:
            for element in barrio["elements"]:
                # Add node with attributes
                self.graph.add_node(
                    element["name"], 
                    type=element.get("type", ""), 
                    max_capacity=element.get("max_capacity", 0), 
                    current_capacity=element.get("current_capacity", 0)
                )
                
                # Process connections
                for conn in element.get("connections", []):
                    target = conn["target"]
                    capacity = conn.get("capacity", 0)
                    
                    # Handle different connection types
                    if target.startswith('+'):
                        dest = target[1:]
                        self.graph.add_edge(element["name"], dest, capacidad=capacity, direction='right')
                    elif target.startswith('-'):
                        dest = target[1:]
                        self.graph.add_edge(dest, element["name"], capacidad=capacity, direction='left')
                    else:
                        # Bidirectional or default connection
                        self.graph.add_edge(element["name"], target, capacidad=capacity, direction='both')
                        self.graph.add_edge(target, element["name"], capacidad=capacity, direction='both')
        
        # Visualize the updated graph
        self.visualize_graph()

def main():
    app = QApplication(sys.argv)
    main_window = WaterSystemGraphVisualizer()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
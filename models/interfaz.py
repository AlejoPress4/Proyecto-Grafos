import sys
import networkx as nx
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import random
import json
import os
import matplotlib.image as mpimg
from datetime import datetime

from models.funtions import load_graph_from_json,  assign_graph_positions, agregar_conexion

class WaterSystemGraphVisualizer(QMainWindow):
    file=""
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Sistema de Tuberías")
        self.setWindowIcon(QIcon("icons\\tuberias.png"))
        self.setGeometry(100, 100, 1600, 800)  # Increased width to accommodate log

        # Widget central y layout principal
        central_widget = QWidget()
        main_layout = QHBoxLayout()  # Changed to horizontal layout

        # Layout para controles y visualización
        left_layout = QVBoxLayout()
        left_layout.setSpacing(1)
        

        # Botón de carga de grafo
        load_button = QPushButton("Cargar Grafo")
        load_button.clicked.connect(self.load_graph)
        left_layout.addWidget(load_button)
        
        
        # Otros botones (como estaban antes)
        add_button = QPushButton("Agregar Barrio")
        add_button.clicked.connect(self.agregar_barrio)
        left_layout.addWidget(add_button)
        
        delete_button = QPushButton("Eliminar Barrio")
        delete_button.clicked.connect(self.eliminar_barrio)
        left_layout.addWidget(delete_button)
        
        add_connection_button = QPushButton("Agregar Conexión")
        add_connection_button.clicked.connect(self.agregar_conexion)
        left_layout.addWidget(add_connection_button)
        
        # Botón para agregar tanque
        add_tank_button = QPushButton("Agregar Tanque")
        add_tank_button.clicked.connect(self.agregar_tanque)
        left_layout.addWidget(add_tank_button)

        # Botón para agregar casa
        add_house_button = QPushButton("Agregar Casa")
        add_house_button.clicked.connect(self.agregar_casa)
        left_layout.addWidget(add_house_button)
        
        optimize_button = QPushButton("Optimizar Conexiones")
        optimize_button.clicked.connect(self.optimize_graph_connections)
        left_layout.addWidget(optimize_button)

        max_flow_button = QPushButton("Calcular Flujo Máximo")
        max_flow_button.clicked.connect(self.calculate_max_flow)
        left_layout.addWidget(max_flow_button)
        
        change_direction_button = QPushButton("Cambiar Dirección de Conexión")
        change_direction_button.clicked.connect(self.change_connection_direction)
        left_layout.addWidget(change_direction_button)
        
        # Botón para simular obstrucción
        simulate_obstruction_button = QPushButton("Simular Obstrucción")
        simulate_obstruction_button.clicked.connect(self.cambiar_capacidad_conexion)
        left_layout.addWidget(simulate_obstruction_button)

        # Layout para gráfico y log
        visualization_layout = QVBoxLayout()

        # Figura de matplotlib para visualización
        self.figure = Figure(figsize=(12, 10))
        self.canvas = FigureCanvas(self.figure)
        visualization_layout.addWidget(self.canvas)

        # Área de texto para el historial de optimización
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText("El historial aparecerá aquí...")
        visualization_layout.addWidget(self.log_text)

        # Combinar layouts
        main_layout.addLayout(left_layout)
        main_layout.addLayout(visualization_layout)
        main_layout.setStretch(2, 1)  # Botones
        main_layout.setStretch(1, 3)  # Visualización y log

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.graph = None
        self.original_data = None
        self.optimization_log = []  # Nuevo atributo para mantener el registro

        self.graph = None
        self.original_data = None

    def load_graph(self):
        """Cargar grafo desde un archivo JSON"""
        self.file, _ = QFileDialog.getOpenFileName(self, "Abrir Archivo JSON", "", "JSON Files (*.json)")
        
        if self.file:
            try:
                # Cargar grafo desde JSON
                self.graph, self.original_data = load_graph_from_json(self.file)
                
                
                self.log_action(f"Grafo cargado desde: {os.path.basename(self.file)}")
                # Visualizar grafo
                self.visualize_graph()
                
                
                self.analizar_grafo_y_generar_recomendaciones()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo cargar el grafo: {str(e)}")
                self.log_action(f"Error al cargar el grafo: {str(e)}")
                



    def agregar_barrio(self):
        """Agregar un nuevo barrio con tanques, casas y conexiones."""
        # Pedir nombre del barrio
        barrio_name, ok = QInputDialog.getText(self, "Nuevo Barrio", "Nombre del nuevo barrio:")
        if not ok or not barrio_name.strip():  # Verificar que no esté vacío o solo contenga espacios
            QMessageBox.warning(self, "Error", "El nombre del barrio no puede estar vacío o contener solo espacios.")
            return

        # Verificar si el barrio ya existe
        if any(barrio['name'] == barrio_name for barrio in self.original_data):
            QMessageBox.warning(self, "Error", f"Ya existe un barrio con el nombre '{barrio_name}'.")
            return

        # Crear estructura básica del barrio
        nuevo_barrio = {
            "name": barrio_name.strip(),  # Eliminar espacios en blanco
            "elements": []
        }

        # Lista para almacenar los tanques y las casas temporalmente
        tanques = []
        casas = []

        # Agregar múltiples tanques
        while True:
            tanque_name, ok = QInputDialog.getText(self, "Nuevo Tanque", "Nombre del tanque (deja vacío para terminar):")
            if not ok or not tanque_name.strip():  # Verificar que no esté vacío o solo contenga espacios
                break

            max_capacity, ok = QInputDialog.getInt(self, "Capacidad Máxima", f"Capacidad máxima de {tanque_name.strip()}:", min=1)
            if not ok:
                break

            current_capacity, ok = QInputDialog.getInt(self, "Capacidad Actual", f"Capacidad actual de {tanque_name.strip()}:", min=0, max=max_capacity)
            if not ok:
                break

            # Agregar el tanque a la lista temporal
            tanques.append({
                "name": tanque_name.strip(),  # Eliminar espacios en blanco
                "type": "tank",
                "max_capacity": max_capacity,
                "current_capacity": current_capacity,
                "connections": []  # Las conexiones se agregarán después
            })

        # Validar que se haya agregado al menos un tanque
        if not tanques:
            QMessageBox.warning(self, "Error", "Se debe agregar al menos un tanque al barrio.")
            return

        # Agregar los tanques al barrio
        nuevo_barrio["elements"].extend(tanques)

        # Agregar múltiples casas
        while True:
            casa_name, ok = QInputDialog.getText(self, "Nueva Casa", "Nombre de la casa (deja vacío para terminar):")
            if not ok or not casa_name.strip():  # Verificar que no esté vacío o solo contenga espacios
                break

            # Agregar la casa al barrio
            casas.append({
                "name": casa_name.strip(),  # Eliminar espacios en blanco
                "type": "house",
                "connections": []  # Las conexiones se agregarán después
            })

        # Validar que se haya agregado al menos una casa
        if not casas:
            QMessageBox.warning(self, "Error", "Se debe agregar al menos una casa al barrio.")
            return

        # Agregar las casas al barrio
        nuevo_barrio["elements"].extend(casas)

        # Conexiones manuales
        while True:
            # Mostrar lista de elementos para seleccionar origen
            elementos = [elem['name'] for elem in tanques + casas]
            origen, ok = QInputDialog.getItem(
                self, 
                "Seleccionar Origen", 
                "Selecciona el elemento de origen (cancelar para terminar):", 
                elementos, 
                0, 
                False
            )
            if not ok:
                break

            # Mostrar lista de destinos (excluyendo el origen)
            destinos = [elem['name'] for elem in tanques + casas if elem['name'] != origen]
            destino, ok = QInputDialog.getItem(
                self, 
                "Seleccionar Destino", 
                f"Selecciona el elemento de destino para {origen}:", 
                destinos, 
                0, 
                False
            )
            if not ok:
                continue

            # Pedir capacidad de la conexión
            capacidad, ok = QInputDialog.getInt(
                self, 
                "Capacidad de Conexión", 
                f"Capacidad de la conexión entre {origen} y {destino}:",
                min=1
            )
            if not ok:
                continue

            # Pedir dirección de la conexión
            direccion, ok = QInputDialog.getItem(
                self, 
                "Dirección de Conexión", 
                f"Seleccione la dirección de la conexión entre {origen} y {destino}:", 
                ["both", "right", "left"], 
                0, 
                False
            )
            if not ok:
                continue

            # Buscar y actualizar los elementos originales
            for element in nuevo_barrio["elements"]:
                # Actualizar elemento de origen
                if element['name'] == origen:
                    connection_target = (f"+{destino}" if direccion == "right" 
                                        else f"-{destino}" if direccion == "left" 
                                        else destino)
                    element['connections'].append({ 
                        "target": connection_target, 
                        "capacity": capacidad
                    })
                
                # Actualizar elemento de destino para conexión bidireccional o inversa
                if element['name'] == destino:
                    if direccion == "right":
                        element['connections'].append({
                            "target": f"-{origen}",
                            "capacity": capacidad
                        })
                    elif direccion == "left":
                        element['connections'].append({
                            "target": f"+{origen}",
                            "capacity": capacidad
                        })
                    else:  # bidirectional
                        element['connections'].append({
                            "target": origen,
                            "capacity": capacidad
                        })

            # Preguntar si desea agregar más conexiones
            respuesta = QMessageBox.question(
                self, 
                "Conexiones", 
                "¿Desea agregar más conexiones?", 
                QMessageBox.Yes | QMessageBox.No
            )
            if respuesta == QMessageBox.No:
                break

        # Agregar el nuevo barrio a los datos originales
        self.original_data.append(nuevo_barrio)

        # Guardar cambios y actualizar grafo
        self.save_json(self.original_data)
        self.update_graph()
        
        self.analizar_grafo_y_generar_recomendaciones()

        # Mensaje de confirmación
        QMessageBox.information(
            self, 
            "Barrio Agregado", 
            f"Barrio {barrio_name} agregado exitosamente con {len(tanques)} tanques y {len(casas)} casas."
        )

        # Log de la acción
        self.log_action(f"Barrio agregado: {barrio_name}")
        self.log_action(f"  - Tanques: {', '.join(tanque['name'] for tanque in tanques)}")
        self.log_action(f"  - Casas: {', '.join(casa['name'] for casa in casas)}")
        
    def log_action(self, action):
        """Método genérico para registrar acciones en el historial"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_log_entry = f"[{timestamp}] {action}"
        self.optimization_log.append(full_log_entry)
        self.log_text.append(full_log_entry)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

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
            
            tanques_en_barrio = [elem['name'] for elem in barrio_a_eliminar['elements'] if elem.get('type') == 'tank']
            casas_en_barrio = [elem['name'] for elem in barrio_a_eliminar['elements'] if elem.get('type') == 'house']

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
            self.save_json(self.original_data) 
            
            # Pasar 'self.original_data' correctamente
            
                
            self.analizar_grafo_y_generar_recomendaciones()
            # Confirmación de eliminación
            QMessageBox.information(self, "Barrio Eliminado", f"El barrio '{barrio_name}' ha sido eliminado exitosamente.")
            
            self.log_action(f"Barrio eliminado: {barrio_name}")
            self.log_action(f"  - Tanques eliminados: {', '.join(tanques_en_barrio)}")
            self.log_action(f"  - Casas eliminadas: {', '.join(casas_en_barrio)}")

        except Exception as e:
            # En caso de error, mostrar mensaje y evitar que la aplicación se cierre
            QMessageBox.critical(self, "Error", f"Ocurrió un error al eliminar el barrio: {str(e)}")
            self.log_action(f"Error al eliminar el barrio: {str(e)}")



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

        # Cargar imágenes para nodos
        import matplotlib.image as mpimg
        import os

        # Ruta a los iconos (ajusta estas rutas según tu estructura de directorios)
        tank_icon = mpimg.imread('icons\\tanque.png')  # Reemplaza con la ruta a tu ícono de tanque
        house_icon = mpimg.imread('icons\\casa.png')  # Reemplaza con la ruta a tu ícono de casa

        # Dibujar nodos con imágenes
        for node_type, nodes, icon in [('tank', tanks, tank_icon), ('house', houses, house_icon)]:
            for node in nodes:
                x, y = pos[node]
                # Dibujar imagen del nodo
                ax.imshow(icon, extent=(x-0.15, x+0.15, y-0.15, y+0.15), zorder=10)
                
                # Añadir etiqueta de texto SOBRE la imagen
                ax.text(x, y+0.2, node, ha='center', va='bottom', fontsize=8, 
                        bbox=dict(facecolor='white', edgecolor='gray', alpha=0.7))

                # Si es un tanque, añadir información de capacidad
                node_data = self.graph.nodes[node]
                if node_type == 'tank':
                    capacity_text = f"{node_data.get('current_capacity', 0)}/{node_data.get('max_capacity', 0)}L"
                    ax.text(x, y-0.2, capacity_text, ha='center', va='top', fontsize=7,
                            bbox=dict(facecolor='white', edgecolor='gray', alpha=0.7))

        # Dibujar aristas con dirección correcta y estilos
        for (u, v, data) in self.graph.edges(data=True):
            direction = data.get('direction', 'both')

            # Dibujar arista con estilo de flecha correcto
            nx.draw_networkx_edges(
                self.graph,
                pos,
                edgelist=[(u, v)],
                edge_color='gray',
                connectionstyle='arc3,rad=0.1',
                arrows=True,
                arrowsize=35,
                ax=ax
            )

        # Etiquetas de las capacidades de las aristas
        edge_labels = {
            (u, v): f"{data.get('capacidad', 0)} L/s" for u, v, data in self.graph.edges(data=True)
        }
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_size=10, font_color='blue', rotate = True, ax=ax)

        # Añadir nombres de barrios
        for neighborhood in self.original_data:
            # Encontrar las posiciones de los nodos en este barrio
            barrio_nodes = [element['name'] for element in neighborhood['elements']]
            barrio_pos = {node: coords for node, coords in pos.items() if node in barrio_nodes}
            
            if barrio_pos:
                # Calcular el centro del barrio
                x_coords = [coord[0] for coord in barrio_pos.values()]
                y_coords = [coord[1] for coord in barrio_pos.values()]
                center_x = (max(x_coords) + min(x_coords)) / 2
                center_y = max(y_coords) + 0.5  # Posicionar sobre los nodos

                # Añadir nombre del barrio
                ax.text(center_x, center_y, neighborhood['name'], 
                        ha='center', va='bottom', 
                        fontsize=12, fontweight='bold', 
                        bbox=dict(facecolor='white', edgecolor='gray', alpha=0.7))

        ax.axis('off')

        # Dibujar canvas
        self.canvas.draw()
            
    def optimize_graph_connections(self):
        """Optimizar conexiones de grafo dirigido""" 
        if self.graph is None: 
            QMessageBox.warning(self, "Error", "Primero cargue un grafo") 
            return 

        try: 
            # Registrar inicio de optimización usando log_action 
            self.log_action("Iniciando Optimización de Conexiones") 

            # Crear una copia del grafo original para optimizar 
            optimized_graph = self.graph.copy() 

            # Collect all edges with their capacities 
            edges_with_capacity = [(u, v, data.get('capacidad', 0)) for (u, v, data) in optimized_graph.edges(data=True)] 

            # Sort edges by capacity in ascending order 
            edges_with_capacity.sort(key=lambda x: x[2]) 

            # Keep track of connected components 
            connected_components = list(nx.weakly_connected_components(optimized_graph)) 

            # Remove unnecessary edges 
            removed_edges = [] 
            for u, v, capacity in edges_with_capacity: 
                # Remove the edge temporarily 
                optimized_graph.remove_edge(u, v) 

                # Check if graph remains connected after removing the edge 
                new_components = list(nx.weakly_connected_components(optimized_graph)) 

                if len(new_components) > len(connected_components): 
                    # If removing this edge breaks connectivity, add it back 
                    optimized_graph.add_edge(u, v, capacidad=capacity) 
                else: 
                    # Edge is unnecessary, log the removal 
                    removed_edges.append((u, v, capacity)) 
                    self.log_action(f"Conexión eliminada: {u} <-> {v} (Capacidad: {capacity} L/s)") 
                    connected_components = new_components 

                    # Actualizar self.original_data para eliminar la conexión
                    self.remove_connection_from_data(u, v)

            # Update the graph's edges 
            self.graph = optimized_graph 

            # Visualize the optimized graph 
            self.visualize_graph() 

            # Log optimization results 
            self.log_action(f"Optimización completada. Se eliminaron {len(removed_edges)} conexiones innecesarias.") 
            
            
                
            self.analizar_grafo_y_generar_recomendaciones()

            # Show optimization results 
            results_message = ( 
                f"Optimización Completada!\n" 
                f"Se eliminaron {len(removed_edges)} conexiones innecesarias." 
            ) 
            QMessageBox.information(self, "Resultados de Optimización", results_message) 

            # Guardar cambios en el JSON después de la optimización
            self.save_json(self.original_data)

        except Exception as e: 
            # Log any errors that occur 
            self.log_action(f"Error en optimización de conexiones: {str(e)}") 
            QMessageBox.critical(self, "Error", f"Ocurrió un error al optimizar: {str(e)}") 

    def remove_connection_from_data(self, source, target):
        """Eliminar la conexión de los elementos en self.original_data."""
        for barrio in self.original_data:
            for element in barrio['elements']:
                # Eliminar conexión del elemento de origen
                element['connections'] = [conn for conn in element['connections'] if not (conn['target'] == target or conn['target'] == f"+{target}" or conn['target'] == f"-{target}")]
                # Eliminar conexión del elemento de destino
                element['connections'] = [conn for conn in element['connections'] if not (conn['target'] == source or conn['target'] == f"+{source}" or conn['target'] == f"-{source}")]
            
        
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
        
    def agregar_conexion(self):
        """Agregar una nueva conexión entre elementos del grafo.""" 
        if not self.original_data: 
            QMessageBox.warning(self, "Error", "Primero cargue un grafo") 
            return 

        # Recopilar todos los elementos de todos los barrios 
        all_elements = [] 
        for barrio in self.original_data: 
            all_elements.extend(barrio['elements']) 

        # Nombres de todos los elementos para selección 
        element_names = [element['name'] for element in all_elements] 

        if len(element_names) < 2: 
            QMessageBox.warning(self, "Error", "Se necesitan al menos dos elementos para crear una conexión") 
            return 

        # Seleccionar elemento de origen 
        origen, ok1 = QInputDialog.getItem( 
            self, 
            "Seleccionar Origen", 
            "Selecciona el elemento de origen:", 
            element_names, 
            0, 
            False 
        ) 
        if not ok1: 
            return 

        # Seleccionar elemento de destino (excluyendo el origen) 
        destino_options = [name for name in element_names if name != origen] 
        destino, ok2 = QInputDialog.getItem( 
            self, 
            "Seleccionar Destino", 
            f"Selecciona el elemento de destino para {origen}:", 
            destino_options, 
            0, 
            False 
        ) 
        if not ok2: 
            return 

        # Pedir capacidad de la conexión 
        capacidad, ok3 = QInputDialog.getInt( 
            self, 
            "Capacidad de Conexión", 
            f"Ingrese la capacidad de la conexión entre {origen} y {destino}:", 
            min=1 
        ) 
        if not ok3: 
            return 

        # Pedir dirección de la conexión 
        direccion, ok4 = QInputDialog.getItem( 
            self, 
            "Dirección de Conexión", 
            f"Seleccione la dirección de la conexión entre {origen} y {destino}:", 
            ["both", "right", "left"], 
            0, 
            False 
        ) 
        if not ok4: 
            return 

        # Buscar y actualizar los elementos originales 
        for barrio in self.original_data: 
            for element in barrio['elements']: 
                # Actualizar elemento de origen 
                if element['name'] == origen: 
                    connection_target = (f"+{destino}" if direccion == "right" 
                                        else f"-{destino}" if direccion == "left" 
                                        else destino) 

                    # Aquí se limita la capacidad a la capacidad máxima del tanque 
                    if element['type'] == 'tank': 
                        capacidad_conexion = min(element['max_capacity'], capacidad)  # Limitar a la capacidad máxima del tanque 
                    else: 
                        capacidad_conexion = capacidad  # Para casas, usar la capacidad proporcionada 

                    element['connections'].append({ 
                        "target": connection_target, 
                        "capacity": capacidad_conexion  # Usar capacidad limitada 
                    }) 

                # Actualizar elemento de destino para conexión bidireccional o inversa 
                if element['name'] == destino: 
                    if direccion == "right": 
                        element['connections'].append({ 
                            "target": f"-{origen}", 
                            "capacity": capacidad_conexion 
                        }) 
                    elif direccion == "left": 
                        element['connections'].append({ 
                            "target": f"+{origen}", 
                            "capacity": capacidad_conexion 
                        }) 
                    else:  # bidirectional 
                        element['connections'].append({ 
                            "target": origen, 
                            "capacity": capacidad_conexion 
                        }) 

        # Guardar cambios y actualizar grafo 
        self.save_json(self.original_data) 
        self.update_graph() 

        # Registrar la acción en el historial 
        self.log_action(f"Conexión agregada: {origen} <-> {destino} (Capacidad: {capacidad_conexion} L/s, Dirección: {direccion})") 

        self.analizar_grafo_y_generar_recomendaciones()

        # Mensaje de confirmación 
        QMessageBox.information( 
            self, 
            "Conexión Agregada", 
            f"Conexión entre {origen} y {destino} agregada exitosamente." 
        ) 
        
            
    def agregar_tanque(self):
        """Método para agregar un nuevo tanque"""
        # Pedir nombre del tanque
        tanque_name, ok1 = QInputDialog.getText(self, "Nuevo Tanque", "Nombre del tanque:")
        if not ok1 or not tanque_name:
            return

        # Pedir capacidad máxima
        max_capacity, ok2 = QInputDialog.getInt(
            self, 
            "Capacidad Máxima", 
            f"Capacidad máxima de {tanque_name}:", 
            min=1
        )
        if not ok2:
            return

        # Pedir capacidad actual
        current_capacity, ok3 = QInputDialog.getInt(
            self, 
            "Capacidad Actual", 
            f"Capacidad actual de {tanque_name}:", 
            min=0, 
            max=max_capacity
        )
        if not ok3:
            return


        # Verificar si hay barrios existentes
        if not self.original_data:
            # Si no hay barrios, crear uno nuevo
            barrio_name, ok6 = QInputDialog.getText(
                self, 
                "Nuevo Barrio", 
                "No hay barrios. Nombre del nuevo barrio:"
            )
            if not ok6 or not barrio_name:
                return
            
            # Crear nuevo barrio con el tanque
            nuevo_barrio = {
                "name": barrio_name,
                "elements": []
            }
            self.original_data.append(nuevo_barrio)

        # Preguntar en qué barrio agregar el tanque
        barrio_names = [barrio['name'] for barrio in self.original_data]
        barrio_name, ok7 = QInputDialog.getItem(
            self, 
            "Seleccionar Barrio", 
            "Selecciona el barrio para agregar el tanque:", 
            barrio_names, 
            0, 
            False
        )
        if not ok7:
            return

        # Encontrar el barrio seleccionado y agregar el tanque
        for barrio in self.original_data:
            if barrio['name'] == barrio_name:
                nuevo_tanque = {
                    "name": tanque_name,
                    "type": "tank",
                    "max_capacity": max_capacity,
                    "current_capacity": current_capacity,
                    "connections": []
                }
                barrio['elements'].append(nuevo_tanque)
                break

        # Guardar cambios
        self.save_json(self.original_data)
        self.update_graph()

        # Log de la acción
        self.log_action(f"Tanque agregado: {tanque_name} en {barrio_name}")
        
        self.analizar_grafo_y_generar_recomendaciones()
        
        # Mensaje de confirmación
        QMessageBox.information(
            self, 
            "Tanque Agregado", 
            f"Tanque {tanque_name} agregado exitosamente a {barrio_name}."
        )

    def agregar_casa(self):
        """Método para agregar una nueva casa"""
        # Verificar si hay barrios existentes
        if not self.original_data:
            QMessageBox.warning(self, "Error", "Primero debe crear un barrio")
            return

        # Pedir nombre de la casa
        casa_name, ok1 = QInputDialog.getText(self, "Nueva Casa", "Nombre de la casa:")
        if not ok1 or not casa_name:
            return

        # Preguntar en qué barrio agregar la casa
        barrio_names = [barrio['name'] for barrio in self.original_data]
        barrio_name, ok2 = QInputDialog.getItem(
            self, 
            "Seleccionar Barrio", 
            "Selecciona el barrio para agregar la casa:", 
            barrio_names, 
            0, 
            False
        )
        if not ok2:
            return

        # Encontrar el barrio seleccionado y agregar la casa
        for barrio in self.original_data:
            if barrio['name'] == barrio_name:
                nueva_casa = {
                    "name": casa_name,
                    "type": "house",
                    "connections": []
                }
                barrio['elements'].append(nueva_casa)
                break

        # Guardar cambios
        self.save_json(self.original_data)
        self.update_graph()

        # Log de la acción
        self.log_action(f"Casa agregada: {casa_name} en {barrio_name}")
        
        
                
        self.analizar_grafo_y_generar_recomendaciones()
        # Mensaje de confirmación
        QMessageBox.information(
            self, 
            "Casa Agregada", 
            f"Casa {casa_name} agregada exitosamente a {barrio_name}."
        )
        
    def bfs_find_augmenting_path(self,G, source, sink):
        """Buscar un camino aumentante usando BFS y retornar el flujo posible."""
        visited = {node: False for node in G.nodes()}
        parent = {node: None for node in G.nodes()}
        queue = [source]
        visited[source] = True
        flow = float('Inf')  # Inicializar el flujo como infinito

        while queue:
            u = queue.pop(0)

            for v in G.neighbors(u):
                # Solo considerar aristas con capacidad positiva en la dirección correcta
                if not visited[v] and G[u][v]['capacidad'] > 0:
                    visited[v] = True
                    parent[v] = u
                    flow = min(flow, G[u][v]['capacidad'])  # Actualizar el flujo mínimo

                    if v == sink:
                        return parent, flow  # Retornar el camino y el flujo

                    queue.append(v)

        return None, 0  # No se encontró un camino
        
    def calculate_max_flow(self):
        """Calcular y mostrar el flujo máximo en el grafo"""
        if self.graph is None:
            QMessageBox.warning(self, "Error", "Primero cargue un grafo")
            return

        try:
            # Obtener la lista de tanques y casas
            tanks = [n for n in self.graph.nodes() if self.graph.nodes[n].get('type') == 'tank']
            houses = [n for n in self.graph.nodes() if self.graph.nodes[n].get('type') == 'house']

            if not tanks or not houses:
                QMessageBox.warning(self, "Error", "Se necesitan tanques y casas para calcular el flujo máximo")
                return

            # Seleccionar tanque (fuente)
            source, ok1 = QInputDialog.getItem(self, "Seleccionar Fuente", "Selecciona un tanque como fuente:", tanks, 0, False)
            if not ok1:
                return

            # Seleccionar casa (sumidero)
            sink, ok2 = QInputDialog.getItem(self, "Seleccionar Sumidero", "Selecciona una casa como sumidero:", houses, 0, False)
            if not ok2:
                return

            # Calcular flujo máximo usando networkx
            max_flow_value, max_flow_dict = nx.maximum_flow(self.graph, source, sink, capacity='capacidad')

            # Preparar mensaje de resultados
            results_message = (
                f"Flujo Máximo Calculado:\n"
                f"Desde {source} hasta {sink}\n"
                f"Valor de Flujo Máximo: {max_flow_value} L/s"
            )

            # Mostrar detalles del flujo máximo
            QMessageBox.information(self, "Resultado de Flujo Máximo", results_message)
        
                
            self.analizar_grafo_y_generar_recomendaciones()
            # Log de la acción
            self.log_action(f"Flujo Máximo calculado: {max_flow_value} L/s desde {source} a {sink}")

        except Exception as e:
            # Manejo de errores detallado
            error_message = f"Error al calcular flujo máximo: {str(e)}"
            QMessageBox.critical(self, "Error", error_message)
            self.log_action(error_message)
            
    def change_connection_direction(self):
        """Cambiar la dirección de una conexión existente en el grafo."""
        if not self.original_data:
            QMessageBox.warning(self, "Error", "Primero cargue un grafo")
            return

        # Recopilar todos los elementos de todos los barrios
        all_elements = []
        for barrio in self.original_data:
            all_elements.extend(barrio['elements'])

        # Nombres de todos los elementos para selección
        element_names = [element['name'] for element in all_elements]

        if len(element_names) < 2:
            QMessageBox.warning(self, "Error", "Se necesitan al menos dos elementos para cambiar la dirección de una conexión")
            return

        # Seleccionar elemento de origen
        origen, ok1 = QInputDialog.getItem(
            self,
            "Seleccionar Origen",
            "Selecciona el elemento de origen:",
            element_names,
            0,
            False
        )
        if not ok1:
            return

        # Seleccionar elemento de destino (excluyendo el origen)
        destino_options = [name for name in element_names if name != origen]
        destino, ok2 = QInputDialog.getItem(
            self,
            "Seleccionar Destino",
            f"Selecciona el elemento de destino para {origen}:",
            destino_options,
            0,
            False
        )
        if not ok2:
            return

        # Pedir nueva dirección de la conexión
        nueva_direccion, ok3 = QInputDialog.getItem(
            self,
            "Nueva Dirección de Conexión",
            f"Selecciona la nueva dirección de la conexión entre {origen} y {destino}:",
            ["both", "right", "left"],
            0,
            False
        )
        if not ok3:
            return

        # Actualizar la dirección en los elementos originales
        for barrio in self.original_data:
            for element in barrio['elements']:
                # Actualizar elemento de origen
                if element['name'] == origen:
                    # Buscar la conexión existente
                    for conn in element['connections']:
                        if conn['target'] == destino or conn['target'] == f"+{destino}" or conn['target'] == f"-{destino}":
                            # Mantener la capacidad de la conexión existente
                            existing_capacity = conn['capacity']
                            # Eliminar la conexión existente
                            element['connections'].remove(conn)
                            break  # Salir del bucle una vez que se encuentra y elimina la conexión

                    # Agregar nueva conexión
                    connection_target = (f"+{destino}" if nueva_direccion == "right"
                                        else f"-{destino}" if nueva_direccion == "left"
                                        else destino)
                    element['connections'].append({
                        "target": connection_target,
                        "capacity": existing_capacity
                    })

                # Actualizar elemento de destino para conexión bidireccional o inversa
                if element['name'] == destino:
                    # Buscar la conexión existente
                    for conn in element['connections']:
                        if conn['target'] == origen or conn['target'] == f"+{origen}" or conn['target'] == f"-{origen}":
                            # Mantener la capacidad de la conexión existente
                            existing_capacity = conn['capacity']
                            # Eliminar la conexión existente
                            element['connections'].remove(conn)
                            break  # Salir del bucle una vez que se encuentra y elimina la conexión

                    if nueva_direccion == "right":
                        element['connections'].append({
                            "target": f"-{origen}",
                            "capacity": existing_capacity  # Mantener la capacidad
                        })
                    elif nueva_direccion == "left":
                        element['connections'].append({
                            "target": f"+{origen}",
                            "capacity": existing_capacity  # Mantener la capacidad
                        })
                    else:  # bidirectional
                        element['connections'].append({
                            "target": origen,
                            "capacity": existing_capacity  # Mantener la capacidad
                        })

        # Guardar cambios en el JSON
        self.save_json(self.original_data)
        self.update_graph()

        # Log de la acción
        self.log_action(f"Dirección de la conexión entre {origen} y {destino} cambiada a '{nueva_direccion}'.")


                
        self.analizar_grafo_y_generar_recomendaciones()
        # Mensaje de confirmación
        QMessageBox.information(
            self,
            "Dirección Cambiada",
            f"Dirección de la conexión entre {origen} y {destino} cambiada exitosamente."
        )
        
        
    def cambiar_capacidad_conexion(self):
        """Cambiar la capacidad de una conexión existente en el grafo."""
        if not self.original_data:
            QMessageBox.warning(self, "Error", "Primero cargue un grafo")
            return

        # Recopilar todos los elementos de todos los barrios
        all_elements = []
        for barrio in self.original_data:
            all_elements.extend(barrio['elements'])

        # Nombres de todos los elementos para selección
        element_names = [element['name'] for element in all_elements]

        if len(element_names) < 2:
            QMessageBox.warning(self, "Error", "Se necesitan al menos dos elementos para cambiar la capacidad de una conexión")
            return

        # Seleccionar elemento de origen
        origen, ok1 = QInputDialog.getItem(
            self,
            "Seleccionar Origen",
            "Selecciona el elemento de origen:",
            element_names,
            0,
            False
        )
        if not ok1:
            return

        # Seleccionar elemento de destino (excluyendo el origen)
        destino_options = [name for name in element_names if name != origen]
        destino, ok2 = QInputDialog.getItem(
            self,
            "Seleccionar Destino",
            f"Selecciona el elemento de destino para {origen}:",
            destino_options,
            0,
            False
        )
        if not ok2:
            return

        # Pedir nueva capacidad de la conexión
        nueva_capacidad, ok3 = QInputDialog.getInt(
            self,
            "Nueva Capacidad de Conexión",
            f"Ingrese la nueva capacidad de la conexión entre {origen} y {destino}:",
            min=1
        )
        if not ok3:
            return

        # Actualizar la capacidad en los elementos originales
        for barrio in self.original_data:
            for element in barrio['elements']:
                # Actualizar elemento de origen
                if element['name'] == origen:
                    for conn in element['connections']:
                        if conn['target'] == destino or conn['target'] == f"+{destino}" or conn['target'] == f"-{destino}":
                            conn['capacity'] = nueva_capacidad  # Cambiar la capacidad
                            break  # Salir del bucle una vez que se encuentra y actualiza la conexión

                # Actualizar elemento de destino para conexión bidireccional o inversa
                if element['name'] == destino:
                    for conn in element['connections']:
                        if conn['target'] == origen or conn['target'] == f"+{origen}" or conn['target'] == f"-{origen}":
                            conn['capacity'] = nueva_capacidad  # Cambiar la capacidad
                            break  # Salir del bucle una vez que se encuentra y actualiza la conexión

        # Guardar cambios en el JSON
        self.save_json(self.original_data)
        self.update_graph()

        # Log de la acción
        self.log_action(f"Capacidad de la conexión entre {origen} y {destino} cambiada a {nueva_capacidad} L/s.")


                
        self.analizar_grafo_y_generar_recomendaciones()
        # Mensaje de confirmación
        QMessageBox.information(
            self,
            "Capacidad Cambiada",
            f"Capacidad de la conexión entre {origen} y {destino} cambiada exitosamente a {nueva_capacidad} L/s."
        )
        
    def analizar_grafo_y_generar_recomendaciones(self):
        """Analizar el grafo y generar recomendaciones automáticamente."""
        if not self.graph:
            return

        recomendaciones = []

        # Verificar conexiones de baja capacidad
        for (u, v, data) in self.graph.edges(data=True):
            capacidad_actual = data.get('capacidad', 0)
            UMBRAL_BAJO = 20  # L/s

            if capacidad_actual < UMBRAL_BAJO:
                recomendaciones.append(f"Conexión de baja capacidad detectada: {u} -> {v} (Capacidad: {capacidad_actual} L/s)")

        # Verificar tanques y casas sin conexiones
        for node in self.graph.nodes(data=True):
            if node[1]['type'] == 'tank':
                if not self.graph.out_degree(node[0]):
                    recomendaciones.append(f"Tanque {node[0]} sin conexiones. Considera conectarlo a una casa.")
            elif node[1]['type'] == 'house':
                if not self.graph.in_degree(node[0]):
                    recomendaciones.append(f"Casa {node[0]} sin conexiones. Considera conectarla a un tanque.")

        # Mostrar recomendaciones si hay alguna
        if recomendaciones:
            self.mostrar_recomendaciones(recomendaciones)

    def mostrar_recomendaciones(self, recomendaciones):
        """Mostrar las recomendaciones en un cuadro de diálogo."""
        dialogo_recomendaciones = QDialog(self)
        dialogo_recomendaciones.setWindowTitle("Recomendaciones de Optimización")
        layout = QVBoxLayout()

        for recomendacion in recomendaciones:
            label = QLabel(recomendacion)
            layout.addWidget(label)

        # Botón para ignorar
        btn_ignorar = QPushButton("Ignorar")
        btn_ignorar.clicked.connect(dialogo_recomendaciones.close)
        layout.addWidget(btn_ignorar)

        dialogo_recomendaciones.setLayout(layout)
        dialogo_recomendaciones.exec_()


def main():
    app = QApplication(sys.argv)
    main_window = WaterSystemGraphVisualizer()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
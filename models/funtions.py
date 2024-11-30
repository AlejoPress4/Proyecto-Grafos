import networkx as nx
import json
import math
from PyQt5.QtWidgets import QMessageBox, QInputDialog

def load_graph_from_json(file_path):
    """Cargar un grafo desde un archivo JSON, procesando direcciones con prefijos."""
    import json
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Crear grafo dirigido
    G = nx.DiGraph()

    for neighborhood in data:
        for element in neighborhood['elements']:
            # Añadir nodo con atributos
            G.add_node(element['name'], **{k: v for k, v in element.items() if k != 'connections'})

            # Procesar conexiones
            for connection in element.get('connections', []):
                # Validar que la conexión tiene un nodo destino definido
                target = connection['target']
                capacity = connection.get('capacity', 0)

                # Determinar la dirección según el prefijo
                if target.startswith('+'):
                    dest = target[1:]  # Eliminar el prefijo '+'
                    G.add_edge(element['name'], dest, capacidad=capacity, direction='right')
                elif target.startswith('-'):
                    dest = target[1:]  # Eliminar el prefijo '-'
                    G.add_edge(dest, element['name'], capacidad=capacity, direction='left')
                else:
                    # Sin prefijo, conexión bidireccional por defecto
                    dest = target
                    G.add_edge(element['name'], dest, capacidad=capacity, direction='both')

    return G, data




def calculate_max_flow(G, source=None, sink=None):
    """Calcular flujo máximo usando Ford-Fulkerson"""
    # Si no se especifican fuente y sumidero, intentar encontrarlos
    if source is None:
        source = [n for n in G.nodes() if G.nodes[n].get('type') == 'tank'][0]
    
    if sink is None:
        sink = [n for n in G.nodes() if G.nodes[n].get('type') == 'house'][-1]
    
    try:
        # Calcular flujo máximo
        max_flow_value, max_flow_dict = nx.maximum_flow(G, source, sink)
        return max_flow_value, max_flow_dict
    except Exception as e:
        print(f"Error calculando flujo máximo: {e}")
        return 0, {}


import networkx as nx
import math

def assign_graph_positions(graph, data):
    """Asigna posiciones a los nodos, separando los barrios en disposición circular."""
    pos = {}
    x_offset = 0  # Desplazamiento horizontal inicial entre barrios

    for i, neighborhood in enumerate(data):
        # Extraer los nodos del barrio
        nodes = [element['name'] for element in neighborhood['elements']]

        # Generar un layout circular para los nodos del barrio
        circular_pos = nx.circular_layout(graph.subgraph(nodes))

        # Ajustar el layout circular con un desplazamiento horizontal único por barrio
        for node, (x, y) in circular_pos.items():
            pos[node] = (x + x_offset, y)

        # Incrementar el desplazamiento horizontal para el siguiente barrio
        x_offset += 3  # Ajusta el valor según el espacio necesario entre barrios

    return pos

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

    # Guardar cambios y actualizar grafo
    self.save_json(self.original_data)
    self.update_graph()

    # Mensaje de confirmación
    QMessageBox.information(
        self, 
        "Conexión Agregada", 
        f"Conexión entre {origen} y {destino} agregada exitosamente."
    )
import networkx as nx
import json
import math

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

def _agregar_conexion(self, origen, destino, peso):
        if origen not in self.barrios and origen not in self.tanques:
            raise ValueError(f"Origen {origen} no definido")
        if destino not in self.barrios and destino not in self.tanques:
            raise ValueError(f"Destino {destino} no definido")
        if origen in self.conexiones and destino in self.conexiones[origen]:
            raise ValueError(f"Conexión duplicada entre {origen} y {destino}")
        if origen not in self.conexiones:
            self.conexiones[origen] = []
        self.conexiones[origen].append((destino, peso))



# Sistema de Visualización de Grafos de Tuberías

Este proyecto es una aplicación para la visualización y gestión de un sistema de tuberías utilizando grafos. La interfaz gráfica está construida con PyQt5 y la visualización de grafos se realiza con NetworkX y Matplotlib.

## Archivos Principales

### `models/interfaz.py`

Este archivo contiene la clase `WaterSystemGraphVisualizer`, que es la ventana principal de la aplicación. A continuación se describen los métodos principales y los algoritmos utilizados:

- **`__init__(self)`**: Inicializa la interfaz de usuario.
- **`initUI(self)`**: Configura la interfaz de usuario, incluyendo botones y layouts.
- **`load_graph(self)`**: Carga un grafo desde un archivo JSON utilizando la función `load_graph_from_json`.
- **`agregar_barrio(self)`**: Agrega un nuevo barrio con tanques, casas y conexiones.
- **`eliminar_barrio(self)`**: Elimina un barrio existente del grafo y del JSON.
- **`save_json(self, data)`**: Guarda los cambios en el archivo JSON.
- **`visualize_graph(self)`**: Visualiza el grafo de tuberías utilizando `matplotlib` para la representación gráfica y `networkx` para la disposición de los nodos.
- **`optimize_graph_connections(self)`**: Optimiza las conexiones del grafo utilizando el algoritmo de Prim para encontrar el árbol de expansión mínima.
- **`remove_connection_from_data(self, source, target)`**: Elimina una conexión de los elementos en `self.original_data`.
- **`update_graph(self)`**: Reconstruye el grafo desde `self.original_data`.
- **`agregar_conexion(self)`**: Agrega una nueva conexión entre elementos del grafo.
- **`agregar_tanque(self)`**: Agrega un nuevo tanque.
- **`agregar_casa(self)`**: Agrega una nueva casa.
- **`calculate_max_flow(self)`**: Calcula y muestra el flujo máximo en el grafo utilizando el algoritmo de Ford-Fulkerson implementado en `networkx`.
- **`change_connection_direction(self)`**: Cambia la dirección de una conexión existente en el grafo.
- **`cambiar_capacidad_conexion(self)`**: Cambia la capacidad de una conexión existente en el grafo.
- **`analizar_grafo_y_generar_recomendaciones(self)`**: Analiza el grafo y genera recomendaciones automáticamente.
- **`mostrar_recomendaciones(self, recomendaciones)`**: Muestra las recomendaciones en un cuadro de diálogo.
- **`log_action(self, action)`**: Registra acciones en el historial.

### `models/funtions.py`

Este archivo contiene funciones auxiliares para la gestión y análisis del grafo. A continuación se describen las funciones principales y los algoritmos utilizados:

- **`load_graph_from_json(file_path)`**: Carga un grafo desde un archivo JSON.
- **`calculate_max_flow(G, source=None, sink=None)`**: Calcula el flujo máximo usando el algoritmo de Ford-Fulkerson implementado en `networkx`.
- **`assign_graph_positions(graph, data)`**: Asigna posiciones a los nodos utilizando el algoritmo de disposición de resorte (`spring_layout`) de `networkx`.
- **`agregar_conexion(self)`**: Agrega una nueva conexión entre elementos del grafo.

## Requisitos

- Python 3.x
- PyQt5: `pip install PyQt5`
- NetworkX: `pip install networkx`
- Matplotlib: `pip install matplotlib`

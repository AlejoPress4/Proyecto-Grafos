import json
import heapq

class RedAcueducto:
    def __init__(self):
        self.barrios = {}
        self.tanques = {}
        self.conexiones = {}

    def cargar_desde_json(self, archivo):
        with open(archivo, 'r') as f:
            data = json.load(f)
            self._procesar_datos(data)

    def _procesar_datos(self, data):
        # Procesar barrios
        for barrio in data.get('barrios', []):
            self.barrios[barrio['id']] = barrio

        # Procesar tanques
        for tanque in data.get('tanques', []):
            self.tanques[tanque['id']] = tanque

        # Procesar conexiones
        for conexion in data.get('conexiones', []):
            self._agregar_conexion(conexion['origen'], conexion['destino'], conexion['peso'])

        self._verificar_consistencia()

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

    def _verificar_consistencia(self):
        # Verificar bucles y conexiones inválidas
        visitados = set()
        for origen in self.conexiones:
            if not self._dfs(origen, visitados, set()):
                raise ValueError(f"Bucle detectado en la red a partir de {origen}")

    def _dfs(self, nodo, visitados, en_curso):
        if nodo in en_curso:
            return False
        if nodo in visitados:
            return True
        en_curso.add(nodo)
        for vecino, _ in self.conexiones.get(nodo, []):
            if not self._dfs(vecino, visitados, en_curso):
                return False
        en_curso.remove(nodo)
        visitados.add(nodo)
        return True

    def agregar_barrio(self, id, nombre):
        if id in self.barrios:
            raise ValueError(f"Barrio {id} ya existe")
        self.barrios[id] = {'id': id, 'nombre': nombre}

    def eliminar_barrio(self, id):
        if id not in self.barrios:
            raise ValueError(f"Barrio {id} no existe")
        del self.barrios[id]
        # Eliminar conexiones relacionadas
        self.conexiones = {k: v for k, v in self.conexiones.items() if k != id and id not in v}

    def agregar_tanque(self, id, capacidad):
        if id in self.tanques:
            raise ValueError(f"Tanque {id} ya existe")
        self.tanques[id] = {'id': id, 'capacidad': capacidad}

    def eliminar_tanque(self, id):
        if id not in self.tanques:
            raise ValueError(f"Tanque {id} no existe")
        del self.tanques[id]
        # Eliminar conexiones relacionadas
        self.conexiones = {k: v for k, v in self.conexiones.items() if k != id and id not in v}

    def agregar_conexion(self, origen, destino, peso):
        self._agregar_conexion(origen, destino, peso)
        self._verificar_consistencia()

    def eliminar_conexion(self, origen, destino):
        if origen in self.conexiones and destino in self.conexiones[origen]:
            self.conexiones[origen] = [conn for conn in self.conexiones[origen] if conn[0] != destino]
        self._verificar_consistencia()

    def encontrar_ruta_optima(self, origen, destino):
        # Implementar el algoritmo de Dijkstra
        distancias = {nodo: float('inf') for nodo in self.barrios}
        distancias[origen] = 0
        pq = [(0, origen)]
        while pq:
            (dist_actual, nodo_actual) = heapq.heappop(pq)
            if dist_actual > distancias[nodo_actual]:
                continue
            for vecino, peso in self.conexiones.get(nodo_actual, []):
                distancia = dist_actual + peso
                if distancia < distancias[vecino]:
                    distancias[vecino] = distancia
                    heapq.heappush(pq, (distancia, vecino))
        return distancias[destino]

# Ejemplo de uso
red = RedAcueducto()
red.cargar_desde_json('red_acueducto.json')
print(red.encontrar_ruta_optima('barrio1', 'barrio5'))
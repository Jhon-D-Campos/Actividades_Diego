"""Grafo no dirigido; conserva la API del proyecto original."""
import math
import networkx as nx


class Nodo:
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.vecinos = {}

    def agregar_vecino(self, vecino: str, peso: float):
        self.vecinos[vecino] = peso


class Grafo:
    def __init__(self):
        self.nodos = {}
        self.red = nx.Graph()

    def agregar_nodo(self, nombre: str):
        nombre = nombre.strip().upper()
        if not nombre:
            raise ValueError('El nombre no puede estar vacío.')
        self.nodos.setdefault(nombre, Nodo(nombre))
        self.red.add_node(nombre)

    def agregar_conexion(self, origen: str, destino: str, peso: float):
        origen, destino = origen.strip().upper(), destino.strip().upper()
        peso = float(peso)
        if not math.isfinite(peso) or peso < 0:
            raise ValueError('El peso debe ser finito y no negativo.')
        if origen == destino:
            raise ValueError('El origen y destino deben ser distintos.')
        self.agregar_nodo(origen)
        self.agregar_nodo(destino)
        self.nodos[origen].agregar_vecino(destino, peso)
        self.nodos[destino].agregar_vecino(origen, peso)
        self.red.add_edge(origen, destino, weight=peso)

    def dijkstra(self, inicio: str, destino: str):
        inicio, destino = inicio.strip().upper(), destino.strip().upper()
        if inicio not in self.red or destino not in self.red:
            raise ValueError('Uno de los nodos no existe.')
        try:
            return nx.single_source_dijkstra(self.red, inicio, destino, weight='weight')
        except nx.NetworkXNoPath:
            return float('inf'), []

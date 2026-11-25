
"""
Módulo de gestión de grafos no dirigidos y ponderados.

Proyecto: Dine-de-one-nodo.
Materia: Programación III.

Contiene las clases Nodo y Grafo, así como la implementación
del algoritmo de Dijkstra mediante NetworkX.
"""

import math

import networkx as nx


class Nodo:
    """Representa un nodo y sus conexiones con otros nodos."""

    def __init__(self, nombre: str) -> None:
        """Inicializa un nodo con su nombre y vecinos."""
        self.nombre = nombre
        self.vecinos: dict[str, float] = {}

    def agregar_vecino(self, vecino: str, peso: float) -> None:
        """Agrega o actualiza la conexión con un vecino."""
        self.vecinos[vecino] = peso


class Grafo:
    """Representa una red de nodos con conexiones ponderadas."""

    def __init__(self) -> None:
        """Inicializa un grafo vacío y no dirigido."""
        self.nodos: dict[str, Nodo] = {}
        self.red = nx.Graph()

    def agregar_nodo(self, nombre: str) -> None:
        """Agrega un nodo al grafo si todavía no existe."""
        nombre = nombre.strip().upper()

        if not nombre:
            raise ValueError('El nombre no puede estar vacío.')

        self.nodos.setdefault(nombre, Nodo(nombre))
        self.red.add_node(nombre)

    def agregar_conexion(
        self, origen: str, destino: str, peso: float
    ) -> None:
        """Agrega una conexión bidireccional con peso positivo."""
        origen = origen.strip().upper()
        destino = destino.strip().upper()

        if not origen or not destino:
            raise ValueError('Los nombres no pueden estar vacíos.')

        try:
            peso = float(peso)

        except ValueError as error:
            raise ValueError('El peso debe ser numérico.') from error

        except TypeError as error:
            raise ValueError('El tipo de peso no es válido.') from error

        if not math.isfinite(peso) or peso <= 0:
            raise ValueError('El peso debe ser finito y positivo.')

        if origen == destino:
            raise ValueError('El origen y destino deben ser distintos.')

        self.agregar_nodo(origen)
        self.agregar_nodo(destino)

        self.nodos[origen].agregar_vecino(destino, peso)
        self.nodos[destino].agregar_vecino(origen, peso)

        self.red.add_edge(origen, destino, weight=peso)

    def dijkstra(
        self, inicio: str, destino: str
    ) -> tuple[float, list[str]]:
        """Calcula la ruta más corta y devuelve su costo total."""
        inicio = inicio.strip().upper()
        destino = destino.strip().upper()

        if inicio not in self.red or destino not in self.red:
            raise ValueError('Uno de los nodos no existe.')

        try:
            return nx.single_source_dijkstra(
                self.red,
                inicio,
                destino,
                weight='weight'
            )

        except nx.NetworkXNoPath:
            return float('inf'), []

        except nx.NodeNotFound as error:
            raise ValueError('No se encontró el nodo.') from error

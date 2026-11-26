
"""

Título: Proyecto FINAL. Persistencia Relacional con SQLite
Nombre: Jhonatan Enrique Diaz Campos
Fecha: 26 de Noviembre de 2026
Descripción: Creacion de nuestra pagina Streamlit de nodos
pero esta vez ya no es csv sinó DB

"""

import math

import networkx as nx


class Nodo:
    # Clase nodo, aqui es donde el nodo se crea

    def __init__(self, nombre: str) -> None:
        # Inicializa el nodo con su nombre y vecinos
        self.nombre = nombre
        self.vecinos: dict[str, float] = {}

    def agregar_vecino(self, vecino: str, peso: float) -> None:
        # Actualiza el nodo con su vecino
        self.vecinos[vecino] = peso


class Grafo:
    # Aqui se crea el grafo y las conecciones

    def __init__(self) -> None:
        # Aqui se define el grafo vacio
        self.nodos: dict[str, Nodo] = {}
        self.red = nx.Graph()

    def agregar_nodo(self, nombre: str) -> None:
        # Agrega un nodo al grafo si aun no existe
        nombre = nombre.strip().upper()

        if not nombre:
            raise ValueError('El nombre no puede estar vacío.')

        self.nodos.setdefault(nombre, Nodo(nombre))
        self.red.add_node(nombre)

    def agregar_conexion(
        self, origen: str, destino: str, peso: float
    ) -> None:
        # Agrega una direccion con peso positivo
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
        # Calcula la ruta más corta y devuelve su costo total.
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

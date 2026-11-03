# Clases para representar un grafo y ejecutar Dijkstra.

# Aqui definimos la clase nodo
class Nodo:
    # Inicializa el nombre y el diccionario de vecinos.
    def __init__(self, nombre: str) -> None:

        self.nombre: str = nombre
        self.vecinos: dict[str, float] = {}

    # Agrega o actualiza una conexión con otro nodo.
    def agregar_vecino(self, vecino: str, peso: float) -> None:

        self.vecinos[vecino] = peso


# Aqui definimos la clase grafo
class Grafo:
    def __init__(self) -> None:
        # Inicializa el diccionario de nodos del grafo.
        self.nodos: dict[str, Nodo] = {}

    def agregar_nodo(self, nombre: str) -> None:
        # Agrega un nodo si todavía no existe.
        if nombre not in self.nodos:
            self.nodos[nombre] = Nodo(nombre)

    def agregar_conexion(
        self, origen: str, destino: str, peso: float
    ) -> None:
        # Agrega una conexión bidireccional entre dos nodos.
        if peso < 0:
            raise ValueError("El peso no puede ser negativo.")

        if origen == destino:
            raise ValueError("El origen y destino deben ser distintos.")

        self.agregar_nodo(origen)
        self.agregar_nodo(destino)

        self.nodos[origen].agregar_vecino(destino, peso)
        self.nodos[destino].agregar_vecino(origen, peso)

    def dijkstra(
        self, inicio: str, destino: str
    ) -> tuple[float, list[str]]:
        # Calcula la distancia mínima y el camino entre dos nodos.
        if inicio not in self.nodos:
            raise ValueError(f"El nodo {inicio} no existe.")

        if destino not in self.nodos:
            raise ValueError(f"El nodo {destino} no existe.")

        distancias: dict[str, float] = {}
        anteriores: dict[str, str | None] = {}
        visitados: set[str] = set()

        for nombre in self.nodos:
            distancias[nombre] = float("inf")
            anteriores[nombre] = None

        distancias[inicio] = 0.0

        while len(visitados) < len(self.nodos):
            nodo_actual: str | None = None
            menor_distancia = float("inf")

            for nombre in self.nodos:
                if nombre not in visitados:
                    if distancias[nombre] < menor_distancia:
                        menor_distancia = distancias[nombre]
                        nodo_actual = nombre

            if nodo_actual is None:
                break

            if nodo_actual == destino:
                break

            visitados.add(nodo_actual)
            nodo = self.nodos[nodo_actual]

            for vecino, peso in nodo.vecinos.items():
                nueva_distancia = distancias[nodo_actual] + peso

                if nueva_distancia < distancias[vecino]:
                    distancias[vecino] = nueva_distancia
                    anteriores[vecino] = nodo_actual

        if distancias[destino] == float("inf"):
            return float("inf"), []

        camino: list[str] = []
        actual: str | None = destino

        while actual is not None:
            camino.append(actual)
            actual = anteriores[actual]

        camino.reverse()

        return distancias[destino], camino

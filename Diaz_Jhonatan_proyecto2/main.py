# Programa principal para gestionar una red de transporte.

import math

from grafo import Grafo
from io_handler import (
    cargar_grafo,
    guardar_conexion,
    solicitar_nodo,
    solicitar_peso,
)


def registrar_conexion(grafo: Grafo) -> None:
    # Solicita y guarda una nueva conexión de transporte.
    print("\nRegistra una nueva conexión")

    origen = solicitar_nodo("Nodo de partida: ")
    destino = solicitar_nodo("Nodo de llegada: ")
    peso = solicitar_peso()

    try:
        if origen == destino:
            raise ValueError(
                "El origen y destino no deben ser iguales."
            )

        guardar_conexion(origen, destino, peso)
        grafo.agregar_conexion(origen, destino, peso)

        print("La coneccion se registro con exito.")

    except ValueError as error:
        print(f"Validación: {error}")

    except OSError as error:
        print(f"No es posible encontrar tu coneccion: {error}")


def consultar_ruta(grafo: Grafo) -> None:
    # Calcula y muestra la ruta más corta entre dos nodos.
    print("\nConsulta tu ruta")

    if not grafo.nodos:
        print("No hay conexiones entre los nodos que dijiste D: .")
        return

    inicio = solicitar_nodo("Nodo de partida: ")
    destino = solicitar_nodo("Nodo de llegada: ")

    try:
        distancia, camino = grafo.dijkstra(inicio, destino)

        if math.isinf(distancia):
            print("No existe una ruta entre esos nodos.")
            return

        print(f"Ruta más corta: {' -> '.join(camino)}")
        print(f"Peso total: {distancia}")

    except ValueError as error:
        print(f"Validación: {error}")


def mostrar_conexiones(grafo: Grafo) -> None:
    # Muestra las conexiones registradas en el grafo.
    print("\nConexiones registradas:")

    if not grafo.nodos:
        print("No hay conexiones registradas.")
        return

    mostradas: set[frozenset[str]] = set()

    for nombre, nodo in grafo.nodos.items():
        for vecino, peso in nodo.vecinos.items():
            conexion = frozenset((nombre, vecino))

            if conexion not in mostradas:
                print(f"{nombre} <-> {vecino} | Peso: {peso}")
                mostradas.add(conexion)


def menu() -> None:
    # Ejecuta el menú principal de la aplicación.
    grafo = cargar_grafo()

    while True:
        print("\nRed de nodos")
        print("1. Registra un nuevo nodo")
        print("2. Consultar ruta más corta")
        print("3. Mostrar conexiones entre nodos1")
        print("4. Salir")

        opcion = input("\nSelecciona una opción: ").strip()

        if opcion == "1":
            registrar_conexion(grafo)

        elif opcion == "2":
            grafo = cargar_grafo()
            consultar_ruta(grafo)

        elif opcion == "3":
            grafo = cargar_grafo()
            mostrar_conexiones(grafo)

        elif opcion == "4":
            print("Programa finalizado.")
            return

        else:
            print("Opción no válida. Intenta nuevamente.")


if __name__ == "__main__":
    menu()

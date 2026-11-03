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
    print("\n--- REGISTRAR CONEXIÓN ---")

    origen = solicitar_nodo("Nodo origen: ")
    destino = solicitar_nodo("Nodo destino: ")
    peso = solicitar_peso()

    try:
        if origen == destino:
            raise ValueError(
                "El origen y destino deben ser distintos."
            )

        guardar_conexion(origen, destino, peso)
        grafo.agregar_conexion(origen, destino, peso)

        print("Conexión guardada correctamente.")

    except ValueError as error:
        print(f"Validación: {error}")

    except OSError as error:
        print(f"No fue posible guardar la conexión: {error}")


def consultar_ruta(grafo: Grafo) -> None:
    # Calcula y muestra la ruta más corta entre dos nodos.
    print("\n--- CONSULTAR RUTA ---")

    if not grafo.nodos:
        print("No hay conexiones registradas.")
        return

    inicio = solicitar_nodo("Nodo de inicio: ")
    destino = solicitar_nodo("Nodo de destino: ")

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
    print("\n--- CONEXIONES REGISTRADAS ---")

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
        print("\n=== RED DE TRANSPORTE ===")
        print("1. Registrar nueva conexión")
        print("2. Consultar ruta más corta")
        print("3. Mostrar conexiones")
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

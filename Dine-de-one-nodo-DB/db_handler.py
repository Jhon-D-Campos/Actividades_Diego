
"""
Módulo de persistencia de datos mediante SQLite.

Proyecto: Dine-de-one-nodo.
Materia: Programación III.

Gestiona la base de datos, las consultas JOIN, la migración
de registros y la preparación de tablas mediante pandas.
"""

import math
import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

from grafos import Grafo


ARCHIVO_DB = Path(__file__).resolve().parent / 'nodos.db'

ErrorIntegridad = sqlite3.IntegrityError
ErrorBaseDatos = sqlite3.DatabaseError

CONSULTA_CONEXIONES = """
    SELECT
        origen.nombre AS origen,
        destino.nombre AS destino,
        c.peso
    FROM conexiones AS c
    JOIN nodos AS origen
        ON c.id_origen = origen.id_nodo
    JOIN nodos AS destino
        ON c.id_destino = destino.id_nodo
    ORDER BY origen.nombre, destino.nombre
"""


def validar_nodo(nombre: str) -> str:
    """Limpia y valida el nombre de un nodo."""
    if not isinstance(nombre, str):
        raise ValueError('El nombre del nodo debe ser texto.')

    nombre = nombre.strip().upper()

    if not nombre:
        raise ValueError('El nombre del nodo no puede estar vacío.')

    return nombre


def validar_peso(entrada: float) -> float:
    """Comprueba que el peso sea numérico, finito y positivo."""
    try:
        peso = float(entrada)

    except ValueError as error:
        raise ValueError('El peso debe ser numérico.') from error

    except TypeError as error:
        raise ValueError('El tipo de peso no es válido.') from error

    if not math.isfinite(peso) or peso <= 0:
        raise ValueError('El peso debe ser finito y positivo.')

    return peso


def conectar(
    ruta: str | Path | None = None
) -> sqlite3.Connection:
    """Establece una conexión con SQLite."""
    ruta = ARCHIVO_DB if ruta is None else Path(ruta)

    conexion = sqlite3.connect(str(ruta), timeout=30)
    conexion.execute('PRAGMA foreign_keys = ON')

    return conexion


def crear_tablas(conexion: sqlite3.Connection) -> None:
    """Crea las tablas normalizadas de la base de datos."""
    conexion.execute("""
        CREATE TABLE IF NOT EXISTS nodos (
            id_nodo INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL UNIQUE
        )
    """)

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS conexiones (
            id_origen INTEGER NOT NULL,
            id_destino INTEGER NOT NULL,
            peso REAL NOT NULL CHECK(peso > 0),

            PRIMARY KEY (id_origen, id_destino),

            FOREIGN KEY (id_origen)
                REFERENCES nodos(id_nodo),

            FOREIGN KEY (id_destino)
                REFERENCES nodos(id_nodo),

            CHECK(id_origen < id_destino)
        )
    """)


def obtener_id(
    conexion: sqlite3.Connection, nombre: str
) -> int:
    """Registra un nodo si no existe y devuelve su identificador."""
    conexion.execute(
        'INSERT OR IGNORE INTO nodos(nombre) VALUES (?)',
        (nombre,)
    )

    resultado = conexion.execute(
        'SELECT id_nodo FROM nodos WHERE nombre = ?',
        (nombre,)
    ).fetchone()

    return resultado[0]


def insertar_conexion(
    conexion: sqlite3.Connection,
    origen: str,
    destino: str,
    peso: float
) -> None:
    """Inserta o actualiza una conexión bidireccional."""
    origen = validar_nodo(origen)
    destino = validar_nodo(destino)
    peso = validar_peso(peso)

    if origen == destino:
        raise ValueError('El origen y destino deben ser distintos.')

    id_origen = obtener_id(conexion, origen)
    id_destino = obtener_id(conexion, destino)

    id_origen, id_destino = sorted((id_origen, id_destino))

    conexion.execute("""
        INSERT INTO conexiones (
            id_origen, id_destino, peso
        )
        VALUES (?, ?, ?)
        ON CONFLICT(id_origen, id_destino)
        DO UPDATE SET peso = excluded.peso
    """, (id_origen, id_destino, peso))


def inicializar_db(ruta: str | Path | None = None) -> None:
    """Inicializa SQLite y migra la estructura anterior si existe."""
    with closing(conectar(ruta)) as conexion, conexion:
        conexion.execute('BEGIN IMMEDIATE')

        columnas = conexion.execute(
            'PRAGMA table_info(nodos)'
        ).fetchall()

        nombres = [columna[1] for columna in columnas]

        if nombres and 'id_nodo' not in nombres:
            nodos = conexion.execute(
                'SELECT nombre FROM nodos'
            ).fetchall()

            conexiones = conexion.execute("""
                SELECT origen, destino, peso
                FROM conexiones
            """).fetchall()

            conexion.execute('DROP TABLE conexiones')
            conexion.execute('DROP TABLE nodos')

            crear_tablas(conexion)

            for (nombre,) in nodos:
                obtener_id(conexion, validar_nodo(nombre))

            for origen, destino, peso in conexiones:
                insertar_conexion(
                    conexion, origen, destino, peso
                )

        else:
            crear_tablas(conexion)


def cargar_grafo(ruta: str | Path | None = None) -> Grafo:
    """Reconstruye el grafo utilizando los registros de SQLite."""
    inicializar_db(ruta)
    grafo = Grafo()

    with closing(conectar(ruta)) as conexion, conexion:
        conexion.execute('BEGIN')

        nodos = conexion.execute(
            'SELECT nombre FROM nodos ORDER BY nombre'
        ).fetchall()

        for (nombre,) in nodos:
            grafo.agregar_nodo(nombre)

        conexiones = conexion.execute(
            CONSULTA_CONEXIONES
        ).fetchall()

        for origen, destino, peso in conexiones:
            grafo.agregar_conexion(origen, destino, peso)

    return grafo


def guardar_nodo(
    nombre: str, ruta: str | Path | None = None
) -> None:
    """Guarda un nodo validado en la base de datos."""
    nombre = validar_nodo(nombre)
    inicializar_db(ruta)

    with closing(conectar(ruta)) as conexion, conexion:
        obtener_id(conexion, nombre)


def guardar_conexion(
    origen: str,
    destino: str,
    peso: float,
    ruta: str | Path | None = None
) -> None:
    """Guarda una conexión entre dos nodos."""
    inicializar_db(ruta)

    with closing(conectar(ruta)) as conexion, conexion:
        insertar_conexion(
            conexion, origen, destino, peso
        )


def obtener_tabla_nodos(
    ruta: str | Path | None = None
) -> pd.DataFrame:
    """Devuelve los nodos como una tabla de pandas."""
    inicializar_db(ruta)

    with closing(conectar(ruta)) as conexion:
        return pd.read_sql_query(
            'SELECT nombre AS Nodo FROM nodos ORDER BY nombre',
            conexion
        )


def obtener_tabla_conexiones(
    ruta: str | Path | None = None
) -> pd.DataFrame:
    """Devuelve las conexiones mediante una consulta JOIN."""
    inicializar_db(ruta)

    with closing(conectar(ruta)) as conexion:
        return pd.read_sql_query(
            CONSULTA_CONEXIONES, conexion
        )

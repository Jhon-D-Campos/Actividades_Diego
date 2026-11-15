"""Persistencia CSV con bloqueo entre procesos y reemplazo atómico."""
import csv
import os
import shutil
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
import pandas as pd
from grafo import Grafo

ARCHIVO_CSV = Path(__file__).resolve().parent / 'nodos.csv'
ARCHIVO_NODOS = ARCHIVO_CSV.with_name('nodos_existentes.csv')
ENCABEZADOS = ['Origen', 'Destino', 'Peso']

def validar_nodo(nombre):
    nombre = nombre.strip().upper()
    if not nombre:
        raise ValueError('El nombre del nodo no puede estar vacío.')
    return nombre


def validar_peso(entrada):
    import math
    try:
        peso = float(entrada)
    except (ValueError, TypeError):
        raise ValueError('El peso debe ser numérico.') from None
    if not math.isfinite(peso) or peso < 0:
        raise ValueError('El peso debe ser finito y no negativo.')
    return peso


def leer_csv(ruta):
    if not Path(ruta).exists():
        return [], []
    df = pd.read_csv(ruta, dtype=str, keep_default_na=False, encoding='utf-8-sig')
    if list(df.columns) != ENCABEZADOS:
        raise ValueError('El CSV debe tener encabezados Origen,Destino,Peso.')
    filas, avisos = [], []
    for i, row in df.iterrows():
        try:
            a, b = validar_nodo(row.Origen), validar_nodo(row.Destino)
            p = validar_peso(row.Peso)
            if a == b:
                raise ValueError('Conexión al mismo nodo.')
            filas.append((a, b, p))
        except ValueError as error:
            avisos.append(f'Fila {i + 2} omitida: {error}')
    return filas, avisos


@contextmanager
def bloqueo_archivo(ruta):
    """El sistema operativo libera el bloqueo incluso si termina el proceso."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with Path(str(ruta) + '.lock').open('a+b') as archivo:
        archivo.seek(0, 2)
        if archivo.tell() == 0:
            archivo.write(b'0')
            archivo.flush()
        limite = time.monotonic() + 30
        while True:
            try:
                archivo.seek(0)
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(archivo.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(archivo, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= limite:
                    raise OSError('El CSV está ocupado. Intenta de nuevo.')
                time.sleep(0.05)
        try:
            yield
        finally:
            archivo.seek(0)
            if os.name == 'nt':
                msvcrt.locking(archivo.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(archivo, fcntl.LOCK_UN)


def escribir_atomico(ruta, columnas, filas):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', newline='', encoding='utf-8-sig',
                dir=ruta.parent, delete=False, suffix='.tmp') as archivo:
            temporal = Path(archivo.name)
            writer = csv.writer(archivo)
            writer.writerow(columnas)
            writer.writerows(filas)
            archivo.flush()
            os.fsync(archivo.fileno())
        os.replace(temporal, ruta)
    finally:
        if temporal is not None and temporal.exists():
            temporal.unlink()


def ruta_nodos(ruta):
    ruta = Path(ruta)
    return ARCHIVO_NODOS if ruta == ARCHIVO_CSV else ruta.with_name(ruta.stem + '_existentes.csv')


def leer_nombres(ruta):
    if not ruta.exists():
        return set()
    tabla = pd.read_csv(ruta, dtype=str, keep_default_na=False, encoding='utf-8-sig')
    if list(tabla.columns) != ['Nombre']:
        raise ValueError('El CSV de nodos debe tener el encabezado Nombre.')
    return {validar_nodo(nombre) for nombre in tabla.Nombre}


def cargar_grafo(ruta=None):
    ruta = ARCHIVO_CSV if ruta is None else Path(ruta)
    g = Grafo()
    with bloqueo_archivo(ruta):
        filas, _ = leer_csv(ruta)
        nombres = leer_nombres(ruta_nodos(ruta))
    for nombre in sorted(nombres):
        g.agregar_nodo(nombre)
    for a, b, peso in filas:
        g.agregar_conexion(a, b, peso)
    return g


def guardar_nodo(nombre, ruta=None):
    nombre = validar_nodo(nombre)
    ruta = ARCHIVO_CSV if ruta is None else Path(ruta)
    with bloqueo_archivo(ruta):
        destino = ruta_nodos(ruta)
        nombres = leer_nombres(destino)
        nombres.add(nombre)
        escribir_atomico(destino, ['Nombre'], [(n,) for n in sorted(nombres)])


def guardar_conexion(origen, destino, peso, ruta=None):
    a, b = validar_nodo(origen), validar_nodo(destino)
    peso = validar_peso(peso)
    if a == b:
        raise ValueError('El origen y destino deben ser distintos.')
    ruta = ARCHIVO_CSV if ruta is None else Path(ruta)
    with bloqueo_archivo(ruta):
        filas, _ = leer_csv(ruta)
        conexiones = {tuple(sorted((x,y))): p for x,y,p in filas}
        conexiones[tuple(sorted((a,b)))] = peso
        # Conserva los bytes originales antes de normalizar duplicados/filas inválidas.
        respaldo = Path(str(ruta) + '.bak')
        if ruta.exists() and not respaldo.exists():
            shutil.copy2(ruta, respaldo)
        escribir_atomico(ruta, ENCABEZADOS,
            [(x,y,p) for (x,y),p in sorted(conexiones.items())])


def avisos_importacion():
    with bloqueo_archivo(ARCHIVO_CSV):
        _, avisos = leer_csv(ARCHIVO_CSV)
    if Path(str(ARCHIVO_CSV) + '.bak').exists():
        avisos.append('Existe nodos.csv.bak: respaldo anterior a la primera escritura. Las filas inválidas se omiten al guardar y los duplicados se consolidan.')
    return avisos


def solicitar_nodo(mensaje):
    while True:
        try:
            return validar_nodo(input(mensaje))
        except ValueError as error:
            print(error)


def solicitar_peso():
    while True:
        try:
            return validar_peso(input('Peso de la conexión: '))
        except ValueError as error:
            print(error)

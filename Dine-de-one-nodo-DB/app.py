
"""

Título: Proyecto FINAL. Persistencia Relacional con SQLite
Nombre: Jhonatan Enrique Diaz Campos
Fecha: 26 de Noviembre de 2026
Descripción: Creacion de nuestra pagina Streamlit de nodos
pero esta vez ya no es csv sinó DB

"""

import math
import threading
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import streamlit as st

from db_handler import (
    ARCHIVO_DB,
    ErrorIntegridad,
    ErrorBaseDatos,
    cargar_grafo,
    guardar_conexion,
    obtener_tabla_nodos,
    obtener_tabla_conexiones,
)
from grafos import Grafo


DIRECTORIO = Path(__file__).resolve().parent

st.set_page_config(
    page_title='Find the one piece',
    layout='wide'
)


@st.cache_resource
def bloqueo() -> threading.RLock:
    # Evita conflictos al visualizar el grafo
    return threading.RLock()


def mostrar_imagen(
    archivo: str,
    comentario: str,
    ancho: int | str = 'stretch'
) -> None:
    # Muestra la imagen local si el archivo existe
    ruta = DIRECTORIO / archivo

    if ruta.exists():
        st.image(
            str(ruta),
            caption=comentario,
            width=ancho
        )


def actualizar_datos() -> bool:
    # Sincroniza los datos con sqlite
    try:
        grafo = cargar_grafo()
        tabla_nodos = obtener_tabla_nodos()
        tabla_conexiones = obtener_tabla_conexiones()

    except ErrorIntegridad as error:
        st.error(f'Error de integridad: {error}')
        return False

    except ErrorBaseDatos as error:
        st.error(f'Error de almacenamiento: {error}')
        return False

    except ValueError as error:
        st.warning(f'Datos inválidos: {error}')
        return False

    st.session_state['grafo'] = grafo
    st.session_state['tabla_nodos'] = tabla_nodos
    st.session_state['tabla_conexiones'] = tabla_conexiones
    st.session_state['camino'] = []
    st.session_state['distancia'] = None

    return True


def guardar(origen: str, destino: str, peso: float) -> None:
    # Valida y guarda la conexion en la base de datos
    origen = origen.strip()
    destino = destino.strip()

    if not origen or not destino:
        st.warning('Debes completar ambos nombres.')
        return

    if origen.upper() == destino.upper():
        st.warning('El origen y destino deben ser distintos.')
        return

    if not math.isfinite(peso) or peso <= 0:
        st.warning('El peso debe ser mayor que cero.')
        return

    try:
        guardar_conexion(origen, destino, peso)

    except ValueError as error:
        st.warning(str(error))

    except ErrorIntegridad as error:
        st.error(f'Error de integridad: {error}')

    except ErrorBaseDatos as error:
        st.error(f'No se pudo guardar la conexión: {error}')

    else:
        if actualizar_datos():
            st.session_state['mensaje'] = (
                'Datos guardados en la base de datos.'
            )
            st.rerun()
        else:
            st.session_state.pop('grafo', None)
            st.warning(
                'La conexión se guardó, pero falta actualizar los datos.'
            )
            st.stop()


def consultar_ruta(
    grafo: Grafo,
    origen: str,
    destino: str
) -> None:
    # Calcula y almacena la ruta mas corta
    st.session_state['camino'] = []
    st.session_state['distancia'] = None

    try:
        distancia, camino = grafo.dijkstra(origen, destino)

    except ValueError as error:
        st.warning(str(error))

    except nx.NetworkXException as error:
        st.error(f'No se pudo calcular la ruta: {error}')

    else:
        if math.isinf(distancia):
            st.warning('No existe una ruta entre esos nodos.')
        else:
            st.session_state['camino'] = camino
            st.session_state['distancia'] = distancia


def visualizar_grafo(
    grafo: Grafo,
    camino: list[str]
) -> None:
    # Dibuja el grafo y señala la ruta mas corta
    with bloqueo():
        fig, ax = plt.subplots(figsize=(10, 6))

        try:
            pos = nx.spring_layout(
                grafo.red,
                seed=42,
                weight=None
            )

            nx.draw_networkx(
                grafo.red,
                pos,
                ax=ax,
                node_color='#b8def5',
                node_size=900
            )

            etiquetas = {
                (a, b): f'{datos["weight"]:g}'
                for a, b, datos in grafo.red.edges(data=True)
            }

            nx.draw_networkx_edge_labels(
                grafo.red,
                pos,
                ax=ax,
                edge_labels=etiquetas
            )

            if camino:
                aristas = list(zip(camino, camino[1:]))

                nx.draw_networkx_edges(
                    grafo.red,
                    pos,
                    ax=ax,
                    edgelist=aristas,
                    edge_color='#e67922',
                    width=4
                )

            ax.axis('off')
            st.pyplot(fig)

        except ValueError as error:
            st.error(f'Error de visualización: {error}')

        except nx.NetworkXException as error:
            st.error(f'Error en el grafo: {error}')

        finally:
            plt.close(fig)


# Título e imagen principal.
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    mostrar_imagen(
        'YoHaciendoLaActividad.jpg',
        'Nosotros haciendo la actividad',
        250
    )

st.title('Find the one piece')
st.caption(
    'Grafo bidireccional. Los pesos pertenecen a las conexiones.'
)


# Inicialización de los datos de la sesión.
if 'grafo' not in st.session_state:
    if not actualizar_datos():
        st.stop()

if 'mensaje' in st.session_state:
    st.success(st.session_state.pop('mensaje'))

grafo = st.session_state['grafo']
nodos = sorted(grafo.nodos)


# Barra lateral y menú de navegación.
with st.sidebar:
    mostrar_imagen(
        'PoseCamaron.jpg',
        'Asi nos vemos haciendo la actividad'
    )

    st.header('Nodos existentes')

    st.dataframe(
        st.session_state['tabla_nodos'],
        hide_index=True
    )

    seccion = st.radio(
        'Apartado',
        [
            'Visualizar grafo',
            'Crear conexión',
            'Consultar camino'
        ]
    )

    if st.button('Actualizar datos'):
        if actualizar_datos():
            st.rerun()

    st.caption(f'Base de datos: {ARCHIVO_DB.name}')

    mostrar_imagen(
        'download.jpg',
        'Yo al ver la actividad del Profe Diego, '
        'y que me toca hacerla a mi'
    )


# Formulario para registrar conexiones.
if seccion == 'Crear conexión':
    st.subheader('Crear o actualizar conexión')

    st.caption(
        'Puedes escribir nodos nuevos. '
        'Repetir una pareja actualiza su peso.'
    )

    with st.form('conexion'):
        origen = st.text_input('Origen')
        destino = st.text_input('Destino')

        peso = st.number_input(
            'Peso',
            min_value=0.01,
            value=1.0,
            step=0.01
        )

        enviar = st.form_submit_button('Guardar conexión')

    if enviar:
        guardar(origen, destino, peso)


# Formulario para consultar la ruta más corta.
elif seccion == 'Consultar camino':
    st.subheader('Camino más corto')

    if nodos:
        with st.form('ruta'):
            origen = st.selectbox(
                'Nodo de partida',
                nodos
            )

            destino = st.selectbox(
                'Nodo de llegada',
                nodos,
                index=min(1, len(nodos) - 1)
            )

            enviar = st.form_submit_button('Consultar')

        if enviar:
            consultar_ruta(grafo, origen, destino)

        camino = st.session_state['camino']
        distancia = st.session_state['distancia']

        if camino and distancia is not None:
            st.success(' → '.join(camino))
            st.metric('Peso total', f'{distancia:g}')

    else:
        st.info('Primero crea alguna conexión.')


# Representación gráfica de los nodos.
st.subheader('Grafo ponderado')

cantidad = grafo.red.number_of_edges()

st.caption(
    f'{len(nodos)} nodos · {cantidad} conexiones'
)

if nodos:
    visualizar_grafo(
        grafo,
        st.session_state['camino']
    )
else:
    st.info('El grafo está vacío.')


# Tabla de conexiones almacenadas.
st.subheader('Conexiones registradas')

st.dataframe(
    st.session_state['tabla_conexiones'],
    hide_index=True
)


# Descarga de la base de datos.
if ARCHIVO_DB.exists():
    try:
        contenido = ARCHIVO_DB.read_bytes()

    except PermissionError as error:
        st.error(f'Permiso denegado: {error}')

    except OSError as error:
        st.error(f'No se pudo leer el archivo: {error}')

    else:
        st.download_button(
            'Descargar base de datos DB',
            data=contenido,
            file_name='nodos.db',
            mime='application/octet-stream'
        )

st.caption(
    'Las conexiones y los nodos aislados se guardan en nodos.db.'
)


# Video original del proyecto.
url_youtube = (
    'https://www.youtube.com/watch?v=WzmB4K4_-_0'
    '&list=RDTVEro-Ch9IY&index=2'
)

st.video(url_youtube, autoplay=True)

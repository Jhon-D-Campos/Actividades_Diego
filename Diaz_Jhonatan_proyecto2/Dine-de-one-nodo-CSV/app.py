import math
import threading
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import streamlit as st
from io_handler import cargar_grafo, guardar_conexion, avisos_importacion, ARCHIVO_CSV, ARCHIVO_NODOS
matplotlib.use('Agg')

# Titulo de la pagina y layout
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image(r'C:\Users\Usuario\Desktop\Uni\Cuarto\Proyectos_y_actividades\ProeyctosDiego\Dijkstra\Diaz_Jhonatan_proyecto2\Dine-de-one-nodo-CSV\YoHaciendoLaActividad.jpg',
             caption='Nosotros haciendo la actividad', width=250)

st.set_page_config(page_title='Find the one piece', layout='wide')
st.title('Find the one piece')
st.caption('Grafo bidireccional. Los pesos pertenecen a las conexiones.')

# Esto es para  evitar que el grado se elimine
@st.cache_resource
def bloqueo():
    return threading.RLock()


# Try except para cargar el grafo y avisos de importación
try:
    grafo = cargar_grafo()
    avisos = avisos_importacion()
except (OSError, ValueError, pd.errors.ParserError) as error:
    st.error(f'No se pudo cargar el almacenamiento: {error}')
    st.stop()

if 'mensaje' in st.session_state:
    st.success(st.session_state.pop('mensaje'))
nodos = sorted(grafo.nodos)

# Sidebar con nodos existentes y secciones
with st.sidebar:
    st.image(r'C:\Users\Usuario\Desktop\Uni\Cuarto\Proyectos_y_actividades\ProeyctosDiego\Dijkstra\Diaz_Jhonatan_proyecto2\Dine-de-one-nodo-CSV\PoseCamaron.jpg',
             caption='Asi nos vemos haciendo la actividad', width='stretch')
    st.header('Nodos existentes')
    st.dataframe(pd.DataFrame({'Nodo': nodos}), hide_index=True)
    seccion = st.radio(
        'Apartado', [
            'Visualizar grafo', 'Crear conexión', 'Consultar camino'])
    st.button('Actualizar datos')
    st.caption(f'Conexiones: {ARCHIVO_CSV}')
    st.caption(f'Nodos aislados: {ARCHIVO_NODOS}')
    st.image(r'C:\Users\Usuario\Desktop\Uni\Cuarto\Proyectos_y_actividades\ProeyctosDiego\Dijkstra\Diaz_Jhonatan_proyecto2\Dine-de-one-nodo-CSV\download.jpg',
             caption='Yo al ver la actividad del Profe Diego, y que me toca hacerla a mi', width='stretch')
if avisos:
    with st.expander('Avisos del CSV'):
        for aviso in avisos:
            st.warning(aviso)

# Función para guardar datos y mostrar errores
def guardar(accion):
    try:
        accion()
    except (ValueError, OSError) as error:
        st.error(str(error))
    else:
        st.session_state['mensaje'] = 'Datos guardados en disco.'
        st.rerun()


# Variable para almacenar el camino más corto
camino = []

if seccion == 'Crear conexión':
    st.subheader('Crear o actualizar conexión')
    st.caption(
        'Puedes escribir nodos nuevos. Repetir una pareja actualiza su peso.')
    with st.form('conexion'):
        a = st.text_input('Origen')
        b = st.text_input('Destino')
        peso = st.number_input('Peso', min_value=0.0, value=1.0)
        enviar = st.form_submit_button('Guardar conexión')
    if enviar:
        guardar(lambda: guardar_conexion(a, b, peso))

# Sección para consultar el camino más corto
elif seccion == 'Consultar camino':
    st.subheader('Camino más corto')
    if nodos:
        with st.form('ruta'):
            a = st.selectbox('Nodo de partida', nodos)
            b = st.selectbox(
                'Nodo de llegada', nodos, index=min(
                    1, len(nodos) - 1))
            enviar = st.form_submit_button('Consultar')
        if enviar:
            distancia, camino = grafo.dijkstra(a, b)
            if math.isinf(distancia):
                st.warning('No existe una ruta entre esos nodos.')
            else:
                st.success(' → '.join(camino))
                st.metric('Peso total', f'{distancia:g}')
    else:
        st.info('Primero crea algún nodo.')

# Visualización del grafo
st.subheader('Grafo ponderado')
st.caption(f'{len(nodos)} nodos · {grafo.red.number_of_edges()} conexiones')
if nodos:
    with bloqueo():
        fig, ax = plt.subplots(figsize=(10, 6))
        try:
            pos = nx.spring_layout(grafo.red, seed=42, weight=None)
            nx.draw_networkx(
                grafo.red,
                pos,
                ax=ax,
                node_color='#b8def5',
                node_size=900)
            nx.draw_networkx_edge_labels(grafo.red, pos, ax=ax,
                                         edge_labels={(a, b): f'{d["weight"]: g}' for a, b, d in grafo.red.edges(data=True)})
            if camino:
                nx.draw_networkx_edges(grafo.red, pos, ax=ax, edgelist=list(
                    zip(camino, camino[1:])), edge_color='#e67922', width=4)
            ax.axis('off')
            st.pyplot(fig)
        finally:
            plt.close(fig)

# Tabla de conexiones y botón de descarga
else:
    st.info('El grafo está vacío.')
tabla = pd.DataFrame([(a, b, d['weight']) for a, b, d in grafo.red.edges(
    data=True)], columns=['Origen', 'Destino', 'Peso'])
st.dataframe(tabla, hide_index=True)
st.download_button(
    'Descargar conexiones CSV',
    tabla.to_csv(
        index=False).encode('utf-8-sig'),
    'conexiones.csv',
    'text/csv')
st.caption('El CSV no incluye nodos aislados. Para un respaldo completo, conserva nodos.csv y nodos_existentes.csv.')

url_youtuebe = 'https://www.youtube.com/watch?v=WzmB4K4_-_0&list=RDTVEro-Ch9IY&index=2'
st.video(url_youtuebe, autoplay=True)

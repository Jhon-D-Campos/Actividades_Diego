# Dine de one nodo — versión CSV

Requiere Python 3.10 o posterior. Descomprime el ZIP en una carpeta y ejecuta desde ella:

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m streamlit run app.py
```

Si ya instalaste las dependencias, basta el último comando. La consola sigue disponible con `.\.venv\Scripts\python main.py`.

## Archivos de datos

- `nodos.csv`: conexiones con las columnas originales `Origen,Destino,Peso`.
- `nodos_existentes.csv`: nombres de nodos creados individualmente, con encabezado `Nombre`. Se crea automáticamente al guardar el primer nodo aislado. El grafo reúne estos nombres con los extremos de las conexiones.
- `nodos.csv.bak`: respaldo de las conexiones antes de la primera modificación. No se sobrescribe en cada guardado.
- Los archivos `.lock` coordinan los accesos entre procesos. Es normal que permanezcan en la carpeta; no son datos del grafo.

Los archivos se encuentran junto a `io_handler.py`, independientemente de la carpeta desde donde abras la terminal. Si quieres usar tu CSV actual, copia tu `nodos.csv` a esa ubicación antes de iniciar. Haz primero un respaldo de tus datos. Se conserva el CSV original incluido en la conversación.

## Funcionamiento

El sidebar lista los nodos. Puedes crear nodos aislados, crear nodos conectados con peso, registrar conexiones y consultar caminos mínimos con peso total. El grafo es no dirigido; las conexiones se resaltan al consultar un camino.

Los nombres se convierten a mayúsculas y se recortan. No se permiten nombres vacíos ni conexiones de un nodo consigo mismo. Los pesos deben ser finitos y no negativos; cero está permitido. Repetir una pareja, incluso invertida, actualiza su peso.

Cada guardado bloquea el archivo entre procesos y reemplaza el CSV mediante un temporal en el mismo directorio. Los cambios se leen de nuevo en cada ejecución de Streamlit; usa Actualizar datos para ver cambios de otros usuarios. No edites el CSV simultáneamente con Excel: Excel no respeta el bloqueo de la app y puede impedir el reemplazo.

## Compatibilidad con los originales

Se mantienen las funciones públicas de `grafo.py` y `io_handler.py` usadas por `main.py`. `app.py` reemplaza la demostración original, que tenía un error de sintaxis. NetworkX calcula las rutas y pandas lee y muestra datos.

El CSV original contiene `P,A,hola`: se omite con aviso porque el peso no es numérico. A–L está repetido: prevalece el último peso, 5. La ruta A–C–D tiene peso total 3. Al guardar una conexión se consolidan duplicados y se omiten filas inválidas; el contenido anterior queda en `nodos.csv.bak`.

Esta versión no lee ni modifica SQLite. Si creaste datos en la versión anterior y solo están en `nodos.sqlite3`, no aparecerán automáticamente: conserva esa base y exporta sus datos antes de cambiar de versión. Los cambios que ya estaban en tu CSV sí se cargan directamente.

## Persistencia y respaldos

Cerrar el navegador, detener Streamlit y reiniciar el equipo conserva los datos mientras los CSV estén en un disco persistente. Respalda `nodos.csv` y `nodos_existentes.csv` con la app detenida. El botón de descarga exporta únicamente conexiones.

Streamlit Community Cloud no garantiza conservar archivos locales entre reinicios o despliegues. Cambiar SQLite por CSV no elimina esa limitación. Para durabilidad en ese host hace falta almacenamiento externo; en un servidor propio puedes usar un disco o volumen persistente.
Referencia: https://docs.streamlit.io/develop/concepts/connections/connecting-to-data

## Verificación

```powershell
.\.venv\Scripts\python -m unittest -v test_proyecto
```

La prueba incluida comprueba grafo, validación y persistencia entre procesos usando copias temporales del CSV. En el entorno de entrega se comprobó la sintaxis y se verificó la capa CSV: actualización de conexiones, nodos aislados, respaldo, validación y lectura desde otro proceso. La prueba completa de Streamlit/NetworkX no se ejecutó porque NetworkX no está disponible.

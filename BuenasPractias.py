"""
Título: Aplicación de buenas practicas en Python - Unidad 2
Nombre: Jhonatan Enrique Diaz Campos
Fecha: 29 de Octubre de 2026
Descripción: Aplicación de buenas prácticas en el desarrollo de código en Python, incluyendo el uso de tipado, manejo de errores y documentación.
"""

# Función para validar el nombre de una persona
def valida_nombre(nombre: str) -> str:
    nombre = nombre.strip()
    if nombre == "":
        raise ValueError("El nombre no puede estar vacío")
    if not nombre.replace(" ", "").isalpha():
        raise ValueError("El nombre solo puede contener letras")
    return nombre

# Función para validar la edad de una persona
def valida_edad(edad: int) -> int:

    if edad < 18:
        raise ValueError("La persona debe tener al menos 18 años.")
    return edad


lista_cosas = ["Coca", "Papas", "Servilletas"]


# Función para obtener el nombre del usuario con validación
def get_nombre() -> str:
    while True:
        try:
            nombre = valida_nombre(input("Dame tu nombre: "))
        except ValueError as error:
            print(f"Validación: {error}")
        else:
            return nombre

# Función para obtener la edad del usuario con validación
def get_edad() -> int:
    while True:
        try:
            edad = int(input("Dame tu edad: "))
            return valida_edad(edad)
        except ValueError as error:
            print(f"Validación: {error}")

# Función para obtener la elección de traje del usuario con validación
def get_traje(lista_cosas: list[str]) -> str:
    while True:
        print("\n¿Qué cosa llevarás?")
        for numero, cosa in enumerate(lista_cosas, start=1):
            print(f"{numero}. {cosa}")

        try:
            seleccion = int(input("Selecciona una opción: "))
            traje = lista_cosas[seleccion - 1]
        except (ValueError, IndexError):
            print("Validación: selecciona una opción válida.")
        else:
            return traje

# Función para mostrar la información del usuario
def mostrar_informacion(nombre: str, edad: int, traje: str) -> None:
    
    print(f"Nombre: {nombre}")
    print(f"Edad: {edad}")
    print(f"Cosa que llevará: {traje}")

# Función principal del programa que maneja el menú y la interacción con el usuario
def menu() -> None:
    while True:
    
        print("1. Registrar información")
        print("2. Salir")
     
        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            nombre = get_nombre()
            edad = get_edad()
            traje = get_traje(lista_cosas)
            mostrar_informacion(nombre, edad, traje)
        elif opcion == "2" or opcion.lower() == "salir":
            print("Programa finalizado.")
            return
        else:
            print("Opción no válida. Intenta nuevamente.")


if __name__ == "__main__":
    menu()

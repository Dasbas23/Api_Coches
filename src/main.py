# -*- coding: utf-8 -*-
"""
API REST para gestionar una colección de coches.

Este script utiliza Flask para crear una API que permite realizar operaciones
CRUD (Crear, Leer, Actualizar, Borrar) sobre una base de datos SQLite
que almacena información de coches.
"""
import sqlite3
from flask import Flask, jsonify, request

# Inicialización de la aplicación Flask
app = Flask(__name__)


def get_db_connection():
    """
    Establece una conexión con la base de datos SQLite.

    La conexión está configurada para devolver filas que se pueden acceder
    por nombre de columna (como un diccionario).

    :return: Objeto de conexión a la base de datos.
    """
    conn = sqlite3.connect('database.db')
    # Permite acceder a las columnas por su nombre.
    conn.row_factory = sqlite3.Row
    return conn


# --- Rutas de la API ---

@app.route("/")
def hola_mundo():
    """Ruta de bienvenida a la API."""
    return "Bienvenido a mi API de Coches"


@app.route("/marcas")
def marcas():
    """Ruta de ejemplo estática."""
    return "Aqui irán las marcas de coches"


@app.route("/api/coches", methods=['GET'])
def get_all_coches():
    """
    Obtiene la lista completa de todos los coches de la base de datos.

    :return: Respuesta JSON con una lista de todos los coches y código de estado 200 (OK).
    """
    conn = get_db_connection()
    coches_db = conn.execute('SELECT * FROM coches').fetchall()
    conn.close()

    # Convierte las filas de la base de datos (sqlite3.Row) a una lista de diccionarios.
    coches_lista = [dict(coche) for coche in coches_db]

    return jsonify(coches_lista), 200


@app.route("/api/coches/<int:coche_id>", methods=['GET'])
def get_coche_by_id(coche_id):
    """
    Obtiene un único coche por su ID.

    :param coche_id: El ID del coche a buscar.
    :return: Respuesta JSON con los datos del coche y código 200 (OK),
             o un error 404 (Not Found) si el coche no existe.
    """
    conn = get_db_connection()
    # Se usa fetchone() porque esperamos un único resultado.
    coche_db = conn.execute('SELECT * FROM coches WHERE id = ?', (coche_id,)).fetchone()
    conn.close()

    if coche_db is None:
        return jsonify({'Error': 'Coche no encontrado'}), 404

    return jsonify(dict(coche_db)), 200


@app.route("/api/coches", methods=['POST'])
def create_coche():
    """
    Crea un nuevo coche en la base de datos.

    Espera un cuerpo de solicitud JSON con 'marca', 'modelo' y 'anio'.

    :return: Respuesta JSON con un mensaje de éxito, el ID del nuevo coche y código 201 (Created),
             o un error 400 (Bad Request) si los datos son incompletos.
    """
    datos_nuevos = request.get_json()

    # Validación de datos de entrada.
    if not datos_nuevos or "marca" not in datos_nuevos or "modelo" not in datos_nuevos or "anio" not in datos_nuevos:
        return jsonify({"Error": "Datos incompletos. Se requiere marca, modelo y anio."}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO coches(marca, modelo, anio) VALUES (?, ?, ?)',
                (datos_nuevos['marca'], datos_nuevos['modelo'], datos_nuevos['anio']))

    # Obtenemos el ID del último registro insertado.
    last_id = cur.lastrowid

    conn.commit()
    conn.close()

    return jsonify({'mensaje': 'Se ha agregado el nuevo coche exitosamente', 'id': last_id}), 201


@app.route("/api/coches/<int:coche_id>", methods=['DELETE'])
def delete_coche(coche_id):
    """
    Elimina un coche de la base de datos por su ID.

    :param coche_id: El ID del coche a eliminar.
    :return: Respuesta JSON con un mensaje de éxito y código 200 (OK),
             o un error 404 (Not Found) si el coche no existía.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM coches WHERE id = ?', (coche_id,))
    conn.commit()

    # Comprobamos si la operación afectó a alguna fila.
    if cur.rowcount == 0:
        conn.close()
        return jsonify({'Error': 'Coche no encontrado, no se pudo eliminar'}), 404

    conn.close()
    return jsonify({"mensaje": "Coche eliminado exitosamente"}), 200


@app.route("/api/coches/<int:coche_id>", methods=['PUT'])
def update_coche(coche_id):
    """
    Actualiza los datos de un coche existente por su ID.

    Permite actualizaciones parciales. El cuerpo de la solicitud JSON puede
    contener uno o más campos a actualizar ('marca', 'modelo', 'anio').

    :param coche_id: El ID del coche a actualizar.
    :return: Respuesta JSON con un mensaje de éxito y código 200 (OK),
             o un error 404 (Not Found) si el coche no existe,
             o un error 400 (Bad Request) si se envían campos inválidos.
    """
    datos_update = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()

    # 1. BUSCAR el recurso. Es lo PRIMERO que hacemos.
    coche_actual = cur.execute('SELECT * FROM coches WHERE id = ?', (coche_id,)).fetchone()

    # 2. VALIDAR si el recurso existe.
    if coche_actual is None:
        conn.close()
        return jsonify({'Error': 'Coche no encontrado'}), 404

    # 3. VALIDAR los datos de entrada (las claves del JSON).
    cur.execute("SELECT * FROM coches LIMIT 1")
    campos_disponibles = [description[0] for description in cur.description]
    for key in datos_update.keys():
        if key not in campos_disponibles:
            conn.close()
            return jsonify({'Error': f"El campo '{key}' es inválido"}), 400

    # 4. FUSIONAR los datos viejos con los nuevos para permitir actualizaciones parciales.
    marca_final = datos_update.get('marca', coche_actual['marca'])
    modelo_final = datos_update.get('modelo', coche_actual['modelo'])
    anio_final = datos_update.get('anio', coche_actual['anio'])

    # 5. EJECUTAR la actualización.
    cur.execute('UPDATE coches SET marca = ?, modelo = ?, anio = ? WHERE id = ?',
                (marca_final, modelo_final, anio_final, coche_id))
    conn.commit()
    conn.close()

    return jsonify({'mensaje': 'Se ha actualizado el coche exitosamente', 'id': coche_id}), 200


# --- Punto de entrada para ejecutar la aplicación ---
if __name__ == '__main__':
    # El modo debug se activa para que el servidor se reinicie con cada cambio.
    # No usar en producción.!!!!
    app.run(debug=True)

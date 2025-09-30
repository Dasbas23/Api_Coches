import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
# Datos de ejemplo: una lista de coches


def get_db_connection():
    """Función para conectarse a la base de datos."""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row # Esto nos permite acceder a las columnas por nombre
    return conn

# Definimos la primera "ruta" o "endpoint"
@app.route("/")
def hola_mundo():
    return "Bienvenido a mi API de Coches"


@app.route("/marcas")
def marcas():
    return "Aqui irán las marcas de coches"


@app.route("/api/coches", methods=['GET'])
def get_coche():
    conn = get_db_connection()
    # Ejecutamos la consulta y obtenemos todos los resultados
    coches_db = conn.execute('SELECT * FROM coches').fetchall()
    conn.close()

    # Convertimos los resultados de la BD a una lista de diccionarios
    coches_lista = []
    for coche in coches_db:
        coches_lista.append(dict(coche))

    return jsonify(coches_lista),200



@app.route("/api/coches/<int:coche_id>", methods=['GET'])
def get_coche_filtro(coche_id):
    conn = get_db_connection()
    coche_db = conn.execute('SELECT * FROM coches WHERE id = ?',(coche_id,)).fetchone()
    conn.close()

    if coche_db is None:
        return jsonify({'Error': 'Coche no encontrado'}), 404

    return jsonify(dict(coche_db)),200



# Endpoint para crear un nuevo coche
@app.route("/api/coches", methods=['POST'])
def create_coche():
    # Objeto JSON enviado en la solicitud
    new_coche_data = request.get_json()

    # Validamos que el objeto tenga los campos necesarios
    if not new_coche_data or not "marca" in new_coche_data or not "modelo" in new_coche_data or not "anio" in new_coche_data:
        return jsonify({"error": "Datos incompletos"}), 400  # Bad Request

    # Creamos nuevo coche
    new_coche = {
        "id": coches[-1]["id"] + 1 if coches else 1,  # Asignamos un nuevo ID
        "marca": new_coche_data["marca"],
        "modelo": new_coche_data["modelo"],
        "anio": new_coche_data.get("anio", "Desconocido")  # Valor por defecto si no se proporciona
    }
    coches.append(new_coche)  # Añadimos el nuevo coche a la lista
    # Devolvemos el coche recién creado y el código 201 Created
    return jsonify(new_coche), 201

#Endpoint para eliminar un coche
@app.route("/api/coches/<int:coche_id>", methods=['DELETE'])
def delete_coche(coche_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM coches WHERE id = ?',(coche_id,))
    conn.commit()
    conn.close()

    #Comprobar si se ha borrado
    if cur.rowcount == 0:
        return jsonify({'Error':'Coche no encontrado para borrar'}),404
    
    return jsonify({"mensaje": "Coche eliminado"}), 200

@app.route("/api/coches/<int:coche_id>", methods=['PUT'])
def update_coche(coche_id):
    coche_a_actualizar = None
    for coche in coches:
        if coche["id"] == coche_id:
            coche_a_actualizar = coche
            break
    if not coche_a_actualizar:
        return jsonify({"error": "Coche no encontrado"}), 404

    updated_data = request.get_json()
   # Comprobamos si al menos una de las claves que nos envían es válida para actualizar
    allowed_keys = {"marca", "modelo", "anio"}
    if not updated_data:
        return jsonify({"error": "No se enviaron datos"}), 400

    invalid_keys = [k for k in updated_data if k not in allowed_keys]
    if invalid_keys:
        return jsonify({"error": f"Campos invalidos: {invalid_keys}"}), 400

    # Actualizar solo los permitidos
    for key in allowed_keys:
        if key in updated_data:
            coche_a_actualizar[key] = updated_data[key]

    return jsonify({"mensaje": "Coche actualizado con exito ✔"}), 200


# Esto es para poder ejecutar el servidor al correr el script
if __name__ == '__main__':
    app.run(debug=True)
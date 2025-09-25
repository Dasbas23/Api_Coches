from flask import Flask, jsonify, request

app = Flask(__name__)
# Datos de ejemplo: una lista de coches
coches = [
    {"id": 1, "marca": "Audi", "modelo": "A4", "anio": 2020},
    {"id": 2, "marca": "BMW", "modelo": "X3", "anio": 2021},
    {"id": 3, "marca": "Mercedes", "modelo": "C-Class", "anio": 2019}
]


# Definimos la primera "ruta" o "endpoint"
@app.route("/")
def hola_mundo():
    return "Bienvenido a mi API de Coches"


@app.route("/marcas")
def marcas():
    return "Aqui irán las marcas de coches"


@app.route("/api/coches", methods=['GET'])
def obtener_coches():
    return jsonify(coches)


@app.route("/api/coches/<int:coche_id>", methods=['GET'])
def get_coche(coche_id):
    # Usamos un bucle para encontrar el coche por su ID
    for coche in coches:
        if coche["id"] == coche_id:
            return jsonify(coche)

    # Si no encontramos el coche, devolvemos un error 404
    return jsonify({"error": "Coche no encontrado"}),


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


# Esto es para poder ejecutar el servidor al correr el script
if __name__ == '__main__':
    app.run(debug=True)
import requests
from flask import current_app


def _backend_url():
    return current_app.config.get("BACKEND_URL", "http://localhost:5000/api")


def get(endpoint, params=None, headers=None):
    response = requests.get(
        f"{_backend_url()}{endpoint}",
        params=params,
        headers=headers,
        timeout=5,
    )

    if response.status_code == 404:
        return response.json()

    response.raise_for_status()
    return response.json()


def post(endpoint, data=None, headers=None):
    response = requests.post(
        f"{_backend_url()}{endpoint}",
        json=data,
        headers=headers,
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


def cancelar_compra(id_compra, cookie_backend):
    try:
        response = requests.patch(
            f"{_backend_url()}/compras/{id_compra}",
            json={"estado_qr": "CANCELADO"},
            cookies={"session": cookie_backend},
            timeout=5,
        )
        try:
            datos = response.json()
        except ValueError:
            datos = {}
        if not isinstance(datos, dict):
            datos = {}

        if response.status_code == 200 and datos.get("status") == "success":
            return True, f"La compra #{id_compra} fue cancelada."
        return False, datos.get(
            "message", "No se pudo cancelar la compra. Revisá si sigue siendo elegible."
        )
    except requests.RequestException:
        return False, "No se pudo conectar con el Backend para cancelar la compra."


def obtener_peliculas(genero=None, titulo=None, id_sucursal=None):
    params = {}
    if genero:
        params["genero"] = genero
    if titulo:
        params["titulo"] = titulo
    if id_sucursal:
        params["id_sucursal"] = id_sucursal
    response = get("/peliculas", params=params)

    if response.get("status") != "success":
        raise RuntimeError(response.get("message", "No se pudo obtener la cartelera"))

    peliculas = response.get("data", [])

    if not isinstance(peliculas, list):
        raise ValueError("La respuesta del backend no contiene una lista de películas")
    return peliculas


def obtener_pelicula_por_id(id_pelicula):
    response = get(f"/peliculas/{id_pelicula}")

    if response.get("status") == "error":
        return None
    if response.get("status") != "success":
        raise RuntimeError(response.get("message", "No se pudo obtener la película"))

    return response.get("data")


def obtener_funciones(id_pelicula=None, id_sucursal=None, fecha=None):
    params = {}
    if id_sucursal:
        params['id_sucursal'] = id_sucursal
    if fecha:
        params['fecha'] = fecha
    if id_pelicula:
        params['id_pelicula'] = id_pelicula

    response = get(f"/funciones", params=params)
    if response.get("status") != "success":
        raise RuntimeError(response.get("message", "No se pudieron obtener las funciones"))

    funciones = response.get("data")
    if not isinstance(funciones, list):
        raise ValueError("La respuesta del backend no contiene una lista de funciones")
    return funciones


def obtener_sucursales():
    response = get("/sucursales")
    if response.get("status") != "success":
        raise RuntimeError(response.get("message", "No se pudieron obtener las sucursales"))

    sucursales = response.get("data")
    if not isinstance(sucursales, list):
        raise ValueError("La respuesta del backend no contiene una lista de sucursales")
    return sucursales
def obtener_servicios():
    response = get("/servicios")

    if response.get("status") != "success":
        raise RuntimeError(
            response.get("message", "No se pudieron obtener los servicios")
        )

    servicios = response.get("data")

    if not isinstance(servicios, list):
        raise ValueError("La respuesta del backend no contiene una lista de servicios")

    return servicios


def crear_compra(datos, cookie_backend):
    response = requests.post(
        f"{_backend_url()}/compras",
        json=datos,
        cookies={"session": cookie_backend},
        timeout=5,
    )

    try:
        respuesta = response.json()
    except ValueError:
        raise ValueError("El backend devolvió una respuesta inválida.")

    response.raise_for_status()

    return respuesta


def obtener_funcion_por_id(id_funcion):
    response = get(f"/funciones/{id_funcion}")
    if response.get("status") == "error":
        return None
    if response.get("status") != "success":
        raise RuntimeError(response.get("message", "No se pudo obtener la función"))
    return response.get("data")


def obtener_asientos_por_funcion(id_funcion):
    response = get(f"/funciones/{id_funcion}/asientos")
    if response.get("status") == "error":
        return None
    if response.get("status") != "success":
        raise RuntimeError(response.get("message", "No se pudo obtener la disponibilidad de asientos"))

    asientos = response.get("data", [])
    if not isinstance(asientos, list):
        raise ValueError("La respuesta del backend no contiene una lista de asientos")
    return asientos

def obtener_resenas(id_pelicula):
    response = get(f"/peliculas/{id_pelicula}/resenas")

    if response.get("status") != "success":
        raise RuntimeError(
            response.get("message", "No se pudieron obtener las reseñas")
        )

    resenas = response.get("data")

    if not isinstance(resenas, list):
        raise ValueError("La respuesta del backend no contiene una lista de reseñas")

    return resenas


def crear_resena(id_pelicula, puntuacion, comentario, cookie_backend):
    cuerpo = {"puntuacion": puntuacion}
    if comentario:
        cuerpo["comentario"] = comentario

    try:
        response = requests.post(
            f"{_backend_url()}/peliculas/{id_pelicula}/resenas",
            json=cuerpo,
            cookies={"session": cookie_backend},
            timeout=5,
        )
        try:
            datos = response.json()
        except ValueError:
            datos = {}
        if not isinstance(datos, dict):
            datos = {}

        if response.status_code == 201 and datos.get("status") == "success":
            return True, "¡Gracias por tu reseña!"
        return False, datos.get(
            "message", "No se pudo publicar la reseña. Intentá nuevamente."
        )
    except requests.RequestException:
        return False, "No se pudo conectar con el Backend para publicar la reseña."
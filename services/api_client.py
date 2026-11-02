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


def obtener_peliculas(genero=None, sucursal=None, fecha=None, page=1):
    params = {}
    if genero:
        params["genero"] = genero
    if sucursal:
        params["sucursal"] = sucursal
    if fecha:
        params["fecha"] = fecha
    params["page"] = page

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

def obtener_funciones(pelicula_id, sucursal=None, fecha=None):
    params = {}
    if sucursal:
        params['sucursal'] = sucursal
    if fecha:
        params['fecha'] = fecha

    response = get(f"/peliculas/{pelicula_id}/funciones", params=params)
    if response.get("status") != "success":
        raise RuntimeError(response.get("message", "No se pudieron obtener las funciones"))

    funciones = response.get("data")
    if not isinstance(funciones, list):
        raise ValueError("La respuesta del backend no contiene una lista de funciones")
    return funciones    


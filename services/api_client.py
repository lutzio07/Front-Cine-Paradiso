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


def obtener_peliculas(genero=None, titulo=None, id_sucursal=None):
    """Return movies list; try backend first, fallback to static JSON.
    Filters ``genero`` and ``titulo`` are applied on the final list.
    """
    params = {k: v for k, v in (("genero", genero), ("titulo", titulo), ("id_sucursal", id_sucursal)) if v}
    try:
        resp = get("/peliculas", params=params)
        if resp.get("status") == "success":
            return resp.get("data", [])
        raise RuntimeError(resp.get("message", "Error backend"))
    except Exception:
        import json, os
        path = os.path.join(current_app.root_path, "static", "data", "peliculas.json")
        with open(path, "r", encoding="utf-8") as f:
            peliculas = json.load(f)
        for p in peliculas:
            p.setdefault("duracion_min", p.pop("duracion_minutos", None))
            p.setdefault("con_funciones", p.pop("tiene_funciones_disponibles", None))
        if genero:
            peliculas = [p for p in peliculas if p.get("genero") == genero]
        if titulo:
            peliculas = [p for p in peliculas if titulo.lower() in p.get("titulo", "").lower()]
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
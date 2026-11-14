import requests
from flask import current_app, session


def _backend_url():
    base = ( current_app.config.get("BACKEND_URL") or "http://localhost:5000/api" ).rstrip("/")

    return base if base.endswith("/api") else f"{base}/api"


def _get_auth_headers():
    return {"Content-Type": "application/json"}


def _get_backend_cookies():
    cookie = session.get("backend_session")
    return {"session": cookie} if cookie else {}


def _extraer_error(respuesta, defecto):
    try:
        cuerpo = respuesta.json()
        if isinstance(cuerpo, dict):
            return ( cuerpo.get("message") or cuerpo.get("mensaje")  or defecto )

    except ValueError:
        pass

    return defecto


def consultar_lista(path, recurso):
    try:
        respuesta = requests.get(
            f"{_backend_url()}{path}", headers=_get_auth_headers(), cookies=_get_backend_cookies(), timeout=10, )

        if not respuesta.ok:
            return [], _extraer_error(respuesta, "No fue posible obtener los datos")

        cuerpo = respuesta.json()
        datos = cuerpo.get("data") if isinstance(cuerpo, dict) else None

        if not isinstance(datos, list):
            return [], "La respuesta no contiene una lista en data."

        return datos, None

    except (requests.RequestException, ValueError) as error:
        current_app.logger.warning("Fallo consultando %s: %s", recurso, error)
        return [], "verificá la conexión con el backend."


def obtener_datos_backoffice_peliculas():
    sucursales, _ = consultar_lista("/sucursales", "sucursales")

    salas = []
    for sucursal in sucursales:
        if not isinstance(sucursal, dict):
            continue

        id_sucursal = sucursal.get("id_sucursal")
        if id_sucursal is None:
            continue

        salas_sucursal, _ = consultar_lista(
            f"/sucursales/{id_sucursal}/salas", "salas" )

        for sala in salas_sucursal:
            if isinstance(sala, dict):
                sala["nombre_sucursal"] = sucursal.get("nombre")
                salas.append(sala)

    peliculas_list, _ = consultar_lista("/peliculas", "películas")
    funciones, _ = consultar_lista("/funciones", "funciones")

    return sucursales, salas, peliculas_list, funciones


def crear_sala(id_sucursal, nombre, capacidad):
    payload = { "nombre": nombre, "capacidad": capacidad }

    try:
        respuesta = requests.post(
            f"{_backend_url()}/sucursales/{id_sucursal}/salas", json=payload,  headers=_get_auth_headers(), cookies=_get_backend_cookies(), timeout=10, )

        if respuesta.status_code == 201:
            return True, f"Sala '{nombre}' creada exitosamente."

        return False, f"Error {respuesta.status_code}: {_extraer_error(respuesta, 'No se pudo crear la sala.')}"

    except requests.RequestException:
        return False, "No se pudo contactar con el backend para crear la sala."


def crear_funcion(payload):
    try:
        respuesta = requests.post(
            f"{_backend_url()}/funciones", json=payload, headers=_get_auth_headers(), cookies=_get_backend_cookies(), timeout=10, )

        if respuesta.status_code == 201:
            return True, "Función programada exitosamente."

        return False, f"Error {respuesta.status_code}: {_extraer_error(respuesta, 'No se pudo programar la función.')}"

    except requests.RequestException:
        return False, "No se pudo contactar con el backend para crear la función."


def eliminar_sala(id_sucursal, id_sala):
    try:
        respuesta = requests.delete(
            f"{_backend_url()}/sucursales/{id_sucursal}/salas/{id_sala}", headers=_get_auth_headers(), cookies=_get_backend_cookies(), timeout=10, )

        if respuesta.status_code == 200:
            return True, "Sala eliminada correctamente."

        if respuesta.status_code == 409:
            detalle = _extraer_error(respuesta, "No se puede eliminar la sala porque tiene funciones o recursos asociados.")
            return False, f"No se pudo eliminar: {detalle}"

        if respuesta.status_code in (401, 403):
            return False, "Sesión expirada o sin permisos. Iniciá sesión nuevamente."

        return False, f"Error {respuesta.status_code}: {_extraer_error(respuesta, 'No fue posible eliminar la sala.')}"

    except requests.RequestException:
        return False, "No se pudo conectar con el backend para eliminar la sala."


def eliminar_funcion(id_funcion):
    try:
        respuesta = requests.delete(
            f"{_backend_url()}/funciones/{id_funcion}",  headers=_get_auth_headers(), cookies=_get_backend_cookies(), timeout=10, )

        if respuesta.status_code == 200:
            return True, "Función eliminada correctamente."

        if respuesta.status_code == 409:
            detalle = _extraer_error(respuesta, "No se puede eliminar la función porque tiene entradas vendidas asociadas.")
            return False, f"No se pudo eliminar: {detalle}"

        if respuesta.status_code in (401, 403):
            return False, "Sesión expirada o sin permisos. Iniciá sesión nuevamente."

        return False, f"Error {respuesta.status_code}: {_extraer_error(respuesta, 'No fue posible eliminar la función.')}"

    except requests.RequestException:
        return False, "No se pudo conectar con el backend para eliminar la función."


def buscar_peliculas_tmdb(texto_busqueda):
    if not texto_busqueda or not texto_busqueda.strip():
        return [], "Ingresá un título o palabra clave para buscar en TMDb."

    try:
        respuesta = requests.get(
            f"{_backend_url()}/peliculas-externas",
            params={"q": texto_busqueda.strip()},
            headers=_get_auth_headers(),
            cookies=_get_backend_cookies(),
            timeout=10,
        )

        if not respuesta.ok:
            return [], _extraer_error(respuesta, "No fue posible consultar TMDb.")

        cuerpo = respuesta.json()
        datos = cuerpo.get("data") if isinstance(cuerpo, dict) else None

        if not isinstance(datos, list):
            return [], "La respuesta de TMDb no contiene un listado válido."

        return datos, None

    except requests.RequestException as error:
        current_app.logger.warning("Fallo consultando TMDb: %s", error)
        return [], "Error de conexión al consultar TMDb. Verificá que el backend esté activo."


def importar_pelicula(payload):
    try:
        respuesta = requests.post(
            f"{_backend_url()}/peliculas",
            json=payload,
            headers=_get_auth_headers(),
            cookies=_get_backend_cookies(),
            timeout=10,
        )

        if respuesta.status_code == 201:
            titulo = payload.get("titulo", "Película")
            return True, f"Película '{titulo}' importada exitosamente al catálogo."

        if respuesta.status_code == 409:
            titulo = payload.get("titulo", "Película")
            return False, f"La película '{titulo}' ya se encuentra registrada en el catálogo."

        return False, f"Error {respuesta.status_code}: {_extraer_error(respuesta, 'No se pudo importar la película.')}"

    except requests.RequestException:
        return False, "No se pudo conectar con el backend para importar la película."


def obtener_servicios():
    servicios_list, _ = consultar_lista("/servicios", "servicios")
    return servicios_list


def validar_codigo_qr(codigo_qr, id_funcion):
    try:
        url = f"{_backend_url()}/codigos-qr/{codigo_qr}"
        headers = _get_auth_headers()
        cookies = _get_backend_cookies()
        payload = {"id_funcion": id_funcion}

        response = requests.patch(url, json=payload, headers=headers, cookies=cookies, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return (True, "Acceso permitido", data)
        elif response.status_code == 400:
            error = _extraer_error(response, "Codigo QR invalido")
            return (False, error, None)
        elif response.status_code == 403:
            error = _extraer_error(response, "Codigo QR ya utilizado")
            return (False, error, None)
        elif response.status_code == 404:
            return (False, "Código QR no encontrado", None)
        elif response.status_code == 409:
            error = _extraer_error(response, "Codigo ya usado o no valido para esta funcion")
            return (False, error, None)
        else:
            error = _extraer_error(response, "Error al validar el codigo QR")
            return (False, error, None)

    except requests.exceptions.ConnectionError:
        return (False, "No se pudo conectar con el servidor", None)

    except Exception as e:
        return (False, f"Error inesperado: {str(e)}", None)

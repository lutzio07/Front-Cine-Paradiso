import requests
from flask import current_app


def _backend_url():
    base = ( current_app.config.get("BACKEND_URL") or "http://localhost:5000/api" ).rstrip("/")

    return base if base.endswith("/api") else f"{base}/api"


def registrar_usuario(nombre, email, password):
    payload = {
        "nombre": nombre,
        "email": email,
        "password": password
    }

    try:
        respuesta = requests.post(
            f"{_backend_url()}/usuarios", json=payload, timeout=5,)

        datos = (
            respuesta.json()
            if respuesta.headers.get("content-type") == "application/json"
            else {}
        )

        if respuesta.status_code == 201 and datos.get("status") == "success":
            return True, "Cuenta creada. Ahora podés iniciar sesión."

        return False, datos.get("message", "No se pudo registrar la cuenta.")

    except requests.RequestException:
        return False, "No se pudo conectar con el Backend."


def iniciar_sesion(email, password):
    payload = {
        "email": email,
        "password": password
    }

    try:
        respuesta = requests.post(
            f"{_backend_url()}/sesiones", json=payload, timeout=5, )

        datos = (
            respuesta.json()
            if respuesta.headers.get("content-type") == "application/json"
            else {}
        )

        cookie_backend = respuesta.cookies.get("session")

        if (
            respuesta.status_code == 200
            and datos.get("status") == "success"
        ):
            usuario = datos.get("data")
            if (isinstance(usuario, dict) and usuario.get("id_usuario") and usuario.get("nombre") and usuario.get("rol") in ("CLIENTE", "ADMIN") and cookie_backend):
                return True, usuario, cookie_backend, None

            return False, None, None, "El Backend devolvió una sesión incompleta."

        return False, None, None, datos.get("message", "Credenciales incorrectas.")

    except requests.RequestException:
        return False, None, None, "No se pudo conectar con el Backend."


def cerrar_sesion(cookie_backend):
    if not cookie_backend:
        return True

    try:
        respuesta = requests.delete(
            f"{_backend_url()}/sesiones", cookies={"session": cookie_backend}, timeout=5, )

        return respuesta.status_code in (200, 204, 401)

    except requests.RequestException:
        return False
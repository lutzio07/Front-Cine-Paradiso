import requests
from flask import current_app


def _backend_url():
    base = (
        current_app.config.get("BACKEND_URL") or "http://localhost:5000/api"
    ).rstrip("/")
    return base if base.endswith("/api") else f"{base}/api"


def solicitar_recuperacion_password(email, frontend_url):
    payload = {
        "email": email,
        "frontend_url": frontend_url,
    }

    try:
        respuesta = requests.post(
            f"{_backend_url()}/recuperar-password",
            json=payload,
            timeout=15,
        )

        datos = (
            respuesta.json()
            if "application/json" in respuesta.headers.get("content-type", "")
            else {}
        )

        if respuesta.status_code == 200 and datos.get("status") == "success":
            mensaje = (datos.get("data") or {}).get(
                "message",
                "Si el correo está registrado, te enviamos un enlace para restablecer tu contraseña.",
            )
            return True, mensaje

        return False, datos.get("message", "No se pudo procesar la solicitud.")

    except requests.RequestException:
        return False, "No se pudo conectar con el Backend."


def restablecer_password(token, password):
    payload = {
        "token": token,
        "password": password,
    }

    try:
        respuesta = requests.post(
            f"{_backend_url()}/restablecer-password",
            json=payload,
            timeout=5,
        )

        datos = (
            respuesta.json()
            if "application/json" in respuesta.headers.get("content-type", "")
            else {}
        )

        if respuesta.status_code == 200 and datos.get("status") == "success":
            mensaje = (datos.get("data") or {}).get(
                "message",
                "Contraseña actualizada correctamente. Ya podés iniciar sesión.",
            )
            return True, mensaje

        return False, datos.get("message", "No se pudo restablecer la contraseña.")

    except requests.RequestException:
        return False, "No se pudo conectar con el Backend."
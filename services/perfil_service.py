from flask import session
from services.api_client import get

def obtener_perfil():
    cookie = session.get("backend_session")         # la clave con la que el login guardó la cookie del backend
    respuesta = get("/perfil", headers={"Cookie": f"session={cookie}"})
    if respuesta.get("status") != "success":
        raise RuntimeError(respuesta.get("message", "No se pudo obtener el perfil"))
    return respuesta["data"]
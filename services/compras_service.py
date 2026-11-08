from flask import session
from services.api_client import get

def obtener_detalle_compra(id_compra):
    # Reutiliza la sesión del backend para consultar la compra.
    cookie = session.get("backend_session")
    respuesta = get(
        f"/compras/{id_compra}",
        headers={"Cookie": f"session={cookie}"},
    )
    if respuesta.get("status") != "success":
        return None
    return respuesta["data"]

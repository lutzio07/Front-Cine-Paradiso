# Datos de ejemplo con la forma del swagger v2.1.0.
# TODO backend: response = get("/perfil"); validar status == "success"; return response["data"]


def obtener_perfil():
    return {
        "usuario": {"id_usuario": 2, "nombre": "Ana García", "email": "ana@example.com", "rol": "CLIENTE"},
        "compras": [
            {"id_compra": 1, "id_usuario": 2, "fecha_compra": "2026-10-15T20:00:00-03:00",
             "monto_total": 9000.0, "codigo_qr": "QR-8F92A1B3", "estado_qr": "USADO"},
            {"id_compra": 2, "id_usuario": 2, "fecha_compra": "2026-10-20T18:30:00-03:00",
             "monto_total": 3500.0, "codigo_qr": "QR-1C44D7E2", "estado_qr": "PENDIENTE"},
        ],
    }
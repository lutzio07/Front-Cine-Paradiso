from datetime import datetime, timedelta, timezone

import requests
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app,
)


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)


def es_admin():
    usuario = (
        session.get("usuario")
        or session.get("user")
        or session.get("user_info")
    )

    if isinstance(usuario, dict):
        rol = str(
            usuario.get("rol")
            or usuario.get("role")
            or ""
        ).lower()

        if rol:
            return rol in ("admin", "administrador")

    rol = str(
        session.get("rol")
        or session.get("role")
        or ""
    ).lower()

    return rol in ("admin", "administrador")


def backend_url():
    base = (
        current_app.config.get("BACKEND_URL")
        or "http://localhost:5000/api"
    ).rstrip("/")

    return base if base.endswith("/api") else f"{base}/api"


def get_auth_headers():
    return {
        "Content-Type": "application/json"
    }


def get_backend_cookies():
    cookie = session.get("backend_session")

    return {
        "session": cookie
    } if cookie else {}


def extraer_error(respuesta, defecto):
    try:
        cuerpo = respuesta.json()

        if isinstance(cuerpo, dict):
            return (
                cuerpo.get("message")
                or cuerpo.get("mensaje")
                or defecto
            )

    except ValueError:
        pass

    return defecto


def consultar_lista(url, recurso):
    try:
        respuesta = requests.get(
            url,
            headers=get_auth_headers(),
            cookies=get_backend_cookies(),
            timeout=10,
        )

        if not respuesta.ok:
            detalle = extraer_error(
                respuesta,
                "No fue posible obtener los datos"
            )

            flash(
                f"No se pudieron cargar {recurso} "
                f"(HTTP {respuesta.status_code}): {detalle}",
                "error"
            )

            return []

        cuerpo = respuesta.json()

        datos = (
            cuerpo.get("data")
            if isinstance(cuerpo, dict)
            else None
        )

        if not isinstance(datos, list):
            flash(
                f"La respuesta de {recurso} "
                "no contiene una lista en data.",
                "error"
            )

            return []

        return datos

    except (requests.RequestException, ValueError) as error:
        current_app.logger.warning(
            "Fallo consultando %s: %s",
            recurso,
            error
        )

        flash(
            f"No se pudieron cargar {recurso}: "
            "verificá la conexión con el backend.",
            "error"
        )

        return []

@admin_bp.route(
    "/peliculas",
    methods=["GET"],
    endpoint="peliculas"
)
@admin_bp.route(
    "/cargar-pelicula",
    methods=["GET"],
    endpoint="admin_salas_funciones"
)
@admin_bp.route(
    "/dashboard",
    methods=["GET"],
    endpoint="dashboard"
)
@admin_bp.route("/", methods=["GET"])
def peliculas():

    if not es_admin():
        flash(
            "Acceso denegado. Se requieren permisos de administrador.",
            "error"
        )

        return redirect(url_for("auth.vista_login"))

    base = backend_url()


    sucursales = consultar_lista(
        f"{base}/sucursales",
        "sucursales"
    )



    salas = []

    for sucursal in sucursales:

        if not isinstance(sucursal, dict):
            continue

        id_sucursal = sucursal.get("id_sucursal")

        if id_sucursal is None:
            continue

        salas_sucursal = consultar_lista(
            f"{base}/sucursales/{id_sucursal}/salas",
            "salas"
        )

        for sala in salas_sucursal:

            if isinstance(sala, dict):
                sala["nombre_sucursal"] = sucursal.get("nombre")
                salas.append(sala)


    peliculas_list = consultar_lista(
        f"{base}/peliculas",
        "películas"
    )


    funciones = consultar_lista(
        f"{base}/funciones",
        "funciones"
    )


    return render_template(
        "pages/admin_cargar_pelicula.html",
        section="admin",
        active="peliculas",
        sucursales=sucursales,
        salas=salas,
        peliculas=peliculas_list,
        funciones=funciones,
    )


@admin_bp.route(
    "/servicios",
    methods=["GET"],
    endpoint="servicios"
)
def servicios():

    if not es_admin():
        flash(
            "Acceso denegado. Se requieren permisos de administrador.",
            "error"
        )

        return redirect(url_for("auth.vista_login"))

    url = f"{backend_url()}/servicios"

    servicios_list = consultar_lista(
        url,
        "servicios"
    )

    return render_template(
        "pages/admin_abm_servicios.html",
        section="admin",
        active="servicios",
        servicios=servicios_list,
    )


@admin_bp.route(
    "/validador",
    methods=["GET"],
    endpoint="validador"
)
def validador():

    if not es_admin():
        flash(
            "Acceso denegado. Se requieren permisos de administrador.",
            "error"
        )

        return redirect(url_for("auth.vista_login"))

    return render_template(
        "pages/admin_validador.html",
        section="admin",
        active="validador"
    )

@admin_bp.route(
    "/salas",
    methods=["POST"],
    endpoint="crear_sala"
)
def crear_sala():

    if not es_admin():
        flash(
            "Acceso no autorizado.",
            "error"
        )

        return redirect(url_for("auth.vista_login"))

    if not get_backend_cookies():
        flash(
            "Falta la sesión del backend. "
            "Iniciá sesión nuevamente.",
            "error"
        )

        return redirect(url_for("admin.peliculas"))

    id_sucursal = request.form.get(
        "id_sucursal", ""
    ).strip()

    nombre = request.form.get(
        "nombre", ""
    ).strip()

    try:
        capacidad = int(
            request.form.get("capacidad", "")
        )

    except ValueError:
        flash(
            "La capacidad debe ser un número entero.",
            "error"
        )

        return redirect(url_for("admin.peliculas"))

    payload = {
        "nombre": nombre,
        "capacidad": capacidad
    }

    try:
        respuesta = requests.post(
            f"{backend_url()}/sucursales/{id_sucursal}/salas",
            json=payload,
            headers=get_auth_headers(),
            cookies=get_backend_cookies(),
            timeout=10,
        )

    except requests.RequestException:
        flash(
            "No se pudo contactar con el backend "
            "para crear la sala.",
            "error"
        )

        return redirect(url_for("admin.peliculas"))

    if respuesta.status_code == 201:
        flash(
            f"Sala '{nombre}' creada exitosamente.",
            "success"
        )

    else:
        flash(
            f"Error {respuesta.status_code}: "
            f"{extraer_error(respuesta, 'No se pudo crear la sala.')}",
            "error"
        )

    return redirect(url_for("admin.peliculas"))

@admin_bp.route(
    "/funciones",
    methods=["POST"],
    endpoint="crear_funcion"
)
def crear_funcion():

    if not es_admin():
        flash(
            "Acceso no autorizado.",
            "error"
        )

        return redirect(url_for("auth.vista_login"))

    if not get_backend_cookies():
        flash(
            "Falta la sesión del backend. "
            "Iniciá sesión nuevamente.",
            "error"
        )

        return redirect(url_for("admin.peliculas"))

    try:
        id_pelicula = int(
            request.form.get("id_pelicula", "")
        )

        id_sala = int(
            request.form.get("id_sala", "")
        )

        precio = float(
            request.form.get("precio_entrada", "")
        )

        # datetime-local no incluye zona horaria.
        fecha_local = datetime.fromisoformat(
            request.form.get("fecha_hora", "")
        )

        if fecha_local.tzinfo is not None:
            raise ValueError("Fecha con zona inesperada")

        zona_argentina = timezone(
            timedelta(hours=-3)
        )

        fecha_argentina = fecha_local.replace(
            tzinfo=zona_argentina
        )

    except (ValueError, TypeError):
        flash(
            "Revisá la película, la sala, "
            "la fecha/hora y el precio.",
            "error"
        )

        return redirect(url_for("admin.peliculas"))

    payload = {
        "id_pelicula": id_pelicula,
        "id_sala": id_sala,
        "fecha_hora": fecha_argentina.isoformat(
            timespec="seconds"
        ),
        "precio_entrada": precio,
    }

    try:
        respuesta = requests.post(
            f"{backend_url()}/funciones",
            json=payload,
            headers=get_auth_headers(),
            cookies=get_backend_cookies(),
            timeout=10,
        )

    except requests.RequestException:
        flash(
            "No se pudo contactar con el backend "
            "para crear la función.",
            "error"
        )

        return redirect(url_for("admin.peliculas"))

    if respuesta.status_code == 201:
        flash(
            "Función programada exitosamente.",
            "success"
        )

    else:
        detalle = extraer_error(
            respuesta,
            "No se pudo programar la función."
        )

        flash(
            f"Error {respuesta.status_code}: {detalle}",
            "error"
        )

    return redirect(url_for("admin.peliculas"))

from flask import Blueprint, flash, render_template, request, session, redirect, url_for
from services.api_client import (
    cancelar_compra as solicitar_cancelacion_compra,
    obtener_pelicula_por_id, 
    obtener_peliculas,
    obtener_funciones,
    obtener_sucursales,
    obtener_servicios,
    crear_compra,
)
from services.cartelera_service import armar_cartelera
from datetime import datetime
from requests.exceptions import RequestException
from services.perfil_service import obtener_perfil
main_bp = Blueprint("main", __name__)

@main_bp.route("/compras/servicios")
def seleccionar_servicios():
    if not session.get("backend_session"):
        flash("Iniciá sesión para continuar con la compra.", "warning")
        return redirect(url_for("auth.vista_login"))

    if session.get("rol") != "CLIENTE":
        flash("Solo los clientes pueden realizar compras.", "danger")
        return redirect(url_for("main.index"))

    compra_pendiente = session.get("compra_pendiente")

    if not compra_pendiente:
        flash("Primero tenés que seleccionar las butacas.", "warning")
        return redirect(url_for("main.index"))

    servicios = []
    error_servicios = False

    try:
        servicios = obtener_servicios()
    except (RequestException, RuntimeError, ValueError):
        error_servicios = True

    return render_template(
        "pages/seleccion_servicios.html",
        servicios=servicios,
        error_servicios=error_servicios,
        id_funcion=compra_pendiente["id_funcion"],
        asientos_ids=compra_pendiente["asientos_ids"],
    )

@main_bp.post("/compras/servicios")
def confirmar_compra_route():
    if not session.get("backend_session"):
        flash("Iniciá sesión para continuar con la compra.", "warning")
        return redirect(url_for("auth.vista_login"))

    if session.get("rol") != "CLIENTE":
        flash("Solo los clientes pueden realizar compras.", "danger")
        return redirect(url_for("main.index"))

    compra_pendiente = session.get("compra_pendiente")

    if not compra_pendiente:
        flash("No hay una selección de butacas pendiente.", "warning")
        return redirect(url_for("main.index"))

    try:
        catalogo_servicios = obtener_servicios()
    except (RequestException, RuntimeError, ValueError):
        flash("No se pudieron verificar los servicios adicionales. Intentá nuevamente.", "danger")
        return redirect(url_for("main.seleccionar_servicios"))

    if not all(
        isinstance(servicio, dict)
        and type(servicio.get("id_servicio")) is int
        and servicio["id_servicio"] > 0
        for servicio in catalogo_servicios
    ):
        flash("El catálogo de servicios contiene datos inválidos.", "danger")
        return redirect(url_for("main.seleccionar_servicios"))

    ids_servicios_validos = {
        servicio["id_servicio"]
        for servicio in catalogo_servicios
    }

    servicios = []

    try:
        for campo, valor in request.form.items():
            if not campo.startswith("servicio_"):
                continue

            id_servicio = int(campo.removeprefix("servicio_"))
            cantidad = int(valor)

            if id_servicio <= 0 or id_servicio not in ids_servicios_validos or cantidad < 0 or cantidad > 10:
                raise ValueError

            if cantidad > 0:
                servicios.append({
                    "id_servicio": id_servicio,
                    "cantidad": cantidad,
                })

    except ValueError:
        flash("Las cantidades de los servicios no son válidas.", "danger")
        return redirect(url_for("main.seleccionar_servicios"))

    datos_compra = {
        "id_funcion": compra_pendiente["id_funcion"],
        "asientos_ids": compra_pendiente["asientos_ids"],
        "servicios": servicios,
    }

    try:
        respuesta = crear_compra(
            datos_compra,
            session["backend_session"],
        )

        if not isinstance(respuesta, dict):
            raise ValueError("La respuesta del backend no es válida.")

        if respuesta.get("status") != "success":
            raise RuntimeError(
                respuesta.get("message", "No se pudo completar la compra.")
            )

    except (RequestException, RuntimeError, ValueError):
        flash("No se pudo completar la compra. Intentá nuevamente.", "danger")
        return redirect(url_for("main.seleccionar_servicios"))

    session.pop("compra_pendiente", None)

    flash("¡Tu compra se realizó correctamente!", "success")
    return redirect(url_for("main.perfil"))

@main_bp.route("/")
def index():
    genero = request.args.get("genero", default=None, type=str)
    id_sucursal = request.args.get("id_sucursal", default=None, type=int)
    fecha = request.args.get("fecha", default=None, type=str)

    peliculas = []
    generos = []
    sucursales = []
    cartelera = []
    error = False
    try:
        peliculas = obtener_peliculas(genero=genero)
        funciones = obtener_funciones(id_sucursal=id_sucursal, fecha=fecha)
        sucursales = obtener_sucursales()
        cartelera = armar_cartelera(peliculas, funciones, filtrando=bool(id_sucursal or fecha))
        generos = sorted(set(p["genero"] for p in peliculas if "genero" in p and p["genero"]))
    except (RequestException, RuntimeError, ValueError):
        error = True

    return render_template(
        "pages/index.html",
        peliculas=cartelera,
        generos_disponibles=generos,
        error=error,
        sucursales=sucursales,
    )

@main_bp.route("/pelicula/<int:id_pelicula>")
def pelicula_detalle(id_pelicula):
    id_sucursal = request.args.get("id_sucursal", default=None, type=int)
    fecha = request.args.get("fecha", default=None, type=str)
    pelicula = None
    funciones = []
    sucursales = []
    error = False
    try:
        pelicula = obtener_pelicula_por_id(id_pelicula=id_pelicula)
        if pelicula:
            funciones = obtener_funciones(id_sucursal=id_sucursal, fecha=fecha, id_pelicula=id_pelicula)
            sucursales = obtener_sucursales()
    except (RequestException, RuntimeError, ValueError):
        error = True

    if error:
        return render_template("pages/pelicula_detalle.html", pelicula=pelicula, funciones=[], error=True), 503

    if not pelicula:
        return render_template("pages/pelicula_detalle.html", pelicula=None, funciones=[], error=False), 404
    
    return render_template("pages/pelicula_detalle.html", pelicula=pelicula, funciones=funciones, sucursales=sucursales, error=False)

@main_bp.route("/perfil")
def perfil():
    if not session.get("backend_session"):
        return redirect(url_for("auth.vista_login"))
    usuario = {}
    compras = []
    error = False
    try:
        datos = obtener_perfil()
        usuario = datos["usuario"]
        compras = datos["compras"]
    except (RequestException, RuntimeError, ValueError, KeyError):
        error = True

    peliculas_vistas = [c for c in compras if c.get("estado_qr") == "USADO"]
    status = 503 if error else 200
    return render_template("pages/perfil.html", usuario=usuario, compras=compras,
                           peliculas_vistas=peliculas_vistas, error=error), status


@main_bp.post("/mis-compras/<int:id_compra>/cancelacion")
def cancelar_compra_route(id_compra):
    cookie_backend = session.get("backend_session")
    if not cookie_backend:
        flash("Iniciá sesión para cancelar una compra.", "danger")
        return redirect(url_for("auth.vista_login"))

    ok, mensaje = solicitar_cancelacion_compra(id_compra, cookie_backend)
    flash(mensaje, "success" if ok else "danger")

    return redirect(url_for("main.perfil"))

@main_bp.app_template_filter("datetimeformat")
def datetimeformat(value, formato="%d/%m/%Y %H:%M"):
    try:
        fecha = datetime.fromisoformat(value)
        return fecha.strftime(formato)
    except (ValueError, TypeError):
        return value

@main_bp.app_template_filter("pesos")
def pesos(value):
    try:
        return "${:,.0f}".format(float(value)).replace(",", ".")
    except (ValueError, TypeError):
        return value

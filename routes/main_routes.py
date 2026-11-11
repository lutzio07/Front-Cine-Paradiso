from flask import Blueprint, flash, render_template, request, session, redirect, url_for
from services.api_client import (
    cancelar_compra as solicitar_cancelacion_compra,
    obtener_asientos_por_funcion,
    obtener_funcion_por_id,
    obtener_pelicula_por_id, 
    obtener_peliculas,
    obtener_funciones,
    obtener_sucursales,
    obtener_sucursales,
    obtener_servicios,
    crear_compra,
)
from services.butacas_service import agrupar_asientos_por_fila
from services.cartelera_service import armar_cartelera
from datetime import datetime
from requests.exceptions import RequestException
from services.perfil_service import obtener_perfil
from services.compras_service import obtener_detalle_compra
from services.qr_service import generar_qr_data_url
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
    error_funciones = False

    try:
        peliculas = obtener_peliculas(genero=genero)
        generos = sorted(set(
            p["genero"] for p in peliculas
            if "genero" in p and p["genero"]
        ))
        sucursales = obtener_sucursales()

    except (RequestException, RuntimeError, ValueError):
        error = True

    if not error:
        try:
            funciones = obtener_funciones(
                id_sucursal=id_sucursal,
                fecha=fecha
            )
            cartelera = armar_cartelera(
                peliculas,
                funciones,
                filtrando=bool(id_sucursal or fecha)
            )

        except (RequestException, RuntimeError, ValueError):
            error_funciones = True
            cartelera = [
                {**p, "con_funciones": False}
                for p in peliculas
            ]

    return render_template(
        "pages/index.html",
        peliculas=cartelera,
        generos_disponibles=generos,
        error=error,
        error_funciones=error_funciones,
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
    error_funciones = False
    error_sucursales = False

    try:
        pelicula = obtener_pelicula_por_id(id_pelicula=id_pelicula)
    except (RequestException, RuntimeError, ValueError):
        error = True

    if error:
        return render_template(
            "pages/pelicula_detalle.html",
            pelicula=None,
            funciones=[],
            sucursales=[],
            error=True,
            error_funciones=False,
            error_sucursales=False
        ), 503

    if not pelicula:
        return render_template(
            "pages/pelicula_detalle.html",
            pelicula=None,
            funciones=[],
            sucursales=[],
            error=False,
            error_funciones=False,
            error_sucursales=False
        ), 404

    try:
        funciones = obtener_funciones(
            id_sucursal=id_sucursal,
            fecha=fecha,
            id_pelicula=id_pelicula
        )
    except (RequestException, RuntimeError, ValueError):
        error_funciones = True

    try:
        sucursales = obtener_sucursales()
    except (RequestException, RuntimeError, ValueError):
        error_sucursales = True

    return render_template("pages/pelicula_detalle.html", pelicula=pelicula, funciones=funciones, sucursales=sucursales, error=False, error_funciones=error_funciones, error_sucursales=error_sucursales)

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


@main_bp.get("/mis-compras/<int:id_compra>")
def detalle_compra(id_compra):
    if not session.get("backend_session"):
        return redirect(url_for("auth.vista_login"))

    try:
        detalle = obtener_detalle_compra(id_compra)
    except (RequestException, RuntimeError, ValueError, KeyError):
        flash("No pudimos cargar la compra. Intentá de nuevo.", "danger")
        return redirect(url_for("main.perfil"))

    if detalle is None:
        flash("La compra no existe.", "danger")
        return redirect(url_for("main.perfil"))

    compra = detalle["compra"]
    qr = None
    # Solo se muestra el QR si la compra sigue pendiente de uso.
    if compra.get("codigo_qr") and compra.get("estado_qr") == "PENDIENTE":
        qr = generar_qr_data_url(compra["codigo_qr"])

    return render_template(
        "pages/compra_detalle.html",
        compra=compra,
        entradas=detalle["entradas"],
        servicios=detalle["servicios"],
        qr=qr,
    )


@main_bp.route("/funciones/<int:id_funcion>/butacas", methods=["GET"])
def seleccion_butacas(id_funcion):
    error = False
    funcion = None
    pelicula = None
    mapa_filas = {}
    estadisticas = {}

    try:
        funcion = obtener_funcion_por_id(id_funcion)
        if funcion:
            pelicula = obtener_pelicula_por_id(funcion.get("id_pelicula"))
            asientos = obtener_asientos_por_funcion(id_funcion)
            if asientos is not None:
                mapa_filas, estadisticas = agrupar_asientos_por_fila(asientos)
            else:
                error = True
    except (RequestException, RuntimeError, ValueError):
        error = True

    if error:
        flash("No pudimos conectar con el servidor para consultar las butacas.", "danger")
        return render_template(
            "pages/seleccion_butacas.html",
            funcion=funcion,
            pelicula=pelicula,
            mapa_filas={},
            estadisticas={},
            error=True
        ), 503

    if not funcion:
        return render_template("pages/404.html"), 404

    compra_previa = session.get("compra_actual", {})
    asientos_previamente_seleccionados = []
    if compra_previa.get("id_funcion") == id_funcion:
        asientos_previamente_seleccionados = compra_previa.get("asientos_ids", [])

    return render_template(
        "pages/seleccion_butacas.html",
        funcion=funcion,
        pelicula=pelicula,
        mapa_filas=mapa_filas,
        estadisticas=estadisticas,
        asientos_previamente_seleccionados=asientos_previamente_seleccionados,
        error=False,
    )


@main_bp.route("/funciones/<int:id_funcion>/butacas", methods=["POST"])
def guardar_seleccion_butacas(id_funcion):
    asientos_ids = request.form.getlist("asientos_ids", type=int)

    if not asientos_ids:
        flash("Debés seleccionar al menos una butaca para continuar.", "warning")
        return redirect(url_for("main.seleccion_butacas", id_funcion=id_funcion))

    if len(asientos_ids) > 6:
        flash("El límite máximo de compra es de 6 butacas por operación.", "warning")
        return redirect(url_for("main.seleccion_butacas", id_funcion=id_funcion))

    try:
        funcion = obtener_funcion_por_id(id_funcion)
    except (RequestException, RuntimeError, ValueError):
        funcion = None

    precio_unitario = float(funcion.get("precio_entrada", 0)) if funcion else 0
    subtotal = precio_unitario * len(asientos_ids)

    asientos_etiquetas = []
    try:
        asientos_todos = obtener_asientos_por_funcion(id_funcion) or []
        asientos_dict = {
            a["id_asiento"]: f"{a.get('fila', '')}{a.get('numero', '')}"
            for a in asientos_todos
            if "id_asiento" in a
        }
        asientos_etiquetas = [
            asientos_dict.get(aid, str(aid)) for aid in sorted(asientos_ids)
        ]
    except Exception:
        asientos_etiquetas = [str(aid) for aid in sorted(asientos_ids)]

    session["compra_actual"] = {
        "id_funcion": id_funcion,
        "asientos_ids": sorted(asientos_ids),
        "asientos_etiquetas": asientos_etiquetas,
        "cantidad": len(asientos_ids),
        "precio_unitario": precio_unitario,
        "subtotal": subtotal,
        "titulo_pelicula": funcion.get("titulo_pelicula", "") if funcion else "",
        "nombre_sala": funcion.get("nombre_sala", "") if funcion else "",
        "nombre_sucursal": funcion.get("nombre_sucursal", "") if funcion else "",
        "fecha_hora": funcion.get("fecha_hora", "") if funcion else "",
    }

    session["compra_pendiente"] = {
    "id_funcion": id_funcion,
    "asientos_ids": sorted(asientos_ids),
    }

    flash(f"Seleccionaste {len(asientos_ids)} butaca(s) correctamente.", "success")
    return redirect(url_for("main.seleccionar_servicios"))


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

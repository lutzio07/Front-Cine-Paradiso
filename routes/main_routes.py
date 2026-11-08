from flask import Blueprint, flash, render_template, request, session, redirect, url_for
from services.api_client import (
    cancelar_compra as solicitar_cancelacion_compra,
    obtener_pelicula_por_id, 
    obtener_peliculas,
    obtener_funciones,
    obtener_sucursales,
    obtener_funcion_por_id,
    obtener_servicios,
    crear_compra,
    obtener_compra_por_id,
)
from services.cartelera_service import armar_cartelera
from datetime import datetime
from requests.exceptions import RequestException
from services.perfil_service import obtener_perfil
main_bp = Blueprint("main", __name__)

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


@main_bp.route("/checkout/funcion/<int:id_funcion>", methods=["GET", "POST"])
def checkout(id_funcion):
    if not session.get("backend_session"):
        flash("Iniciá sesión para continuar con la compra.", "warning")
        return redirect(url_for("main.index"))

    try:
        funcion = obtener_funcion_por_id(id_funcion)
        servicios = obtener_servicios()
    except Exception:
        flash("No se pudo cargar el resumen de la compra.", "danger")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        accion = request.form.get("accion")

        if accion == "abandonar":
            flash("Compra abandonada.", "info")
            return redirect(url_for("main.index"))

# Recopilar servicios seleccionados
        servicios_data = []
        for key, value in request.form.items():
            if key.startswith("servicio_"):
                sid = key.replace("servicio_", "")
                cant = int(value)
                if cant > 0:
                    servicios_data.append({"id_servicio": int(sid), "cantidad": cant})

        try:
            resultado = crear_compra(id_funcion, servicios_data)
            id_compra = resultado.get("data", {}).get("compra", {}).get("id_compra")
            if id_compra is None:
                id_compra = resultado.get("id_compra")
            if id_compra is None:
                flash("No se pudo crear la compra. Intentá de nuevo.", "danger")
                return render_template("pages/checkout.html", funcion=funcion, servicios=servicios, error=True)
            return redirect(url_for("main.comprobante", id_compra=id_compra))
        except Exception as e:
            if "No hay asientos disponibles" in str(e):
                flash("No hay asientos disponibles para esta función.", "danger")
            else:
                flash("No se pudo crear la compra. Intentá de nuevo.", "danger")
            return render_template("pages/checkout.html", funcion=funcion, servicios=servicios, error=True)

    return render_template("pages/checkout.html", funcion=funcion, servicios=servicios, error=False)


@main_bp.route("/comprobante/<int:id_compra>")
def comprobante(id_compra):
    if not session.get("backend_session"):
        flash("Iniciá sesión para ver el comprobante.", "warning")
        return redirect(url_for("main.index"))

    try:
        compra = obtener_compra_por_id(id_compra)
    except Exception:
        flash("No se pudo cargar el comprobante.", "danger")
        return redirect(url_for("main.index"))

# Obtener datos de la función desde la primera entrada
    funcion = None
    if compra.get("entradas") and compra["entradas"]:
        id_funcion = compra["entradas"][0].get("id_funcion")
        if id_funcion:
            try:
                funcion = obtener_funcion_por_id(id_funcion)
            except Exception:
                pass

    return render_template("pages/comprobante.html", compra=compra, funcion=funcion)
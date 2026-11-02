from flask import Blueprint, render_template, request
from services.api_client import (
    obtener_pelicula_por_id, 
    obtener_peliculas,
    obtener_funciones,
    obtener_sucursales,
    )
from services.cartelera_service import armar_cartelera
from datetime import datetime
from requests.exceptions import RequestException

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

@main_bp.app_template_filter("datetimeformat")
def datetimeformat(value, formato="%d/%m/%Y %H:%M"):
    try:
        fecha = datetime.fromisoformat(value)
        return fecha.strftime(formato)
    except (ValueError, TypeError):
        return value
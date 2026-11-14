from datetime import datetime, timedelta, timezone

from flask import (
    Blueprint,
    Response,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from services.admin_service import (
    buscar_peliculas_tmdb as servicio_buscar_peliculas_tmdb,
    crear_funcion as servicio_crear_funcion,
    crear_sala as servicio_crear_sala,
    eliminar_funcion as servicio_eliminar_funcion,
    eliminar_sala as servicio_eliminar_sala,
    importar_pelicula as servicio_importar_pelicula,
    obtener_datos_backoffice_peliculas,
    obtener_servicios,
    validar_codigo_qr as servicio_validar_codigo_qr, consultar_lista,
)

from services.estadisticas_service import (
    consultar_estadistica,
    obtener_estadistica,
    obtener_pdf,
)


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


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


@admin_bp.route("/peliculas", methods=["GET"], endpoint="peliculas")
@admin_bp.route("/cargar-pelicula", methods=["GET"], endpoint="admin_salas_funciones")
@admin_bp.route("/", methods=["GET"])
def peliculas():

    if not es_admin():
        flash(
            "Acceso denegado. Se requieren permisos de administrador.",
            "error"
        )
        return redirect(url_for("auth.vista_login"))

    sucursales, salas, peliculas_list, funciones = (
        obtener_datos_backoffice_peliculas()
    )

    busqueda_tmdb = request.args.get("busqueda_tmdb", "").strip()
    resultados_tmdb = []
    if busqueda_tmdb:
        resultados_tmdb, error_tmdb = servicio_buscar_peliculas_tmdb(busqueda_tmdb)
        if error_tmdb:
            flash(error_tmdb, "error")

    titulos_catalogo = {
        p.get("titulo", "").strip().lower()
        for p in peliculas_list
        if isinstance(p, dict) and p.get("titulo")
    }

    return render_template(
        "pages/admin_cargar_pelicula.html",
        section="admin",
        active="peliculas",
        sucursales=sucursales,
        salas=salas,
        peliculas=peliculas_list,
        funciones=funciones,
        busqueda_tmdb=busqueda_tmdb,
        resultados_tmdb=resultados_tmdb,
        titulos_catalogo=titulos_catalogo,
    )


@admin_bp.get("/dashboard")
def dashboard():
    if not es_admin():
        flash(
            "Acceso denegado. Se requieren permisos de administrador.",
            "error"
        )
        resultado = redirect(url_for("auth.vista_login"))

    else:
        filtros = {}
        errores_filtros = []

        for nombre in ("id_pelicula", "id_funcion"):
            valores = request.args.getlist(nombre)
            valor = valores[0].strip() if valores else ""

            filtro_invalido = (
                len(valores) > 1
                or (
                    valor
                    and (
                        not valor.isascii()
                        or not valor.isdecimal()
                        or int(valor) <= 0
                    )
                )
            )

            if filtro_invalido:
                errores_filtros.append(nombre)

            elif valor:
                filtros[nombre] = int(valor)

        campos_ocupacion = {
            "id_funcion": "numero",
            "titulo_pelicula": "texto",
            "nombre_sala": "texto",
            "fecha_hora": "texto",
            "capacidad": "numero",
            "entradas_vendidas": "numero",
            "porcentaje_ocupacion": "numero",
        }

        if errores_filtros:
            ocupacion = None
            error_ocupacion = (
                "Los filtros deben ser enteros positivos. "
                "Revisá los valores ingresados."
            )

        else:
            ocupacion, error_ocupacion = obtener_estadistica(
                "estadisticas/ocupacion",
                campos_ocupacion,
                filtros
            )

        ventas, error_ventas = obtener_estadistica(
            "estadisticas/ventas-por-genero",
            {
                "genero": "texto",
                "total_ventas": "numero",
            }
        )

        franjas, error_franjas = obtener_estadistica(
            "estadisticas/franjas-horarias",
            {
                "hora": "texto",
                "entradas_vendidas": "numero",
            }
        )

        cancelaciones, error_cancelaciones = obtener_estadistica(
            "estadisticas/cancelaciones",
            {
                "total_cancelaciones": "numero",
            },
            lista=False
        )

        peliculas_lista, error_peliculas = consultar_estadistica(
            "peliculas"
        )

        funciones_lista, error_funciones = consultar_estadistica(
            "funciones"
        )

        resultado = render_template(
            "pages/admin_dashboard.html",
            ocupacion=ocupacion,
            error_ocupacion=error_ocupacion,
            ventas_por_genero=ventas,
            error_ventas=error_ventas,
            franjas=franjas,
            error_franjas=error_franjas,
            cancelaciones=cancelaciones,
            error_cancelaciones=error_cancelaciones,
            peliculas=peliculas_lista or [],
            funciones=funciones_lista or [],
            error_peliculas=error_peliculas,
            error_funciones=error_funciones,
            filtros=filtros
        )

    return resultado


@admin_bp.get("/estadisticas/reporte-pdf")
def reporte_pdf():
    if not es_admin():
        flash("Sesión expirada o sin permisos. Iniciá sesión nuevamente.", "error")
        return redirect(url_for("auth.vista_login"))

    contenido, error, estado = obtener_pdf()

    if error:
        flash(error, "error")
        return redirect(url_for("admin.dashboard"))

    return Response(
        contenido,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": (
                'attachment; filename="reporte-cine-paradiso.pdf"'
            )
        }
    )


@admin_bp.route("/servicios", methods=["GET"], endpoint="servicios")
def servicios():

    if not es_admin():
        flash(
            "Acceso denegado. Se requieren permisos de administrador.",
            "error"
        )
        return redirect(url_for("auth.vista_login"))

    servicios_list = obtener_servicios()

    return render_template(
        "pages/admin_abm_servicios.html",
        section="admin",
        active="servicios",
        servicios=servicios_list,
    )


@admin_bp.route("/validador", methods=["GET"], endpoint="validador")
def validador():

    if not es_admin():
        flash(
            "Acceso denegado. Se requieren permisos de administrador.",
            "error"
        )
        return redirect(url_for("auth.vista_login"))

    funciones, _ = consultar_lista("/funciones", "funciones")

    return render_template(
        "pages/admin_validador.html",
        section="admin",
        active="validador",
        funciones=funciones,
        resultado=None,
        mensaje=None,
        datos=None,
        tipo=None,
    )

@admin_bp.route("/validador", methods=["POST"], endpoint="validador_post")
def validador_post():
    from flask import current_app

    if not es_admin():
        flash("Acceso no autorizado.", "error")
        return redirect(url_for("auth.vista_login"))

    codigo_qr = request.form.get("codigo_qr", "").strip()
    id_funcion_raw = request.form.get("id_funcion", "").strip()

    if not codigo_qr:
        funciones, _ = consultar_lista("/funciones", "funciones")
        return render_template(
            "pages/admin_validador.html",
            section="admin",
            active="validador",
            funciones=funciones,
            resultado=False,
            mensaje="Ingresá el código QR.",
            datos=None,
            tipo="denegado",
        )

    if not id_funcion_raw:
        funciones, _ = consultar_lista("/funciones", "funciones")
        return render_template(
            "pages/admin_validador.html",
            section="admin",
            active="validador",
            funciones=funciones,
            resultado=False,
            mensaje="Seleccioná una función.",
            datos=None,
            tipo="denegado",
        )

    try:
        id_funcion = int(id_funcion_raw)
    except ValueError:
        funciones, _ = consultar_lista("/funciones", "funciones")
        return render_template(
            "pages/admin_validador.html",
            section="admin",
            active="validador",
            funciones=funciones,
            resultado=False,
            mensaje="El ID de función debe ser un número válido.",
            datos=None,
            tipo="denegado",
        )

    exito, mensaje_servicio, datos = servicio_validar_codigo_qr(codigo_qr, id_funcion)

    funciones, _ = consultar_lista("/funciones", "funciones")

    return render_template(
        "pages/admin_validador.html",
        section="admin",
        active="validador",
        funciones=funciones,
        resultado=exito,
        mensaje=mensaje_servicio,
        datos=datos,
        tipo="permitido" if exito else "denegado",
    )

@admin_bp.route("/salas", methods=["POST"], endpoint="crear_sala")
def crear_sala():

    if not es_admin():
        flash("Acceso no autorizado.", "error")
        return redirect(url_for("auth.vista_login"))

    if not session.get("backend_session"):
        flash(
            "Falta la sesión del backend. Iniciá sesión nuevamente.",
            "error"
        )
        return redirect(url_for("admin.peliculas"))

    id_sucursal = request.form.get("id_sucursal", "").strip()
    nombre = request.form.get("nombre", "").strip()

    try:
        capacidad = int(request.form.get("capacidad", ""))

    except ValueError:
        flash("La capacidad debe ser un número entero.", "error")
        return redirect(url_for("admin.peliculas"))

    exito, mensaje = servicio_crear_sala(
        id_sucursal,
        nombre,
        capacidad
    )

    if exito:
        flash(mensaje, "success")
    else:
        flash(mensaje, "error")

    return redirect(url_for("admin.peliculas"))


@admin_bp.route("/funciones", methods=["POST"], endpoint="crear_funcion")
def crear_funcion():

    if not es_admin():
        flash("Acceso no autorizado.", "error")
        return redirect(url_for("auth.vista_login"))

    if not session.get("backend_session"):
        flash(
            "Falta la sesión del backend. Iniciá sesión nuevamente.",
            "error"
        )
        return redirect(url_for("admin.peliculas"))

    try:
        id_pelicula = int(request.form.get("id_pelicula", ""))
        id_sala = int(request.form.get("id_sala", ""))
        precio = float(request.form.get("precio_entrada", ""))

        fecha_local = datetime.fromisoformat(
            request.form.get("fecha_hora", "")
        )

        if fecha_local.tzinfo is not None:
            raise ValueError("Fecha con zona inesperada")

        zona_argentina = timezone(timedelta(hours=-3))
        fecha_argentina = fecha_local.replace(
            tzinfo=zona_argentina
        )

    except (ValueError, TypeError):
        flash(
            "Revisá la película, la sala, la fecha/hora y el precio.",
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

    exito, mensaje = servicio_crear_funcion(payload)

    if exito:
        flash(mensaje, "success")
    else:
        flash(mensaje, "error")

    return redirect(url_for("admin.peliculas"))


@admin_bp.route(
    "/salas/eliminar/<int:id_sucursal>/<int:id_sala>",
    methods=["POST"],
    endpoint="eliminar_sala",
)
def eliminar_sala(id_sucursal, id_sala):

    if not es_admin():
        flash("Acceso no autorizado.", "error")
        return redirect(url_for("auth.vista_login"))

    if not session.get("backend_session"):
        flash(
            "Falta la sesión del backend. Iniciá sesión nuevamente.",
            "error"
        )
        return redirect(url_for("admin.peliculas"))

    exito, mensaje = servicio_eliminar_sala(
        id_sucursal,
        id_sala
    )

    if exito:
        flash(mensaje, "success")
    else:
        flash(mensaje, "error")

    return redirect(url_for("admin.peliculas"))


@admin_bp.route(
    "/funciones/eliminar/<int:id_funcion>",
    methods=["POST"],
    endpoint="eliminar_funcion",
)
def eliminar_funcion(id_funcion):

    if not es_admin():
        flash("Acceso no autorizado.", "error")
        return redirect(url_for("auth.vista_login"))

    if not session.get("backend_session"):
        flash(
            "Falta la sesión del backend. Iniciá sesión nuevamente.",
            "error"
        )
        return redirect(url_for("admin.peliculas"))

    exito, mensaje = servicio_eliminar_funcion(id_funcion)

    if exito:
        flash(mensaje, "success")
    else:
        flash(mensaje, "error")

    return redirect(url_for("admin.peliculas"))


@admin_bp.route("/peliculas", methods=["POST"], endpoint="importar_pelicula")
def importar_pelicula():

    if not es_admin():
        flash("Acceso no autorizado.", "error")
        return redirect(url_for("auth.vista_login"))

    if not session.get("backend_session"):
        flash(
            "Falta la sesión del backend. Iniciá sesión nuevamente.",
            "error"
        )
        return redirect(url_for("admin.peliculas"))

    titulo = request.form.get("titulo", "").strip()
    if not titulo:
        flash("El título de la película es obligatorio.", "error")
        return redirect(url_for("admin.peliculas"))

    try:
        duracion_min = int(request.form.get("duracion_min", 120))
        if duracion_min <= 0:
            duracion_min = 120
    except (ValueError, TypeError):
        duracion_min = 120

    payload = {
        "titulo": titulo,
        "sinopsis": request.form.get("sinopsis", "").strip() or None,
        "poster_url": request.form.get("poster_url", "").strip() or None,
        "genero": request.form.get("genero", "").strip() or "General",
        "duracion_min": duracion_min,
        "clasificacion": request.form.get("clasificacion", "").strip() or "ATP",
    }

    exito, mensaje = servicio_importar_pelicula(payload)

    if exito:
        flash(mensaje, "success")
    else:
        flash(mensaje, "error")

    busqueda_actual = request.form.get("busqueda_tmdb", "").strip()
    if busqueda_actual:
        return redirect(url_for("admin.peliculas", busqueda_tmdb=busqueda_actual))

    return redirect(url_for("admin.peliculas"))

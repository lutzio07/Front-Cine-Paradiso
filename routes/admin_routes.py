from datetime import datetime, timedelta, timezone

from flask import (
    Blueprint,
    Response,
    jsonify,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from services.admin_service import (
    crear_funcion as servicio_crear_funcion,
    crear_sala as servicio_crear_sala,
    eliminar_funcion as servicio_eliminar_funcion,
    eliminar_sala as servicio_eliminar_sala,
    obtener_datos_backoffice_peliculas,
    obtener_servicios,
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

    return render_template(
        "pages/admin_cargar_pelicula.html",
        section="admin",
        active="peliculas",
        sucursales=sucursales,
        salas=salas,
        peliculas=peliculas_list,
        funciones=funciones,
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
        resultado = (
            jsonify(
                error="Sesión expirada o sin permisos. Iniciá sesión nuevamente."
            ),
            403
        )

    else:
        contenido, error, estado = obtener_pdf()

        if error:
            resultado = (
                jsonify(error=error),
                estado
            )

        else:
            resultado = Response(
                contenido,
                mimetype="application/pdf",
                headers={
                    "Content-Disposition": (
                        'attachment; filename="reporte-cine-paradiso.pdf"'
                    )
                }
            )

    return resultado


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

    return render_template(
        "pages/admin_validador.html",
        section="admin",
        active="validador",
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
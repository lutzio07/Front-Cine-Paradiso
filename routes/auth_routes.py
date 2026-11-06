from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from services.auth_service import cerrar_sesion, iniciar_sesion, registrar_usuario

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/registro", methods=["GET", "POST"])
def vista_registro():

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        exito, mensaje = registrar_usuario(nombre, email, password)

        if exito:
            flash(mensaje, "success")
            return redirect(url_for("auth.vista_login"))

        flash(mensaje, "danger")

    return render_template( "pages/login_registro.html", modo="registro" )


@auth_bp.route("/login", methods=["GET", "POST"])
def vista_login():

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        exito, usuario, cookie_backend, mensaje_error = iniciar_sesion( email, password)

        if exito and usuario and cookie_backend:
            session.clear()

            session["id_usuario"] = usuario["id_usuario"]
            session["nombre"] = usuario["nombre"]
            session["rol"] = usuario["rol"]
            session["backend_session"] = cookie_backend

            flash(f"¡Bienvenido, {usuario['nombre']}!", "success")
            return redirect(url_for("main.index"))

        flash(mensaje_error, "danger")

    return render_template( "pages/login_registro.html", modo="login" )


@auth_bp.post("/logout")
def vista_logout():

    cookie_backend = session.get("backend_session")
    cierre_confirmado = cerrar_sesion(cookie_backend)

    session.clear()

    if cierre_confirmado:
        flash("Sesión cerrada.", "info")
    else:
        flash( "Se cerró la sesión local, pero no se pudo " "confirmar el cierre en el Backend.", "warning" )

    return redirect(url_for("auth.vista_login"))
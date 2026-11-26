from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from services.recuperacion_service import (
    restablecer_password,
    solicitar_recuperacion_password,
)

recuperacion_bp = Blueprint("recuperacion", __name__)


@recuperacion_bp.route("/recuperar-password", methods=["GET", "POST"])
def vista_recuperar_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        frontend_url = request.host_url.rstrip("/")

        exito, mensaje = solicitar_recuperacion_password(email, frontend_url)

        if exito:
            flash(mensaje, "success")
            return redirect(url_for("auth.vista_login"))

        flash(mensaje, "danger")

    return render_template("pages/recuperar_password.html")


@recuperacion_bp.route("/restablecer-password/<token>", methods=["GET", "POST"])
def vista_restablecer_password(token):
    if request.method == "POST":
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")

        if password != password_confirm:
            flash("Las contraseñas no coinciden.", "danger")
            return render_template("pages/restablecer_password.html", token=token)

        exito, mensaje = restablecer_password(token, password)

        if exito:
            flash(mensaje, "success")
            return redirect(url_for("auth.vista_login"))

        flash(mensaje, "danger")

    return render_template("pages/restablecer_password.html", token=token)
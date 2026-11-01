import requests
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)


auth_bp = Blueprint("auth", __name__)


def json_seguro(respuesta):
    try:
        datos = respuesta.json()
    except ValueError:
        return {}
    return datos if isinstance(datos, dict) else {}


@auth_bp.route("/registro", methods=["GET", "POST"])
def vista_registro():
    if request.method == "POST":
        payload = {
            "nombre": request.form.get("nombre", "").strip(),
            "email": request.form.get("email", "").strip(),
            "password": request.form.get("password", ""),
        }

        try:
            respuesta = requests.post(
                f"{current_app.config['BACKEND_URL']}/api/usuarios",
                json=payload,
                timeout=5,
            )
            datos = json_seguro(respuesta)
            if respuesta.status_code == 201 and datos.get("status") == "success":
                flash("Cuenta creada. Ahora podés iniciar sesión.", "success")
                return redirect(url_for("auth.vista_login"))

            flash(datos.get("message", "No se pudo registrar la cuenta."), "danger")
        except requests.RequestException:
            flash("No se pudo conectar con el Backend.", "danger")

    return render_template("pages/login_registro.html", modo="registro")


@auth_bp.route("/login", methods=["GET", "POST"])
def vista_login():
    if request.method == "POST":
        payload = {
            "email": request.form.get("email", "").strip(),
            "password": request.form.get("password", ""),
        }

        try:
            respuesta = requests.post(
                f"{current_app.config['BACKEND_URL']}/api/sesiones",
                json=payload,
                timeout=5,
            )
            datos = json_seguro(respuesta)

            if respuesta.status_code == 200 and datos.get("status") == "success":
                usuario = datos.get("data")
                cookie_backend = respuesta.cookies.get("session")

                if (
                    isinstance(usuario, dict)
                    and usuario.get("id_usuario")
                    and usuario.get("nombre")
                    and usuario.get("rol") in ("CLIENTE", "ADMIN")
                    and cookie_backend
                ):
                    session.clear()
                    session["id_usuario"] = usuario["id_usuario"]
                    session["nombre"] = usuario["nombre"]
                    session["rol"] = usuario["rol"]
                    session["backend_session"] = cookie_backend

                    flash(f"¡Bienvenido, {usuario['nombre']}!", "success")
                    return redirect(url_for("main.index"))

                flash("El Backend devolvió una sesión incompleta.", "danger")
            else:
                flash(datos.get("message", "Credenciales incorrectas."), "danger")
        except requests.RequestException:
            flash("No se pudo conectar con el Backend.", "danger")

    return render_template("pages/login_registro.html", modo="login")


@auth_bp.post("/logout")
def vista_logout():
    cookie_backend = session.get("backend_session")
    cierre_confirmado = False

    if cookie_backend:
        try:
            respuesta = requests.delete(
                f"{current_app.config['BACKEND_URL']}/api/sesiones",
                cookies={"session": cookie_backend},
                timeout=5,
            )
            cierre_confirmado = respuesta.status_code in (200,204, 401)
        except requests.RequestException:
            pass

    session.clear()
    if cierre_confirmado:
        flash("Sesión cerrada.", "info")
    else:
        flash(
            "Se cerró la sesión local, pero no se pudo confirmar el cierre en el Backend.",
            "warning",
        )
    return redirect(url_for("auth.vista_login"))

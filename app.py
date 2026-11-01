import os
from flask import Flask
from config import get_config
from routes.main_routes import main_bp
from routes.auth_routes import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(get_config())

    frontend_secret = os.getenv("FRONTEND_SECRET_KEY")
    if frontend_secret:
        app.config["SECRET_KEY"] = frontend_secret

    if app.config.get("BACKEND_URL"):
        app.config["BACKEND_URL"] = app.config["BACKEND_URL"].rstrip("/")

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("Configurá FRONTEND_SECRET_KEY o SECRET_KEY en el entorno")

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    return app

if __name__ == "__main__":
    create_app().run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5001")),
        debug=True
    )

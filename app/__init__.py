from flask import Flask


def create_app():
    app = Flask(
        __name__, template_folder="views/templates", static_folder="views/static"
    )

    from app.routes.demoRoute import demo_bp

    app.register_blueprint(demo_bp)

    return app

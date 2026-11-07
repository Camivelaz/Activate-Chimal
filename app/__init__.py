import os
from flask import Flask
from config import Config
from database import close_db, init_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    app.teardown_appcontext(close_db)

    from app.routes.main import main
    from app.routes.auth import auth
    from app.routes.profile import profile

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(profile)

    with app.app_context():
        init_db()

    return app
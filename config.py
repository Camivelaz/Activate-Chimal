import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "activate-chimal-clave-local-cambiar-en-produccion"
    )

    DATABASE = os.path.join(
        BASE_DIR,
        "instance",
        "activate_chimal.db"
    )

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "app",
        "static",
        "uploads",
        "perfiles"
    )

    MAX_CONTENT_LENGTH = 3 * 1024 * 1024
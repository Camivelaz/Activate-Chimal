import os
import json
import uuid

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, current_app
)

from werkzeug.utils import secure_filename
from database import get_db

profile = Blueprint("profile", __name__)

EXTENSIONES = {"jpg", "jpeg", "png", "webp"}

ROPA = {"playera", "sudadera", "uniforme", "pantalon"}

COLORES = {
    "azul", "celeste", "morado",
    "naranja", "verde", "negro"
}

ACCESORIOS = {
    "ninguno", "gorra", "lentes", "mochila",
    "audifonos", "muñequera", "gorra_deportiva"
}


def obtener_usuario():
    if "usuario_id" not in session:
        return None

    return get_db().execute(
        "SELECT * FROM usuarios WHERE id = ?",
        (session["usuario_id"],)
    ).fetchone()


def obtener_carpeta_fotos():
    carpeta = current_app.config.get("UPLOAD_FOLDER")

    if not carpeta:
        carpeta = os.path.join(
            current_app.static_folder,
            "uploads"
        )

    os.makedirs(carpeta, exist_ok=True)

    return carpeta


@profile.route("/perfil")
def perfil():
    usuario = obtener_usuario()

    if usuario is None:
        return redirect(url_for("auth.login"))

    try:
        avatar = json.loads(usuario["avatar_json"] or "{}")
    except (ValueError, TypeError):
        avatar = {}

    return render_template(
        "perfil.html",
        usuario=usuario,
        avatar=avatar
    )


@profile.route("/perfil/foto", methods=["POST"])
def foto():
    usuario = obtener_usuario()

    if usuario is None:
        return redirect(url_for("auth.login"))

    archivo = request.files.get("foto")

    if not archivo or not archivo.filename:
        flash("Selecciona una fotografía.", "error")
        return redirect(url_for("profile.perfil"))

    nombre = secure_filename(archivo.filename)

    if "." not in nombre:
        flash("El archivo no es válido.", "error")
        return redirect(url_for("profile.perfil"))

    extension = nombre.rsplit(".", 1)[1].lower()

    if extension not in EXTENSIONES:
        flash(
            "Utiliza una imagen JPG, JPEG, PNG o WEBP.",
            "error"
        )
        return redirect(url_for("profile.perfil"))

    carpeta = obtener_carpeta_fotos()

    nuevo_nombre = f"{uuid.uuid4().hex}.{extension}"
    destino = os.path.join(carpeta, nuevo_nombre)

    try:
        archivo.save(destino)

        db = get_db()
        anterior = usuario["foto_perfil"]

        db.execute(
            "UPDATE usuarios SET foto_perfil = ? WHERE id = ?",
            (nuevo_nombre, usuario["id"])
        )

        db.commit()

        # Eliminar la fotografía anterior si existe.
        if anterior:
            ruta_anterior = os.path.join(
                carpeta,
                os.path.basename(anterior)
            )

            if os.path.isfile(ruta_anterior):
                os.remove(ruta_anterior)

        flash("¡Tu fotografía se actualizó correctamente!", "success")

    except Exception as error:
        if os.path.isfile(destino):
            os.remove(destino)

        current_app.logger.exception(
            "Error al guardar la fotografía: %s", error
        )

        flash(
            "No se pudo guardar la fotografía. Inténtalo nuevamente.",
            "error"
        )

    return redirect(url_for("profile.perfil"))


@profile.route("/perfil/avatar", methods=["POST"])
def guardar_avatar():
    usuario = obtener_usuario()

    if usuario is None:
        return redirect(url_for("auth.login"))

    ropa = request.form.get("ropa", "playera")
    color = request.form.get("color", "azul")
    accesorio = request.form.get("accesorio", "ninguno")

    if ropa not in ROPA:
        ropa = "playera"

    if color not in COLORES:
        color = "azul"

    if accesorio not in ACCESORIOS:
        accesorio = "ninguno"

    avatar = {
        "ropa": ropa,
        "color": color,
        "accesorio": accesorio
    }

    db = get_db()

    db.execute(
        "UPDATE usuarios SET avatar_json = ? WHERE id = ?",
        (json.dumps(avatar), usuario["id"])
    )

    db.commit()

    flash("¡Tu avatar se actualizó!", "success")

    return redirect(url_for("profile.perfil"))
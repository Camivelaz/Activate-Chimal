import re
import sqlite3
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session
)
from werkzeug.security import (
    generate_password_hash, check_password_hash
)
from database import get_db

auth = Blueprint("auth", __name__)


@auth.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        usuario = request.form.get("usuario", "").strip()
        correo = request.form.get("correo", "").strip().lower()
        password = request.form.get("password", "")
        confirmar = request.form.get("confirmar", "")

        if not all([nombre, usuario, correo, password, confirmar]):
            flash("Completa todos los campos.", "error")
            return redirect(url_for("auth.registro"))

        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", correo):
            flash("Escribe un correo válido.", "error")
            return redirect(url_for("auth.registro"))

        if len(password) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "error")
            return redirect(url_for("auth.registro"))

        if password != confirmar:
            flash("Las contraseñas no coinciden.", "error")
            return redirect(url_for("auth.registro"))

        db = get_db()

        try:
            cursor = db.execute("""
                INSERT INTO usuarios
                (nombre, usuario, correo, password_hash)
                VALUES (?, ?, ?, ?)
            """, (
                nombre, usuario, correo,
                generate_password_hash(password)
            ))

            db.commit()
            session.clear()
            session["usuario_id"] = cursor.lastrowid

            flash("¡Tu cuenta fue creada!", "success")
            return redirect(url_for("main.dashboard"))

        except sqlite3.IntegrityError:
            flash("Ese usuario o correo ya está registrado.", "error")

    return render_template("registro.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identificador = request.form.get("identificador", "").strip()
        password = request.form.get("password", "")

        db = get_db()

        usuario = db.execute("""
            SELECT * FROM usuarios
            WHERE usuario = ? OR correo = ?
        """, (identificador, identificador.lower())).fetchone()

        if usuario and check_password_hash(
            usuario["password_hash"], password
        ):
            session.clear()
            session["usuario_id"] = usuario["id"]

            flash("Bienvenido a Actívate + Chimal.", "success")
            return redirect(url_for("main.dashboard"))

        flash("Usuario o contraseña incorrectos.", "error")

    return render_template("login.html")


@auth.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión.", "success")
    return redirect(url_for("main.index"))
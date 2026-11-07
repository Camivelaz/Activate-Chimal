import sqlite3
import os
from flask import current_app, g


def get_db():
    if "db" not in g:
        database_path = current_app.config["DATABASE"]

        os.makedirs(os.path.dirname(database_path), exist_ok=True)

        g.db = sqlite3.connect(database_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


def close_db(error=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def agregar_columna(db, tabla, columna, tipo):
    columnas = [
        fila["name"]
        for fila in db.execute(f"PRAGMA table_info({tabla})").fetchall()
    ]

    if columna not in columnas:
        db.execute(
            f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}"
        )


def init_db():
    db = get_db()

    # =================================
    # USUARIOS
    # Conserva los usuarios registrados
    # =================================

    db.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            usuario TEXT NOT NULL UNIQUE,
            correo TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            foto_perfil TEXT,
            avatar_json TEXT DEFAULT '{}',
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Compatibilidad con bases anteriores
    agregar_columna(db, "usuarios", "foto_perfil", "TEXT")
    agregar_columna(db, "usuarios", "avatar_json", "TEXT DEFAULT '{}'")

    # =================================
    # CANCHAS Y ESPACIOS
    # =================================

    db.execute("""
        CREATE TABLE IF NOT EXISTS canchas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            deporte TEXT NOT NULL,
            descripcion TEXT,
            disponible INTEGER DEFAULT 1
        )
    """)

    # =================================
    # RESERVACIONES
    # =================================

    db.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            cancha_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fin TEXT NOT NULL,
            estado TEXT DEFAULT 'pendiente',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (cancha_id) REFERENCES canchas(id)
        )
    """)

    # =================================
    # ACTIVIDADES Y EVENTOS
    # =================================

    db.execute("""
        CREATE TABLE IF NOT EXISTS actividades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            categoria TEXT,
            fecha TEXT,
            hora TEXT,
            lugar TEXT,
            cupo INTEGER DEFAULT 30,
            estado TEXT DEFAULT 'activo'
        )
    """)

    # =================================
    # ASISTENCIA Y RACHA DIARIA
    # =================================

    db.execute("""
        CREATE TABLE IF NOT EXISTS asistencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            actividad TEXT DEFAULT 'Actividad deportiva',
            puntos INTEGER DEFAULT 10,

            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            UNIQUE(usuario_id, fecha)
        )
    """)

    # =================================
    # RETOS
    # =================================

    db.execute("""
        CREATE TABLE IF NOT EXISTS retos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            meta INTEGER DEFAULT 1,
            puntos INTEGER DEFAULT 20,
            categoria TEXT DEFAULT 'General',
            activo INTEGER DEFAULT 1
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS usuario_retos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            reto_id INTEGER NOT NULL,
            progreso INTEGER DEFAULT 0,
            completado INTEGER DEFAULT 0,

            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (reto_id) REFERENCES retos(id),
            UNIQUE(usuario_id, reto_id)
        )
    """)

    # =================================
    # AVISOS
    # =================================

    db.execute("""
        CREATE TABLE IF NOT EXISTS avisos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            categoria TEXT DEFAULT 'General',
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            activo INTEGER DEFAULT 1
        )
    """)

    # =================================
    # REPORTES
    # =================================

    db.execute("""
        CREATE TABLE IF NOT EXISTS reportes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            asunto TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            estado TEXT DEFAULT 'recibido',
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    # =================================
    # COMUNIDAD
    # =================================

    db.execute("""
        CREATE TABLE IF NOT EXISTS testimonios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            mensaje TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    # =================================
    # NOTIFICACIONES
    # =================================

    db.execute("""
        CREATE TABLE IF NOT EXISTS notificaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            mensaje TEXT NOT NULL,
            leida INTEGER DEFAULT 0,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    # =================================
    # ÍNDICES
    # =================================

    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_reservas_fecha
        ON reservas(fecha, cancha_id)
    """)

    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_asistencia_usuario
        ON asistencia(usuario_id, fecha)
    """)

    # =================================
    # ESPACIOS DE EJEMPLO
    # =================================

    canchas = [
        ("Cancha de fútbol", "Fútbol",
         "Espacio para practicar fútbol."),
        ("Cancha de básquetbol", "Básquetbol",
         "Espacio para practicar básquetbol."),
        ("Cancha de voleibol", "Voleibol",
         "Espacio para practicar voleibol."),
        ("Área de ejercicio", "Acondicionamiento físico",
         "Zona para actividad física."),
        ("Pista deportiva", "Atletismo",
         "Espacio para correr y caminar.")
    ]

    db.executemany("""
        INSERT INTO canchas (nombre, deporte, descripcion)
        SELECT ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM canchas WHERE nombre = ?
        )
    """, [
        (nombre, deporte, descripcion, nombre)
        for nombre, deporte, descripcion in canchas
    ])

    # =================================
    # RETOS DE EJEMPLO
    # =================================

    retos = [
        (
            "Primeros pasos",
            "Registra tu primera actividad deportiva.",
            1, 20, "Principiante"
        ),
        (
            "Semana activa",
            "Realiza actividad durante tres días diferentes.",
            3, 50, "Constancia"
        ),
        (
            "En movimiento",
            "Participa en cinco actividades deportivas.",
            5, 80, "Actividad"
        ),
        (
            "Explora Tepalcates",
            "Conoce y utiliza dos espacios deportivos.",
            2, 40, "Exploración"
        )
    ]

    for reto in retos:
        db.execute("""
            INSERT INTO retos
            (titulo, descripcion, meta, puntos, categoria)
            SELECT ?, ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM retos WHERE titulo = ?
            )
        """, (*reto, reto[0]))

    db.commit()
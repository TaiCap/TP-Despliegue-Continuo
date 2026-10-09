import os

import sentry_sdk
from fastapi import FastAPI, HTTPException
from sqlalchemy import text

from database import SessionLocal, engine

# Conecta la app con Sentry. El DSN viene de una variable de entorno,
# así no queda escrito en el código (el repo es público).
# Si SENTRY_DSN no existe (por ejemplo en mi PC), Sentry simplemente no hace nada.
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENVIRONMENT", "production"),
)

app = FastAPI()

# Crea la tabla usuarios si no existe y carga los datos iniciales.
# Es lo mismo que hacía mysql/init.sql, pero lo hace el backend al arrancar.
def preparar_base():
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE IF NOT EXISTS usuarios ("
            "id INT AUTO_INCREMENT PRIMARY KEY, "
            "nombre VARCHAR(100) NOT NULL)"
        ))
        cantidad = conn.execute(text("SELECT COUNT(*) FROM usuarios")).scalar()
        if cantidad == 0:
            conn.execute(text(
                "INSERT INTO usuarios (nombre) VALUES ('Diego'), ('Ricardo')"
            ))


preparar_base()

@app.get("/")
def root():
    return {"mensaje": "Backend FastAPI funcionando"}


@app.get("/usuarios/{usuario_id}")
def obtener_usuario(usuario_id: int):
    db = SessionLocal()

    try:
        resultado = db.execute(
            text("SELECT id, nombre FROM usuarios WHERE id = :id"),
            {"id": usuario_id}
        ).mappings().first()

        if resultado is None:
            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado"
            )

        return {
            "id": resultado["id"],
            "nombre": resultado["nombre"]
        }

    finally:
        db.close()


# Endpoint para provocar un error a propósito (lo usamos en el video).
# Dividir por cero lanza una excepción que nadie atrapa, y Sentry la registra.
@app.get("/error")
def provocar_error():
    return 1 / 0

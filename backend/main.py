import os

import sentry_sdk
from fastapi import FastAPI, HTTPException
from sqlalchemy import text

from database import SessionLocal, engine

# Conecta la app con Sentry. El DSN se lee de la variable de entorno SENTRY_DSN;
# si no está configurada en la plataforma, usa el valor por defecto.
# El DSN solo permite ENVIAR errores, no acceder a la cuenta de Sentry.
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN","https://4902b70edc30a7b7aa21d73475c13a1a@o4512274304270336.ingest.us.sentry.io/4512274310627328"),
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

# Error de tipo: sumar un número con un texto.
# En Sentry aparece como TypeError.
@app.get("/error-tipo")
def error_tipo():
    return 5 + "texto"


# Error de clave: pedir una clave que no existe en un diccionario.
# En Sentry aparece como KeyError.
@app.get("/error-clave")
def error_clave():
    datos = {"nombre": "Diego"}
    return datos["edad"]


# Error de excepción propia: lanzamos una excepción con nuestro mensaje.
# En Sentry aparece como Exception con el texto que escribimos.
@app.get("/error-manual")
def error_manual():
    raise Exception("Error provocado a propósito para probar Sentry")


# Error de base de datos: consultamos una tabla que no existe.
# En Sentry aparece como ProgrammingError y muestra la consulta que falló.
@app.get("/error-db")
def error_db():
    db = SessionLocal()
    try:
        db.execute(text("SELECT * FROM tabla_que_no_existe"))
    finally:
        db.close()

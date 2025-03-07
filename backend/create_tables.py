import time
from sqlalchemy.exc import OperationalError
from database import engine
import models

def wait_for_db():
    max_retries = 10
    retry_delay = 2  # segundos
    
    for attempt in range(max_retries):
        try:
            print(f"Intento {attempt+1}/{max_retries} de conexión a la base de datos...")
            connection = engine.connect()
            connection.close()
            print("✅ Conexión a la base de datos exitosa")
            return True
        except OperationalError as e:
            print(f"⏳ Esperando a que la base de datos esté lista... ({e})")
            time.sleep(retry_delay)
    
    print("❌ No se pudo conectar a la base de datos después de varios intentos")
    return False

def create_tables():
    print("Creando tablas en la base de datos...")
    models.Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas correctamente")

if __name__ == "__main__":
    if wait_for_db():
        create_tables()
    else:
        exit(1) 
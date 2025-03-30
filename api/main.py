from fastapi import APIRouter, Depends, HTTPException, FastAPI
from sqlalchemy.orm import Session
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models import Paciente
from backend.database import get_db

# Crear la instancia de FastAPI
app = FastAPI()

# Nuevo endpoint para interoperabilidad
@app.get("/ficha-interoperable/{rut}")
def obtener_ficha_interoperable(rut: str, db: Session = Depends(get_db)):
    """Endpoint para integración con otros sistemas según normativa chilena"""
    paciente = db.query(Paciente).filter(Paciente.rut == rut).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Convertir a un formato de respuesta adecuado
    return {
        "rut": paciente.rut,
        "nombre": paciente.nombre if hasattr(paciente, 'nombre') else None,
        "apellido": paciente.apellido if hasattr(paciente, 'apellido') else None,
        "fecha_nacimiento": paciente.fecha_nacimiento if hasattr(paciente, 'fecha_nacimiento') else None,
        "sexo": paciente.sexo if hasattr(paciente, 'sexo') else None,
        "prevision": paciente.prevision if hasattr(paciente, 'prevision') else None,
        "contacto_emergencia": paciente.contacto_emergencia
    }

# Endpoint de health check
@app.get("/health")
def health_check():
    """Endpoint para verificar que el servicio está funcionando"""
    return {"status": "ok"}

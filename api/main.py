from fastapi import APIRouter, Depends, HTTPException, FastAPI
from sqlalchemy.orm import Session
from api import schemas, models
from api.database import get_db

# Crear la instancia de FastAPI
app = FastAPI()

# Nuevo endpoint para interoperabilidad
@app.get("/ficha-interoperable/{rut}", response_model=schemas.FichaCompleta)
def obtener_ficha_interoperable(rut: str, db: Session = Depends(get_db)):
    """Endpoint para integración con otros sistemas según normativa chilena"""
    paciente = db.query(models.Paciente).filter(models.Paciente.rut == rut).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return paciente 
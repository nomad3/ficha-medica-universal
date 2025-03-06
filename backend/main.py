from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from database import get_db, engine
import models
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import event
from sqlalchemy.exc import OperationalError
import time

# Definir modelos Pydantic primero
class PacienteBase(BaseModel):
    nombre: str
    apellido: str
    fecha_nacimiento: str
    sexo: str
    direccion: str
    telefono: str
    isapre: Optional[str] = None
    seguros_medicos: Optional[str] = None
    email: Optional[str] = None
    tipo_sangre: str
    alergias: str
    actividad_fisica: str
    dieta: str
    problema_salud_principal: str
    objetivo_suplementacion: str

class PacienteCreate(PacienteBase):
    rut: str
    contacto_emergencia: str
    consentimiento_datos: bool

class PacienteResponse(PacienteBase):
    id: int
    rut: str
    contacto_emergencia: str
    consentimiento_datos: bool

class HistorialMedicoBase(BaseModel):
    suplemento: str
    dosis: str
    fecha_inicio: str
    duracion: str
    colesterol_total: int
    trigliceridos: int
    vitamina_d: int
    omega3_indice: int
    observaciones: str

# Crear instancia de FastAPI después de los modelos
app = FastAPI(title="API Ficha Médica Nutricional")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def wait_for_db():
    max_retries = 5
    retry_delay = 3  # segundos
    for _ in range(max_retries):
        try:
            engine.connect()
            print("Conexión a la base de datos exitosa")
            return
        except OperationalError:
            print("Esperando a que la base de datos esté lista...")
            time.sleep(retry_delay)
    raise Exception("No se pudo conectar a la base de datos después de varios intentos")

# Llamar antes de crear las tablas
wait_for_db()
models.Base.metadata.create_all(bind=engine)

# ... resto del código de rutas ...

@app.post("/pacientes/", response_model=PacienteBase)
def crear_paciente(paciente: PacienteCreate, db: Session = Depends(get_db)):
    db_paciente = models.Paciente(**paciente.dict())
    db.add(db_paciente)
    db.commit()
    db.refresh(db_paciente)
    return db_paciente

@app.get("/pacientes/", response_model=List[PacienteResponse])
def listar_pacientes(db: Session = Depends(get_db)):
    return db.query(models.Paciente).all()

@app.get("/pacientes/{paciente_id}", response_model=PacienteResponse)
def obtener_paciente(paciente_id: int, db: Session = Depends(get_db)):
    paciente = db.query(models.Paciente).filter(models.Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return paciente

@app.post("/historial/{paciente_id}", response_model=HistorialMedicoBase)
def crear_registro_historial(
    paciente_id: int, 
    historial: HistorialMedicoBase, 
    db: Session = Depends(get_db)
):
    db_historial = models.HistorialMedico(
        paciente_id=paciente_id,
        **historial.dict()
    )
    db.add(db_historial)
    db.commit()
    db.refresh(db_historial)
    return db_historial 
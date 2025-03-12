from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from database import get_db, engine
import models
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import event
from sqlalchemy.exc import OperationalError
import time
from datetime import datetime

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

# Modelos FHIR
class FHIRPatient(BaseModel):
    resourceType: str = "Patient"
    id: str
    identifier: List[Dict[str, Any]]
    name: List[Dict[str, Any]]
    gender: str
    birthDate: str
    telecom: Optional[List[Dict[str, Any]]] = None
    address: Optional[List[Dict[str, Any]]] = None
    contact: Optional[List[Dict[str, Any]]] = None

class FHIRObservation(BaseModel):
    resourceType: str = "Observation"
    id: str
    status: str = "final"
    code: Dict[str, Any]
    subject: Dict[str, Any]
    effectiveDateTime: str
    valueQuantity: Dict[str, Any]

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

# Endpoints FHIR
@app.get("/fhir/Patient/{rut}", response_model=FHIRPatient)
def obtener_paciente_fhir(rut: str, db: Session = Depends(get_db)):
    """Endpoint para obtener paciente en formato FHIR"""
    paciente = db.query(models.Paciente).filter(models.Paciente.rut == rut).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Convertir a formato FHIR
    fhir_patient = {
        "resourceType": "Patient",
        "id": str(paciente.id),
        "identifier": [
            {
                "system": "http://minsal.cl/rut",
                "value": paciente.rut
            }
        ],
        "name": [
            {
                "family": paciente.apellido,
                "given": [paciente.nombre]
            }
        ],
        "gender": "male" if paciente.sexo.lower() == "masculino" else "female",
        "birthDate": paciente.fecha_nacimiento,
        "telecom": [
            {
                "system": "phone",
                "value": paciente.telefono
            }
        ],
        "address": [
            {
                "text": paciente.direccion
            }
        ],
        "contact": [
            {
                "relationship": [
                    {
                        "text": "Contacto de emergencia"
                    }
                ],
                "name": {
                    "text": paciente.contacto_emergencia
                }
            }
        ]
    }
    
    return fhir_patient

@app.get("/fhir/Observation/{paciente_id}", response_model=List[FHIRObservation])
def obtener_observaciones_fhir(paciente_id: int, db: Session = Depends(get_db)):
    """Endpoint para obtener observaciones en formato FHIR"""
    historial = db.query(models.HistorialMedico).filter(models.HistorialMedico.paciente_id == paciente_id).all()
    if not historial:
        return []
    
    observaciones = []
    for registro in historial:
        # Observación para colesterol
        if registro.colesterol_total:
            obs_colesterol = {
                "resourceType": "Observation",
                "id": f"col-{registro.id}",
                "status": "final",
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "2093-3",
                            "display": "Colesterol total"
                        }
                    ]
                },
                "subject": {
                    "reference": f"Patient/{paciente_id}"
                },
                "effectiveDateTime": registro.fecha_inicio,
                "valueQuantity": {
                    "value": registro.colesterol_total,
                    "unit": "mg/dL",
                    "system": "http://unitsofmeasure.org",
                    "code": "mg/dL"
                }
            }
            observaciones.append(obs_colesterol)
        
        # Observación para triglicéridos
        if registro.trigliceridos:
            obs_trigliceridos = {
                "resourceType": "Observation",
                "id": f"trig-{registro.id}",
                "status": "final",
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "2571-8",
                            "display": "Triglicéridos"
                        }
                    ]
                },
                "subject": {
                    "reference": f"Patient/{paciente_id}"
                },
                "effectiveDateTime": registro.fecha_inicio,
                "valueQuantity": {
                    "value": registro.trigliceridos,
                    "unit": "mg/dL",
                    "system": "http://unitsofmeasure.org",
                    "code": "mg/dL"
                }
            }
            observaciones.append(obs_trigliceridos)
    
    return observaciones 
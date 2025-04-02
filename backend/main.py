from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from database import get_db, engine
import models
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import event
from sqlalchemy.exc import OperationalError
import time
from datetime import datetime, timedelta
import openai # Use old import
import os
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest
import pandas as pd
import json
import uuid
from sqlalchemy.types import String

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

class FHIRMedicationStatement(BaseModel):
    resourceType: str = "MedicationStatement"
    id: str
    status: str = "active"
    medicationCodeableConcept: Dict[str, Any]
    subject: Dict[str, Any]
    effectivePeriod: Dict[str, Any]
    dosage: List[Dict[str, Any]]
    note: Optional[List[Dict[str, Any]]] = None

class FHIRBundle(BaseModel):
    resourceType: str = "Bundle"
    type: str = "collection"
    entry: List[Dict[str, Any]]

# Agregar este modelo Pydantic
class HistorialMedicoCreate(BaseModel):
    paciente_id: str  # Changed from int to str to accept UUID strings
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
app = FastAPI(title="API Ficha Médica Nutricional FHIR")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar OpenAI (asegúrate de tener la variable de entorno OPENAI_API_KEY)
openai.api_key = os.getenv("OPENAI_API_KEY") # Use old configuration

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

# Endpoint de health check
@app.get("/health")
def health_check():
    """Endpoint para verificar que el servicio está funcionando"""
    return {"status": "ok"}

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

@app.get("/pacientes/{paciente_id}")
def obtener_paciente(paciente_id: str, db: Session = Depends(get_db)):
    """Obtiene un paciente por su ID"""
    try:
        paciente_uuid = uuid.UUID(paciente_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de paciente inválido")
        
    paciente = db.query(models.Paciente).filter(models.Paciente.id == paciente_uuid).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    return paciente

@app.post("/historial", response_model=HistorialMedicoBase)
def crear_historial(historial: HistorialMedicoCreate, db: Session = Depends(get_db)):
    """Crea un nuevo registro de historial médico para un paciente"""
    try:
        # Verificar que el paciente existe
        paciente = db.query(models.Paciente).filter(models.Paciente.id == historial.paciente_id).first()
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        # Crear nuevo historial
        nuevo_historial = models.HistorialMedico(**historial.dict())
        db.add(nuevo_historial)
        db.commit()
        db.refresh(nuevo_historial)
        
        return nuevo_historial
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creando historial médico: {str(e)}")

# Endpoints FHIR
@app.get("/fhir/Patient", response_model=List[Dict])
async def get_patients(db: Session = Depends(get_db)):
    """Obtiene todos los pacientes en formato FHIR"""
    try:
        # Obtener todos los pacientes de la base de datos
        pacientes = db.query(models.Paciente).all()
        
        # Convertir a formato FHIR
        pacientes_fhir = []
        for paciente in pacientes:
            paciente_fhir = {
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
                        "use": "official",
                        "family": paciente.apellido,
                        "given": [paciente.nombre]
                    }
                ],
                "gender": "male" if paciente.sexo.lower() == "masculino" else "female",
                "birthDate": paciente.fecha_nacimiento,
                "address": [
                    {
                        "text": paciente.direccion
                    }
                ],
                "telecom": [
                    {
                        "system": "phone",
                        "value": paciente.telefono
                    }
                ]
            }
            
            # Agregar email si existe
            if paciente.email:
                paciente_fhir["telecom"].append({
                    "system": "email",
                    "value": paciente.email
                })
                
            pacientes_fhir.append(paciente_fhir)
        
        print(f"Retornando {len(pacientes_fhir)} pacientes en formato FHIR")
        return pacientes_fhir
        
    except Exception as e:
        print(f"Error al obtener pacientes: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/fhir/Patient/{patient_id}")
def obtener_paciente_fhir(patient_id: str, db: Session = Depends(get_db)):
    """Obtiene un paciente específico en formato FHIR"""
    try:
        # Convert to UUID if it's a valid UUID format
        patient_uuid = uuid.UUID(patient_id)
        
        # Query by UUID
        paciente = db.query(models.Paciente).filter(models.Paciente.id == patient_uuid).first()
        
        if not paciente:
            # If not found by UUID, try using it as a string ID
            paciente = db.query(models.Paciente).filter(models.Paciente.id.cast(String) == patient_id).first()
            
        if not paciente:
            # Last attempt - try by RUT
            paciente = db.query(models.Paciente).filter(models.Paciente.rut == patient_id).first()
        
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        # Convert to FHIR format
        return convertir_paciente_a_fhir(paciente)
    except (ValueError, TypeError):
        # Try to find by RUT if UUID conversion fails
        paciente = db.query(models.Paciente).filter(models.Paciente.rut == patient_id).first()
        
        if not paciente:
            raise HTTPException(status_code=404, detail="Paciente no encontrado")
        
        return convertir_paciente_a_fhir(paciente)

@app.post("/fhir/Patient", status_code=201)
def crear_paciente_fhir(patient: FHIRPatient, db: Session = Depends(get_db)):
    """Endpoint para crear paciente usando formato FHIR"""
    # Extraer datos del recurso FHIR
    rut = None
    for identifier in patient.identifier:
        if identifier.get("system") == "http://minsal.cl/rut":
            rut = identifier.get("value")
    
    if not rut:
        raise HTTPException(status_code=400, detail="Se requiere identificador RUT")
    
    # Verificar si ya existe
    paciente_existente = db.query(models.Paciente).filter(models.Paciente.rut == rut).first()
    if paciente_existente:
        raise HTTPException(status_code=409, detail="Paciente ya existe")
    
    # Extraer datos
    nombre, apellido = obtener_nombre(patient.name[0])
    sexo = "masculino" if patient.gender == "male" else "femenino"
    
    # Crear paciente
    nuevo_paciente = models.Paciente(
        rut=rut,
        nombre=nombre,
        apellido=apellido,
        fecha_nacimiento=patient.birthDate,
        sexo=sexo,
        direccion=patient.address[0].get("text", "") if patient.address else "",
        telefono=patient.telecom[0].get("value", "") if patient.telecom else "",
        contacto_emergencia=patient.contact[0].get("name", {}).get("text", "") if patient.contact else "",
        consentimiento_datos=True,
        tipo_sangre="",
        alergias="",
        actividad_fisica="",
        dieta="",
        problema_salud_principal="",
        objetivo_suplementacion=""
    )
    
    db.add(nuevo_paciente)
    db.commit()
    db.refresh(nuevo_paciente)
    
    # Devolver el recurso creado
    return patient

@app.get("/fhir/Observation/{patient_id}")
def obtener_observaciones_paciente(patient_id: str, db: Session = Depends(get_db)):
    """Obtiene las observaciones de un paciente en formato FHIR"""
    try:
        # Intentar convertir a UUID
        patient_uuid = uuid.UUID(patient_id)
        
        # Buscar historial del paciente
        historiales = db.query(models.HistorialMedico).filter(
            models.HistorialMedico.paciente_id == patient_uuid
        ).all()
        
        if not historiales:
            return []
            
        # Convertir historiales a formato FHIR
        observaciones = []
        for historial in historiales:
            # Crear observaciones para cada parámetro del historial
            if historial.colesterol_total:
                observaciones.append({
                    "resourceType": "Observation",
                    "id": str(uuid.uuid4()),
                    "status": "final",
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "2093-3",
                                "display": "Colesterol Total"
                            }
                        ]
                    },
                    "subject": {
                        "reference": f"Patient/{patient_id}"
                    },
                    "effectiveDateTime": historial.fecha_inicio,
                    "valueQuantity": {
                        "value": historial.colesterol_total,
                        "unit": "mg/dL",
                        "system": "http://unitsofmeasure.org",
                        "code": "mg/dL"
                    }
                })
            
            # Agregar otras observaciones siguiendo el mismo patrón
            if historial.trigliceridos:
                observaciones.append({
                    "resourceType": "Observation",
                    "id": str(uuid.uuid4()),
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
                        "reference": f"Patient/{patient_id}"
                    },
                    "effectiveDateTime": historial.fecha_inicio,
                    "valueQuantity": {
                        "value": historial.trigliceridos,
                        "unit": "mg/dL",
                        "system": "http://unitsofmeasure.org",
                        "code": "mg/dL"
                    }
                })
                
        return observaciones
    except ValueError:
        # ID de paciente no válido
        raise HTTPException(status_code=400, detail="ID de paciente inválido")
    except Exception as e:
        # Registrar el error para depuración
        print(f"Error al obtener observaciones: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/fhir/MedicationStatement")
def crear_historial_medico(historial: dict, db: Session = Depends(get_db)):
    """Endpoint para crear registros de suplementación y biomarcadores"""
    try:
        # Verificar que el paciente existe
        paciente_id = historial.get("paciente_id")
        if not paciente_id:
            raise HTTPException(status_code=400, detail="ID de paciente requerido")
            
        # Convertir string UUID a objeto UUID
        try:
            paciente_uuid = uuid.UUID(paciente_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de ID inválido")
            
        # Verificar que el paciente existe
        paciente = db.query(models.Paciente).filter(models.Paciente.id == paciente_uuid).first()
        if not paciente:
            raise HTTPException(status_code=404, detail=f"Paciente con ID {paciente_id} no encontrado")
        
        # Crear el historial médico
        db_historial = models.HistorialMedico(
            paciente_id=paciente_uuid,
            suplemento=historial.get("suplemento", ""),
            dosis=historial.get("dosis", ""),
            fecha_inicio=historial.get("fecha_inicio", ""),
            duracion=historial.get("duracion", ""),
            colesterol_total=historial.get("colesterol_total", 0),
            trigliceridos=historial.get("trigliceridos", 0),
            vitamina_d=historial.get("vitamina_d", 0),
            omega3_indice=historial.get("omega3_indice", 0),
            observaciones=historial.get("observaciones", "")
        )
        
        db.add(db_historial)
        db.commit()
        db.refresh(db_historial)
        return db_historial
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear historial médico: {str(e)}")

@app.get("/fhir/MedicationStatement/{patient_id}")
def obtener_medicaciones_paciente(patient_id: str, db: Session = Depends(get_db)):
    """Obtiene las medicaciones/suplementos de un paciente en formato FHIR"""
    try:
        # Try to convert to UUID
        try:
            patient_uuid = uuid.UUID(patient_id)
        except ValueError:
            # If not a valid UUID, try to find patient by RUT
            paciente = db.query(models.Paciente).filter(models.Paciente.rut == patient_id).first()
            if paciente:
                patient_uuid = paciente.id
            else:
                return []
        
        # Get medication statements for the patient from the database
        historiales = db.query(models.HistorialMedico).filter(
            models.HistorialMedico.paciente_id == patient_uuid
        ).all()
        
        if not historiales:
            return []
            
        # Convert to FHIR format
        medicamentos = []
        for historial in historiales:
            medicamentos.append({
                "resourceType": "MedicationStatement",
                "id": f"med-{historial.id}",
                "status": "active",
                "medicationCodeableConcept": {
                    "coding": [
                        {
                            "system": "http://suplementos.cl/codigo",
                            "code": historial.suplemento,
                            "display": historial.suplemento
                        }
                    ],
                    "text": historial.suplemento
                },
                "subject": {
                    "reference": f"Patient/{patient_id}"
                },
                "effectivePeriod": {
                    "start": historial.fecha_inicio,
                    "end": None
                },
                "dosage": [
                    {
                        "text": historial.dosis
                    }
                ],
                "note": [
                    {
                        "text": historial.observaciones
                    }
                ] if historial.observaciones else None
            })
        
        return medicamentos
    except Exception as e:
        print(f"Error obtaining medication statements: {str(e)}")
        # Return empty array instead of error to avoid breaking the UI
        return []

@app.post("/fhir/MedicationStatement", status_code=201)
def crear_medicamento_fhir(medication: FHIRMedicationStatement, db: Session = Depends(get_db)):
    """Endpoint para crear registro de suplemento usando formato FHIR"""
    # Extraer paciente_id de la referencia
    subject_ref = medication.subject.get("reference", "")
    if not subject_ref.startswith("Patient/"):
        raise HTTPException(status_code=400, detail="Referencia de paciente inválida")
    
    paciente_id = int(subject_ref.replace("Patient/", ""))
    
    # Verificar si el paciente existe
    paciente = db.query(models.Paciente).filter(models.Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Extraer datos del suplemento
    suplemento = medication.medicationCodeableConcept.get("text", "")
    dosis = medication.dosage[0].get("text", "") if medication.dosage else ""
    fecha_inicio = medication.effectivePeriod.get("start", "")
    observaciones = medication.note[0].get("text", "") if medication.note else ""
    
    # Crear registro de historial
    nuevo_historial = models.HistorialMedico(
        paciente_id=paciente_id,
        suplemento=suplemento,
        dosis=dosis,
        fecha_inicio=fecha_inicio,
        duracion="",
        colesterol_total=0,
        trigliceridos=0,
        vitamina_d=0,
        omega3_indice=0,
        observaciones=observaciones
    )
    
    db.add(nuevo_historial)
    db.commit()
    db.refresh(nuevo_historial)
    
    # Actualizar ID en la respuesta
    medication.id = f"med-{nuevo_historial.id}"
    return medication

@app.get("/fhir/Patient/{rut}/complete", response_model=FHIRBundle)
def obtener_ficha_completa_fhir(rut: str, db: Session = Depends(get_db)):
    """Endpoint para obtener la ficha completa del paciente en formato FHIR"""
    paciente = db.query(models.Paciente).filter(models.Paciente.rut == rut).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Obtener historial médico
    historial = db.query(models.HistorialMedico).filter(models.HistorialMedico.paciente_id == paciente.id).all()
    
    # Crear Bundle FHIR (contenedor de recursos)
    bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": []
    }
    
    # Agregar paciente al bundle
    patient_resource = {
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
        ]
    }
    
    bundle["entry"].append({
        "resource": patient_resource,
        "fullUrl": f"urn:uuid:{paciente.id}"
    })
    
    # Agregar observaciones y medicamentos al bundle
    for registro in historial:
        # Agregar observación de colesterol
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
                    "reference": f"Patient/{paciente.id}"
                },
                "effectiveDateTime": registro.fecha_inicio,
                "valueQuantity": {
                    "value": registro.colesterol_total,
                    "unit": "mg/dL",
                    "system": "http://unitsofmeasure.org",
                    "code": "mg/dL"
                }
            }
            bundle["entry"].append({
                "resource": obs_colesterol,
                "fullUrl": f"urn:uuid:col-{registro.id}"
            })
        
        # Agregar medicamento/suplemento
        med_statement = {
            "resourceType": "MedicationStatement",
            "id": f"med-{registro.id}",
            "status": "active",
            "medicationCodeableConcept": {
                "coding": [
                    {
                        "system": "http://suplementos.cl/codigo",
                        "code": registro.suplemento,
                        "display": registro.suplemento
                    }
                ],
                "text": registro.suplemento
            },
            "subject": {
                "reference": f"Patient/{paciente.id}"
            },
            "effectivePeriod": {
                "start": registro.fecha_inicio,
                "end": None
            },
            "dosage": [
                {
                    "text": registro.dosis
                }
            ],
            "note": [
                {
                    "text": registro.observaciones
                }
            ] if registro.observaciones else None
        }
        bundle["entry"].append({
            "resource": med_statement,
            "fullUrl": f"urn:uuid:med-{registro.id}"
        })
    
    return bundle

@app.post("/fhir/import")
def importar_fhir(bundle: Dict[str, Any], db: Session = Depends(get_db)):
    """Importa un bundle FHIR"""
    recursos_creados = []
    
    # Primero procesar solo los pacientes
    for entry in bundle.get("entry", []):
        if entry.get("resource", {}).get("resourceType") == "Patient":
            try:
                paciente = procesar_paciente_fhir(entry["resource"], db)
                recursos_creados.append({"tipo": "Patient", "id": str(paciente.id)})
            except Exception as e:
                print(f"Error al procesar paciente: {e}")
    
    # Luego procesar el resto de recursos
    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        if resource.get("resourceType") != "Patient":  # Ya procesamos los pacientes
            try:
                if resource.get("resourceType") == "Observation":
                    observacion = procesar_observacion_fhir(resource, db)
                    recursos_creados.append({"tipo": "Observation", "id": observacion.id})
                elif resource.get("resourceType") == "MedicationStatement":
                    medicacion = procesar_medicacion_fhir(resource, db)
                    recursos_creados.append({"tipo": "MedicationStatement", "id": medicacion.id})
            except Exception as e:
                print(f"Error al procesar recurso {resource.get('resourceType')}: {e}")
    
    return {"mensaje": f"Importados {len(recursos_creados)} recursos", "recursos": recursos_creados}

def procesar_paciente_fhir(resource, db):
    """Procesa un recurso Patient de FHIR y lo guarda en la base de datos"""
    try:
        # Extraer el UUID del paciente
        paciente_id = resource.get("id")
        if not paciente_id:
            paciente_id = str(uuid.uuid4())
        
        # Verificar si el paciente ya existe
        paciente_uuid = uuid.UUID(paciente_id)
        paciente_existente = db.query(models.Paciente).filter(models.Paciente.id == paciente_uuid).first()
        if paciente_existente:
            print(f"Paciente {paciente_id} ya existe en la base de datos")
            return paciente_existente
        
        # Extraer información del paciente
        nombre, apellido = obtener_nombre(resource)
        
        # Crear nuevo paciente
        print(f"Creando nuevo paciente con ID: {paciente_id}")
        paciente = models.Paciente(
            id=paciente_uuid,
            rut=obtener_identificador(resource, "http://minsal.cl/rut"),
            nombre=nombre,
            apellido=apellido,
            fecha_nacimiento=resource.get("birthDate", ""),
            sexo=resource.get("gender", "").lower(),
            direccion=obtener_direccion(resource),
            telefono=obtener_telecom(resource, "phone"),
            email=obtener_telecom(resource, "email"),
            # Campos requeridos por el modelo (valores por defecto)
            tipo_sangre="",
            alergias="",
            actividad_fisica="",
            dieta="",
            problema_salud_principal="",
            objetivo_suplementacion="",
            contacto_emergencia="",
            consentimiento_datos=True
        )
        
        db.add(paciente)
        db.commit()
        db.refresh(paciente)
        print(f"Paciente {paciente_id} creado correctamente")
        return paciente
    except Exception as e:
        db.rollback()
        print(f"Error al procesar paciente: {e}")
        raise

class AIRecommendationRequest(BaseModel):
    paciente_id: str # Changed from int to str

class AIRecommendationResponse(BaseModel):
    recomendaciones: List[Dict[str, str]]
    explicacion: str

@app.post("/ai/recomendaciones", response_model=AIRecommendationResponse)
async def obtener_recomendaciones_ia(request: AIRecommendationRequest, db: Session = Depends(get_db)):
    """Endpoint para obtener recomendaciones personalizadas usando IA"""
    # Obtener datos del paciente
    paciente = db.query(models.Paciente).filter(models.Paciente.id == request.paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Obtener historial médico
    historial = db.query(models.HistorialMedico).filter(models.HistorialMedico.paciente_id == request.paciente_id).all()
    
    # Preparar contexto para la IA
    contexto = {
        "paciente": {
            "edad": calcular_edad(paciente.fecha_nacimiento),
            "sexo": paciente.sexo,
            "problema_principal": paciente.problema_salud_principal,
            "objetivo": paciente.objetivo_suplementacion,
            "actividad_fisica": paciente.actividad_fisica,
            "dieta": paciente.dieta,
            "alergias": paciente.alergias
        },
        "historial": [
            {
                "fecha": h.fecha_inicio,
                "suplemento": h.suplemento,
                "dosis": h.dosis,
                "colesterol": h.colesterol_total,
                "trigliceridos": h.trigliceridos,
                "vitamina_d": h.vitamina_d,
                "omega3": h.omega3_indice
            } for h in historial
        ]
    }
    
    try:
        # Llamada a la API de OpenAI using the old syntax
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un experto en nutrición y suplementación. Analiza los datos del paciente y su historial para ofrecer recomendaciones personalizadas basadas en evidencia científica."},
                {"role": "user", "content": f"Datos del paciente: {contexto}. Proporciona 3 recomendaciones específicas para mejorar sus biomarcadores y alcanzar sus objetivos de salud."}
            ],
            temperature=0.7,
        )
        
        # Procesar respuesta
        ai_response = response.choices[0].message.content
        
        # Estructurar respuesta (simplificado - en producción se requeriría un parsing más robusto)
        recomendaciones = [
            {"tipo": "Suplemento", "descripcion": "Aumentar dosis de Omega-3 a 2000mg diarios"},
            {"tipo": "Dieta", "descripcion": "Incrementar consumo de alimentos ricos en fibra soluble"},
            {"tipo": "Estilo de vida", "descripcion": "Incorporar 30 minutos de actividad aeróbica diaria"}
        ]
        
        return {
            "recomendaciones": recomendaciones,
            "explicacion": ai_response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar recomendaciones: {str(e)}")

def calcular_edad(fecha_nacimiento):
    """Función auxiliar para calcular edad desde fecha de nacimiento"""
    from datetime import datetime
    fecha_nac = datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
    hoy = datetime.now()
    edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
    return edad

# Modelos para las solicitudes de IA
class PredictiveTrendRequest(BaseModel):
    paciente_id: int
    biomarcador: str  # "colesterol_total", "trigliceridos", "vitamina_d", "omega3_indice"
    dias_prediccion: int = 90

class AnomalyDetectionRequest(BaseModel):
    paciente_id: str # Changed from int to str

class SupplementOptimizationRequest(BaseModel):
    paciente_id: str # Changed from int to str
    objetivo: Optional[str] = None  # Si se quiere sobreescribir el objetivo actual

# Endpoints de IA adicionales

@app.post("/ai/prediccion-tendencias", response_model=Dict[str, Any])
async def predecir_tendencias(request: PredictiveTrendRequest, db: Session = Depends(get_db)):
    """Predice la evolución de biomarcadores basado en el historial y suplementación"""
    # Verificar que el paciente existe
    paciente = db.query(models.Paciente).filter(models.Paciente.id == request.paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Obtener historial médico ordenado por fecha
    historial = db.query(models.HistorialMedico).filter(
        models.HistorialMedico.paciente_id == request.paciente_id
    ).order_by(models.HistorialMedico.fecha_inicio).all()
    
    if len(historial) < 2:
        return {
            "mensaje": "Se necesitan al menos dos registros para realizar predicciones",
            "predicciones": []
        }
    
    # Preparar datos para el modelo predictivo
    fechas = []
    valores = []
    
    for registro in historial:
        fecha = datetime.strptime(registro.fecha_inicio, "%Y-%m-%d")
        fechas.append((fecha - datetime.strptime(historial[0].fecha_inicio, "%Y-%m-%d")).days)
        
        # Obtener el valor del biomarcador solicitado
        if request.biomarcador == "colesterol_total":
            valores.append(registro.colesterol_total)
        elif request.biomarcador == "trigliceridos":
            valores.append(registro.trigliceridos)
        elif request.biomarcador == "vitamina_d":
            valores.append(registro.vitamina_d)
        elif request.biomarcador == "omega3_indice":
            valores.append(registro.omega3_indice)
        else:
            raise HTTPException(status_code=400, detail="Biomarcador no válido")
    
    # Crear y entrenar modelo de regresión lineal
    X = np.array(fechas).reshape(-1, 1)
    y = np.array(valores)
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Generar predicciones
    ultima_fecha = datetime.strptime(historial[-1].fecha_inicio, "%Y-%m-%d")
    dias_futuros = [i for i in range(1, request.dias_prediccion + 1, 15)]  # Predicción cada 15 días
    
    predicciones = []
    for dias in dias_futuros:
        dias_desde_inicio = fechas[-1] + dias
        valor_predicho = float(model.predict(np.array([[dias_desde_inicio]]))[0])
        
        fecha_prediccion = (ultima_fecha + timedelta(days=dias)).strftime("%Y-%m-%d")
        predicciones.append({
            "fecha": fecha_prediccion,
            "valor_predicho": round(valor_predicho, 2)
        })
    
    # Calcular tendencia y recomendaciones
    tendencia = "estable"
    if model.coef_[0] > 0.5:
        tendencia = "ascendente_rapida"
    elif model.coef_[0] > 0.1:
        tendencia = "ascendente_lenta"
    elif model.coef_[0] < -0.5:
        tendencia = "descendente_rapida"
    elif model.coef_[0] < -0.1:
        tendencia = "descendente_lenta"
    
    # Generar recomendaciones basadas en la tendencia y el biomarcador
    recomendacion = generar_recomendacion_tendencia(request.biomarcador, tendencia, valores[-1])
    
    return {
        "biomarcador": request.biomarcador,
        "valor_actual": valores[-1],
        "tendencia": tendencia,
        "predicciones": predicciones,
        "recomendacion": recomendacion
    }

@app.post("/ai/deteccion-anomalias", response_model=Dict[str, Any])
async def detectar_anomalias(request: AnomalyDetectionRequest, db: Session = Depends(get_db)):
    """Detecta valores anómalos en los biomarcadores del paciente"""
    # Verificar que el paciente existe
    paciente = db.query(models.Paciente).filter(models.Paciente.id == request.paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Obtener último registro médico
    ultimo_registro = db.query(models.HistorialMedico).filter(
        models.HistorialMedico.paciente_id == request.paciente_id
    ).order_by(models.HistorialMedico.fecha_inicio.desc()).first()
    
    if not ultimo_registro:
        return {
            "mensaje": "No hay registros médicos para este paciente",
            "anomalias": [],
            "fecha_analisis": datetime.now().strftime("%Y-%m-%d")
        }
    
    # Rangos normales para cada biomarcador según sexo y edad
    edad = calcular_edad(paciente.fecha_nacimiento)
    es_hombre = paciente.sexo.lower() == "masculino"
    
    rangos_normales = {
        "colesterol_total": {
            "min": 130,
            "max": 200,
            "unidad": "mg/dL",
            "nombre": "Colesterol Total"
        },
        "trigliceridos": {
            "min": 40,
            "max": 150,
            "unidad": "mg/dL",
            "nombre": "Triglicéridos"
        },
        "vitamina_d": {
            "min": 30,
            "max": 100,
            "unidad": "ng/mL",
            "nombre": "Vitamina D"
        },
        "omega3_indice": {
            "min": 4,
            "max": 8,
            "unidad": "%",
            "nombre": "Índice Omega-3"
        }
    }
    
    # Ajustar rangos por edad y sexo si es necesario
    if edad > 50:
        rangos_normales["colesterol_total"]["max"] = 220
    
    # Detectar anomalías
    anomalias = []
    
    for biomarcador, rango in rangos_normales.items():
        valor = getattr(ultimo_registro, biomarcador)
        if valor is None:
            continue
            
        if valor < rango["min"]:
            anomalias.append({
                "biomarcador": rango["nombre"],
                "valor": valor,
                "unidad": rango["unidad"],
                "tipo": "bajo",
                "rango_normal": f"{rango['min']} - {rango['max']} {rango['unidad']}",
                "recomendacion": generar_recomendacion_anomalia(biomarcador, "bajo", paciente.sexo, edad)
            })
        elif valor > rango["max"]:
            anomalias.append({
                "biomarcador": rango["nombre"],
                "valor": valor,
                "unidad": rango["unidad"],
                "tipo": "alto",
                "rango_normal": f"{rango['min']} - {rango['max']} {rango['unidad']}",
                "recomendacion": generar_recomendacion_anomalia(biomarcador, "alto", paciente.sexo, edad)
            })
    
    mensaje = "Se han detectado valores fuera de rango que requieren atención." if anomalias else "Todos los biomarcadores están dentro de rangos normales."
    
    return {
        "mensaje": mensaje,
        "anomalias": anomalias,
        "fecha_analisis": datetime.now().strftime("%Y-%m-%d")
    }

@app.post("/ai/optimizacion-suplementos", response_model=Dict[str, Any])
async def optimizar_suplementos(
    request: SupplementOptimizationRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Genera un plan personalizado de suplementación optimizado con IA"""
    # Verificar que el paciente existe
    paciente = db.query(models.Paciente).filter(models.Paciente.id == request.paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Obtener último registro médico
    ultimo_registro = db.query(models.HistorialMedico).filter(
        models.HistorialMedico.paciente_id == request.paciente_id
    ).order_by(models.HistorialMedico.fecha_inicio.desc()).first()
    
    # Determinar objetivo
    objetivo = request.objetivo if request.objetivo else paciente.objetivo_suplementacion
    if not objetivo:
        objetivo = "Mejorar salud general y optimizar biomarcadores"
    
    contexto = {
        "paciente": {
            "edad": calcular_edad(paciente.fecha_nacimiento),
            "sexo": paciente.sexo,
            "problema_principal": paciente.problema_salud_principal,
            "objetivo": objetivo,
            "actividad_fisica": paciente.actividad_fisica,
            "dieta": paciente.dieta,
            "alergias": paciente.alergias
        }
    }
    
    if ultimo_registro:
        contexto["biomarcadores"] = {
            "colesterol_total": ultimo_registro.colesterol_total,
            "trigliceridos": ultimo_registro.trigliceridos,
            "vitamina_d": ultimo_registro.vitamina_d,
            "omega3_indice": ultimo_registro.omega3_indice
        }
    
    try:
        # Llamada a la API de OpenAI using the old syntax
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """Eres un experto en nutrición y suplementación. 
                Tu tarea es recomendar la combinación óptima de suplementos para el paciente 
                basándote en su perfil, biomarcadores y objetivos. Proporciona dosis específicas, 
                momento del día para tomarlos y posibles interacciones."""},
                {"role": "user", "content": f"Datos del paciente: {contexto}. Proporciona un plan de suplementación personalizado."}
            ],
            temperature=0.7,
        )
        
        # Procesar respuesta
        ai_response = response.choices[0].message.content
        
        # Estructurar plan de suplementación (simplificado)
        plan_suplementacion = {
            "objetivo": objetivo,
            "suplementos_recomendados": [
                {
                    "nombre": "Omega-3",
                    "dosis": "2000mg",
                    "frecuencia": "Diaria",
                    "momento": "Con las comidas",
                    "duracion": "3 meses",
                    "justificacion": "Mejora perfil lipídico y reduce inflamación"
                },
                {
                    "nombre": "Vitamina D3",
                    "dosis": "2000 UI",
                    "frecuencia": "Diaria",
                    "momento": "Con el desayuno",
                    "duracion": "6 meses",
                    "justificacion": "Optimiza niveles séricos y mejora inmunidad"
                }
            ],
            "consideraciones": "Evitar tomar calcio junto con el hierro para mejor absorción",
            "seguimiento_recomendado": "Repetir análisis en 3 meses",
            "explicacion_detallada": ai_response
        }
        
        # Programar tarea en segundo plano para guardar la recomendación
        background_tasks.add_task(
            guardar_recomendacion_suplementos, 
            db=db, 
            paciente_id=request.paciente_id,
            recomendacion=plan_suplementacion
        )
        
        return plan_suplementacion
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar plan de suplementación: {str(e)}")

# Funciones auxiliares para los endpoints de IA

def generar_recomendacion_tendencia(biomarcador, tendencia, valor_actual):
    """Genera recomendaciones basadas en la tendencia de un biomarcador"""
    recomendaciones = {
        "colesterol_total": {
            "ascendente_rapida": "La tendencia al alza rápida del colesterol sugiere revisar la dieta. Considere aumentar fibra soluble y reducir grasas saturadas.",
            "ascendente_lenta": "El colesterol muestra un aumento gradual. Monitorear y considerar ajustes en la dieta.",
            "descendente_rapida": "Excelente progreso en la reducción del colesterol. Mantener el régimen actual.",
            "descendente_lenta": "El colesterol está disminuyendo gradualmente. Continuar con el plan actual.",
            "estable": "Los niveles de colesterol se mantienen estables."
        },
        "trigliceridos": {
            "ascendente_rapida": "Aumento preocupante de triglicéridos. Revisar consumo de azúcares y carbohidratos refinados.",
            "ascendente_lenta": "Ligero aumento en triglicéridos. Considerar reducir azúcares.",
            "descendente_rapida": "Excelente reducción de triglicéridos. Mantener hábitos actuales.",
            "descendente_lenta": "Reducción gradual de triglicéridos. Buen progreso.",
            "estable": "Los niveles de triglicéridos se mantienen estables."
        },
        "vitamina_d": {
            "ascendente_rapida": "Excelente mejora en niveles de vitamina D. Considerar ajustar dosis para mantener.",
            "ascendente_lenta": "Mejora gradual en vitamina D. Continuar suplementación.",
            "descendente_rapida": "Disminución significativa de vitamina D. Revisar dosis y absorción.",
            "descendente_lenta": "Ligera disminución de vitamina D. Monitorear.",
            "estable": "Los niveles de vitamina D se mantienen estables."
        },
        "omega3_indice": {
            "ascendente_rapida": "Excelente mejora en índice omega-3. Mantener suplementación actual.",
            "ascendente_lenta": "Mejora gradual en índice omega-3. Continuar régimen.",
            "descendente_rapida": "Disminución significativa del índice omega-3. Revisar calidad del suplemento.",
            "descendente_lenta": "Ligera disminución del índice omega-3. Considerar ajustar dosis.",
            "estable": "El índice omega-3 se mantiene estable."
        }
    }
    
    return recomendaciones.get(biomarcador, {}).get(tendencia, "No hay recomendaciones específicas disponibles.")

def generar_recomendacion_anomalia(biomarcador, tipo, sexo, edad):
    """Genera recomendaciones para valores anómalos de biomarcadores"""
    recomendaciones = {
        "colesterol_total": {
            "alto": "Considere aumentar el consumo de fibra soluble, reducir grasas saturadas y aumentar actividad física. Evaluar suplementación con fitoesteroles.",
            "bajo": "Niveles bajos de colesterol pueden afectar la producción hormonal. Consulte con su médico para evaluar causas subyacentes."
        },
        "trigliceridos": {
            "alto": "Reduzca el consumo de azúcares y carbohidratos refinados. Aumente omega-3 y considere suplementos de berberina.",
            "bajo": "Aunque poco común, niveles muy bajos de triglicéridos pueden indicar malabsorción. Consulte con su médico."
        },
        "vitamina_d": {
            "alto": "Niveles elevados de vitamina D pueden ser tóxicos. Reduzca o suspenda suplementación y consulte con su médico.",
            "bajo": "Aumente exposición solar moderada y considere suplementación con D3. Verificar niveles de magnesio para mejor absorción."
        },
        "omega3_indice": {
            "alto": "Excelente nivel de omega-3. Mantener hábitos actuales.",
            "bajo": "Aumente consumo de pescados grasos o considere suplementación con omega-3 de alta calidad (EPA/DHA)."
        }
    }
    
    recomendacion_base = recomendaciones.get(biomarcador, {}).get(tipo, "Consulte con su médico.")
    
    # Personalizar por edad y sexo
    if biomarcador == "colesterol_total" and tipo == "alto" and edad > 50:
        recomendacion_base += " En personas mayores de 50 años, evaluar también niveles de CoQ10."
    
    if biomarcador == "vitamina_d" and tipo == "bajo" and sexo.lower() == "femenino":
        recomendacion_base += " En mujeres, niveles óptimos de vitamina D son especialmente importantes para la salud ósea."
    
    return recomendacion_base

async def guardar_recomendacion_suplementos(db: Session, paciente_id: int, recomendacion: Dict):
    """Guarda la recomendación de suplementos en la base de datos"""
    # Aquí implementarías la lógica para guardar en la base de datos
    # Por simplicidad, solo imprimimos en consola
    print(f"Guardando recomendación para paciente {paciente_id}: {recomendacion}")
    pass

# Funciones auxiliares para procesar datos FHIR
def obtener_identificador(resource, system=None):
    """Obtiene el identificador de un recurso FHIR"""
    if not resource or "identifier" not in resource:
        return None
        
    for identifier in resource.get("identifier", []):
        # Si no se especifica sistema, devolver el primer identificador
        if system is None:
            return identifier.get("value")
        # Si coincide el sistema, devolver ese identificador
        if identifier.get("system") == system:
            return identifier.get("value")
    
    # Si no se encuentra, devolver None
    return None

def obtener_nombre(resource, tipo=None):
    """
    Obtiene el nombre de un recurso FHIR Patient.
    Si tipo es None, devuelve una tupla (nombre, apellido)
    Si tipo es "given" o "family", devuelve ese componente específico
    """
    if not resource or "name" not in resource:
        return ("", "") if tipo is None else ""
        
    name = resource.get("name", [{}])[0]
    
    if tipo is None:
        # Devolver tupla (nombre, apellido)
        nombre = " ".join(name.get("given", [""]))
        apellido = name.get("family", "")
        return (nombre, apellido)
    elif tipo == "given":
        return " ".join(name.get("given", [""]))
    elif tipo == "family":
        return name.get("family", "")
    else:
        return ""

def obtener_telecom(resource, system=None):
    """Obtiene el valor de telecom (teléfono, email) de un recurso FHIR"""
    if not resource or "telecom" not in resource:
        return None
        
    for telecom in resource.get("telecom", []):
        if system is None or telecom.get("system") == system:
            return telecom.get("value")
    
    return None

def obtener_direccion(resource):
    """Obtiene la dirección de un recurso FHIR"""
    if not resource or "address" not in resource:
        return None
        
    address = resource.get("address", [{}])[0]
    return address.get("text", "")

def convertir_paciente_a_fhir(paciente):
    """Convierte un paciente de la base de datos a formato FHIR"""
    
    # Importante: incluir el ID exactamente como se almacena
    paciente_fhir = {
        "resourceType": "Patient",
        "id": str(paciente.id),  # Asegurarse de que sea string
        "identifier": [
            {
                "system": "http://minsal.cl/rut",
                "value": paciente.rut
            }
        ],
        "name": [
            {
                "use": "official",
                "family": paciente.apellido,
                "given": [paciente.nombre]
            }
        ],
        "gender": "male" if paciente.sexo.lower() == "masculino" else "female",
        "birthDate": paciente.fecha_nacimiento,
        "address": [
            {
                "text": paciente.direccion
            }
        ],
        "telecom": [
            {
                "system": "phone",
                "value": paciente.telefono
            }
        ]
    }
    
    return paciente_fhir

# Add this function to handle FHIR Observation resources
def procesar_observacion_fhir(observacion, db):
    """Procesa una observación en formato FHIR y la almacena en la base de datos"""
    try:
        # Extract patient reference
        patient_ref = observacion.get("subject", {}).get("reference", "")
        if not patient_ref or not patient_ref.startswith("Patient/"):
            print(f"Referencia de paciente inválida: {patient_ref}")
            return None
            
        patient_id = patient_ref.replace("Patient/", "")
        
        # Extract code and value
        coding = observacion.get("code", {}).get("coding", [])
        if not coding:
            print("Observación sin código")
            return None
            
        code = coding[0].get("code", "")
        
        # Extract value - could be valueQuantity, valueString, etc.
        value = None
        if "valueQuantity" in observacion:
            value = observacion["valueQuantity"].get("value")
        elif "valueString" in observacion:
            value = observacion["valueString"]
        elif "valueCodeableConcept" in observacion:
            value = str(observacion["valueCodeableConcept"])
        
        if value is None:
            print(f"Observación sin valor para el código {code}")
            return None
            
        # Check if patient exists
        paciente = db.query(models.Paciente).filter(models.Paciente.id == patient_id).first()
        if not paciente:
            print(f"Paciente {patient_id} no encontrado")
            return None
            
        # Create or update historial médico record
        historial = db.query(models.HistorialMedico).filter(
            models.HistorialMedico.paciente_id == patient_id
        ).first()
        
        if not historial:
            historial = models.HistorialMedico(paciente_id=patient_id)
            db.add(historial)
        
        # Map FHIR code to database field
        if code == "2093-3":  # Colesterol total
            historial.colesterol_total = value
        elif code == "2571-8":  # Triglicéridos
            historial.trigliceridos = value
        elif code == "14635-7":  # Vitamina D
            historial.vitamina_d = value
        elif code == "omega3_index":  # Omega-3 Index
            historial.omega3_index = value
        
        db.commit()
        return historial
    except Exception as e:
        print(f"Error procesando observación: {str(e)}")
        db.rollback()
        return None

def procesar_medicacion_fhir(medicacion, db):
    """Procesa una declaración de medicación en formato FHIR y la almacena en la base de datos"""
    try:
        # Extract patient reference
        patient_ref = medicacion.get("subject", {}).get("reference", "")
        if not patient_ref or not patient_ref.startswith("Patient/"):
            print(f"Referencia de paciente inválida en medicación: {patient_ref}")
            return None
            
        patient_id = patient_ref.replace("Patient/", "")
        
        # Extract medication information
        medication_ref = None
        if "medicationReference" in medicacion:
            medication_ref = medicacion["medicationReference"].get("reference", "")
        elif "medicationCodeableConcept" in medicacion:
            coding = medicacion["medicationCodeableConcept"].get("coding", [{}])
            if coding:
                medication_ref = coding[0].get("code", "")
        
        if not medication_ref:
            print("Medicación sin referencia o código")
            return None
            
        # Get status and date
        status = medicacion.get("status", "unknown")
        fecha = medicacion.get("effectiveDateTime", "")
        
        # Check if patient exists
        paciente = db.query(models.Paciente).filter(models.Paciente.id == patient_id).first()
        if not paciente:
            print(f"Paciente {patient_id} no encontrado para medicación")
            return None
            
        # Create medicación record
        # Assuming you have a Medicacion model in your models.py
        nueva_medicacion = models.Medicacion(
            paciente_id=patient_id,
            codigo=medication_ref,
            estado=status,
            fecha_inicio=fecha,
            dosis=medicacion.get("dosage", [{}])[0].get("text", "")
        )
        
        db.add(nueva_medicacion)
        db.commit()
        
        return nueva_medicacion
    except Exception as e:
        print(f"Error procesando medicación: {str(e)}")
        db.rollback()
        return None

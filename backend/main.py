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
import openai
import os
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest
import pandas as pd
import json

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
openai.api_key = os.getenv("OPENAI_API_KEY")

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
@app.get("/fhir/Patient", response_model=List[FHIRPatient])
def listar_pacientes_fhir(db: Session = Depends(get_db)):
    """Endpoint para listar todos los pacientes en formato FHIR"""
    pacientes = db.query(models.Paciente).all()
    
    resultado = []
    for paciente in pacientes:
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
        resultado.append(fhir_patient)
    
    return resultado

@app.get("/fhir/Patient/{id_or_rut}", response_model=FHIRPatient)
def obtener_paciente_fhir(id_or_rut: str, db: Session = Depends(get_db)):
    """Endpoint para obtener un paciente en formato FHIR por ID o RUT"""
    # Intentar buscar por ID numérico
    if id_or_rut.isdigit():
        paciente = db.query(models.Paciente).filter(models.Paciente.id == int(id_or_rut)).first()
    else:
        # Si no es numérico, buscar por RUT
        paciente = db.query(models.Paciente).filter(models.Paciente.rut == id_or_rut).first()
    
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Convertir a formato FHIR
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
        ],
        "contact": [
            {
                "name": {
                    "text": paciente.contacto_emergencia
                }
            }
        ]
    }
    
    return patient_resource

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
    nombre = patient.name[0].get("given", [""])[0] if patient.name else ""
    apellido = patient.name[0].get("family", "") if patient.name else ""
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

@app.post("/fhir/Observation", status_code=201)
def crear_observacion_fhir(observation: FHIRObservation, db: Session = Depends(get_db)):
    """Endpoint para crear observación usando formato FHIR"""
    # Extraer paciente_id de la referencia
    subject_ref = observation.subject.get("reference", "")
    if not subject_ref.startswith("Patient/"):
        raise HTTPException(status_code=400, detail="Referencia de paciente inválida")
    
    paciente_id = int(subject_ref.replace("Patient/", ""))
    
    # Verificar si el paciente existe
    paciente = db.query(models.Paciente).filter(models.Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    # Identificar tipo de observación
    codigo = observation.code.get("coding", [{}])[0].get("code", "")
    valor = observation.valueQuantity.get("value", 0)
    
    # Buscar historial existente o crear uno nuevo
    historial = db.query(models.HistorialMedico).filter(
        models.HistorialMedico.paciente_id == paciente_id,
        models.HistorialMedico.fecha_inicio == observation.effectiveDateTime
    ).first()
    
    if not historial:
        historial = models.HistorialMedico(
            paciente_id=paciente_id,
            fecha_inicio=observation.effectiveDateTime,
            suplemento="",
            dosis="",
            duracion="",
            colesterol_total=0,
            trigliceridos=0,
            vitamina_d=0,
            omega3_indice=0,
            observaciones=""
        )
    
    # Actualizar según el tipo de observación
    if codigo == "2093-3":  # Colesterol total
        historial.colesterol_total = valor
    elif codigo == "2571-8":  # Triglicéridos
        historial.trigliceridos = valor
    
    # Guardar en la base de datos
    if not historial.id:
        db.add(historial)
    db.commit()
    db.refresh(historial)
    
    return observation

@app.get("/fhir/MedicationStatement/{paciente_id}", response_model=List[FHIRMedicationStatement])
def obtener_medicamentos_fhir(paciente_id: int, db: Session = Depends(get_db)):
    """Endpoint para obtener historial de suplementos en formato FHIR"""
    historial = db.query(models.HistorialMedico).filter(models.HistorialMedico.paciente_id == paciente_id).all()
    if not historial:
        return []
    
    medicamentos = []
    for registro in historial:
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
                "reference": f"Patient/{paciente_id}"
            },
            "effectivePeriod": {
                "start": registro.fecha_inicio,
                "end": None  # Podría calcularse con fecha_inicio + duracion
            },
            "dosage": [
                {
                    "text": registro.dosis,
                    "timing": {
                        "repeat": {
                            "frequency": 1,
                            "period": 1,
                            "periodUnit": "d"
                        }
                    }
                }
            ],
            "note": [
                {
                    "text": registro.observaciones
                }
            ] if registro.observaciones else None
        }
        medicamentos.append(med_statement)
    
    return medicamentos

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

@app.post("/fhir/import", status_code=201)
def importar_datos_fhir(bundle: Dict[str, Any], db: Session = Depends(get_db)):
    """Endpoint para importar datos desde otros sistemas en formato FHIR"""
    try:
        # Verificar que sea un Bundle FHIR
        if bundle.get("resourceType") != "Bundle":
            raise HTTPException(status_code=400, detail="Se esperaba un recurso Bundle FHIR")
        
        # Procesar cada entrada del bundle
        for entry in bundle.get("entry", []):
            resource = entry.get("resource", {})
            resource_type = resource.get("resourceType")
            
            # Procesar paciente
            if resource_type == "Patient":
                # Extraer identificador (RUT)
                identifiers = resource.get("identifier", [])
                rut = None
                for identifier in identifiers:
                    if identifier.get("system") == "http://minsal.cl/rut":
                        rut = identifier.get("value")
                
                if not rut:
                    continue  # Saltar si no hay RUT
                
                # Verificar si el paciente ya existe
                paciente_existente = db.query(models.Paciente).filter(models.Paciente.rut == rut).first()
                
                # Extraer datos del paciente
                nombres = resource.get("name", [{}])[0].get("given", [""])[0]
                apellidos = resource.get("name", [{}])[0].get("family", "")
                genero = "masculino" if resource.get("gender") == "male" else "femenino"
                fecha_nacimiento = resource.get("birthDate", "")
                
                # Crear o actualizar paciente
                if not paciente_existente:
                    nuevo_paciente = models.Paciente(
                        rut=rut,
                        nombre=nombres,
                        apellido=apellidos,
                        sexo=genero,
                        fecha_nacimiento=fecha_nacimiento,
                        # Otros campos con valores predeterminados
                        direccion="",
                        telefono="",
                        contacto_emergencia="",
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
        
        return {"message": "Datos FHIR importados correctamente"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al importar datos FHIR: {str(e)}")

class AIRecommendationRequest(BaseModel):
    paciente_id: int

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
        # Llamada a la API de OpenAI
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
    paciente_id: int

class SupplementOptimizationRequest(BaseModel):
    paciente_id: int
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
        # Llamada a la API de OpenAI
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
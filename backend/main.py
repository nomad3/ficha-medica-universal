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
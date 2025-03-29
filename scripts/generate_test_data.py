#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import random
import os
import time
import requests
from datetime import datetime, timedelta
import uuid

# Configuración de la base de datos
DB_CONFIG = {
    "dbname": "salud_db",
    "user": "salud_user",
    "password": "salud_password",
    "host": "db",
    "port": "5432"
}

# Datos de ejemplo para pacientes
NOMBRES = ["Juan", "María", "Carlos", "Ana", "Pedro", "Laura", "Diego", "Sofía", "Miguel", "Valentina"]
APELLIDOS = ["González", "Rodríguez", "Pérez", "López", "Martínez", "Sánchez", "Fernández", "Torres", "Ramírez", "Díaz"]
SEXOS = ["male", "female"]
CIUDADES = ["Santiago", "Concepción", "Valparaíso", "Antofagasta", "Temuco", "La Serena", "Rancagua", "Puerto Montt"]

# Datos para suplementos
SUPLEMENTOS = [
    {"codigo": "Omega3", "nombre": "Omega-3", "dosis": ["500mg", "1000mg", "2000mg"]},
    {"codigo": "VitD", "nombre": "Vitamina D", "dosis": ["1000UI", "2000UI", "5000UI"]},
    {"codigo": "Multi", "nombre": "Multivitamínico", "dosis": ["1 tableta", "2 tabletas"]},
    {"codigo": "CoQ10", "nombre": "Coenzima Q10", "dosis": ["100mg", "200mg"]},
    {"codigo": "Magnesio", "nombre": "Magnesio", "dosis": ["250mg", "400mg", "500mg"]},
    {"codigo": "VitB12", "nombre": "Vitamina B12", "dosis": ["500mcg", "1000mcg", "2500mcg"]},
    {"codigo": "Zinc", "nombre": "Zinc", "dosis": ["15mg", "25mg", "50mg"]}
]

# Datos para biomarcadores
BIOMARCADORES = [
    {"codigo": "2093-3", "nombre": "Colesterol total", "unidad": "mg/dL", "min": 130, "max": 240, "optimo": 180},
    {"codigo": "2571-8", "nombre": "Triglicéridos", "unidad": "mg/dL", "min": 40, "max": 200, "optimo": 100},
    {"codigo": "14635-7", "nombre": "Vitamina D", "unidad": "ng/mL", "min": 10, "max": 80, "optimo": 40},
    {"codigo": "omega3_index", "nombre": "Índice Omega-3", "unidad": "%", "min": 2, "max": 10, "optimo": 6}
]

# Perfiles de pacientes para generar datos más realistas
PERFILES = [
    {
        "nombre": "Perfil Saludable",
        "descripcion": "Paciente con buenos hábitos y valores normales",
        "modificadores": {"colesterol": 0.9, "trigliceridos": 0.8, "vitamina_d": 1.2, "omega3": 1.1},
        "probabilidad_suplemento": 0.3
    },
    {
        "nombre": "Perfil Cardiovascular",
        "descripcion": "Paciente con factores de riesgo cardiovascular",
        "modificadores": {"colesterol": 1.3, "trigliceridos": 1.4, "vitamina_d": 0.9, "omega3": 0.7},
        "probabilidad_suplemento": 0.7
    },
    {
        "nombre": "Perfil Deficiencia Nutricional",
        "descripcion": "Paciente con deficiencias vitamínicas",
        "modificadores": {"colesterol": 1.0, "trigliceridos": 1.0, "vitamina_d": 0.6, "omega3": 0.5},
        "probabilidad_suplemento": 0.8
    },
    {
        "nombre": "Perfil Adulto Mayor",
        "descripcion": "Paciente mayor de 65 años con necesidades específicas",
        "modificadores": {"colesterol": 1.1, "trigliceridos": 1.1, "vitamina_d": 0.7, "omega3": 0.8},
        "probabilidad_suplemento": 0.9
    },
    {
        "nombre": "Perfil Deportista",
        "descripcion": "Paciente con actividad física regular",
        "modificadores": {"colesterol": 0.8, "trigliceridos": 0.7, "vitamina_d": 1.1, "omega3": 1.2},
        "probabilidad_suplemento": 0.6
    }
]

def generar_rut():
    """Genera un RUT chileno aleatorio con formato"""
    num = random.randint(10000000, 25000000)
    verificador = "0123456789K"[num % 11]
    return f"{num:,}".replace(",", ".") + "-" + verificador

def generar_fecha_nacimiento(min_edad=18, max_edad=85):
    """Genera una fecha de nacimiento aleatoria"""
    dias = random.randint(min_edad * 365, max_edad * 365)
    return (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")

def generar_telefono():
    """Genera un número de teléfono chileno aleatorio"""
    return f"+569{random.randint(10000000, 99999999)}"

def generar_direccion():
    """Genera una dirección aleatoria"""
    calles = ["Av. Principal", "Calle Los Robles", "Pasaje Las Flores", "Av. Libertad", "Calle O'Higgins"]
    return f"{random.choice(calles)} {random.randint(100, 9999)}, {random.choice(CIUDADES)}"

def generar_paciente(perfil):
    """Genera datos de un paciente basado en un perfil"""
    sexo = random.choice(SEXOS)
    nombre = random.choice(NOMBRES) if sexo == "male" else random.choice([n for n in NOMBRES if n in ["María", "Ana", "Laura", "Sofía", "Valentina"]])
    
    # Ajustar edad según perfil
    min_edad = 65 if perfil["nombre"] == "Perfil Adulto Mayor" else 18
    max_edad = 90 if perfil["nombre"] == "Perfil Adulto Mayor" else 64
    
    fecha_nacimiento = generar_fecha_nacimiento(min_edad, max_edad)
    
    return {
        "resourceType": "Patient",
        "id": str(uuid.uuid4()),
        "identifier": [
            {
                "system": "http://minsal.cl/rut",
                "value": generar_rut()
            }
        ],
        "name": [
            {
                "family": random.choice(APELLIDOS),
                "given": [nombre]
            }
        ],
        "gender": sexo,
        "birthDate": fecha_nacimiento,
        "telecom": [
            {
                "system": "phone",
                "value": generar_telefono()
            }
        ],
        "address": [
            {
                "text": generar_direccion()
            }
        ],
        "contact": [
            {
                "name": {
                    "text": f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)} {generar_telefono()}"
                }
            }
        ],
        "extension": [
            {
                "url": "http://example.org/fhir/StructureDefinition/patient-profile",
                "valueString": perfil["nombre"]
            }
        ]
    }

def generar_valor_biomarcador(biomarcador, perfil, fecha, tendencia=None):
    """Genera un valor para un biomarcador basado en el perfil del paciente"""
    # Obtener el modificador según el tipo de biomarcador
    modificador = 1.0
    if "colesterol" in biomarcador["nombre"].lower():
        modificador = perfil["modificadores"]["colesterol"]
    elif "trigliceridos" in biomarcador["nombre"].lower():
        modificador = perfil["modificadores"]["trigliceridos"]
    elif "vitamina d" in biomarcador["nombre"].lower():
        modificador = perfil["modificadores"]["vitamina_d"]
    elif "omega" in biomarcador["nombre"].lower():
        modificador = perfil["modificadores"]["omega3"]
    
    # Aplicar tendencia si existe
    if tendencia:
        # Tendencia positiva: valores mejoran con el tiempo
        if tendencia == "mejora":
            dias_pasados = (datetime.now() - datetime.strptime(fecha, "%Y-%m-%d")).days
            factor_tiempo = min(1.0, dias_pasados / 180.0) * 0.2
            if modificador > 1.0:  # Valores altos (malos)
                modificador = max(0.9, modificador - factor_tiempo)
            else:  # Valores bajos (buenos)
                modificador = min(1.1, modificador + factor_tiempo)
        # Tendencia negativa: valores empeoran con el tiempo
        elif tendencia == "empeora":
            dias_pasados = (datetime.now() - datetime.strptime(fecha, "%Y-%m-%d")).days
            factor_tiempo = min(1.0, dias_pasados / 180.0) * 0.2
            if modificador > 1.0:  # Valores altos (malos)
                modificador = min(1.5, modificador + factor_tiempo)
            else:  # Valores bajos (buenos)
                modificador = max(0.7, modificador - factor_tiempo)
    
    # Generar valor con variabilidad
    base = biomarcador["optimo"] * modificador
    variabilidad = base * 0.15  # 15% de variabilidad
    valor = random.uniform(base - variabilidad, base + variabilidad)
    
    # Asegurar que esté dentro de los límites
    valor = max(biomarcador["min"], min(biomarcador["max"], valor))
    
    return round(valor, 1)

def generar_observacion(paciente_id, biomarcador, perfil, fecha, tendencia=None):
    """Genera una observación FHIR para un biomarcador"""
    valor = generar_valor_biomarcador(biomarcador, perfil, fecha, tendencia)
    
    return {
        "resourceType": "Observation",
        "id": str(uuid.uuid4()),
        "status": "final",
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": biomarcador["codigo"],
                    "display": biomarcador["nombre"]
                }
            ]
        },
        "subject": {
            "reference": f"Patient/{paciente_id}"
        },
        "effectiveDateTime": fecha,
        "valueQuantity": {
            "value": valor,
            "unit": biomarcador["unidad"],
            "system": "http://unitsofmeasure.org",
            "code": biomarcador["unidad"]
        }
    }

def generar_medicacion(paciente_id, suplemento, fecha_inicio, fecha_fin=None):
    """Genera un registro de medicación/suplemento FHIR"""
    dosis = random.choice(suplemento["dosis"])
    
    medicacion = {
        "resourceType": "MedicationStatement",
        "id": str(uuid.uuid4()),
        "status": "active" if not fecha_fin else "completed",
        "medicationCodeableConcept": {
            "coding": [
                {
                    "system": "http://suplementos.cl/codigo",
                    "code": suplemento["codigo"],
                    "display": suplemento["nombre"]
                }
            ],
            "text": suplemento["nombre"]
        },
        "subject": {
            "reference": f"Patient/{paciente_id}"
        },
        "effectivePeriod": {
            "start": fecha_inicio
        },
        "dosage": [
            {
                "text": dosis
            }
        ],
        "note": [
            {
                "text": f"Suplementación con {suplemento['nombre']} {dosis}"
            }
        ]
    }
    
    if fecha_fin:
        medicacion["effectivePeriod"]["end"] = fecha_fin
    
    return medicacion

def generar_historial_paciente(paciente, perfil):
    """Genera historial completo para un paciente"""
    paciente_id = paciente["id"]
    recursos = []
    
    # Determinar tendencia general del paciente
    tendencias = ["estable", "mejora", "empeora"]
    pesos = [0.6, 0.2, 0.2]
    if perfil["nombre"] == "Perfil Saludable":
        pesos = [0.4, 0.5, 0.1]
    elif perfil["nombre"] == "Perfil Cardiovascular":
        pesos = [0.3, 0.2, 0.5]
    
    tendencia_general = random.choices(tendencias, weights=pesos, k=1)[0]
    
    # Generar fechas para el historial (últimos 2 años)
    hoy = datetime.now()
    fechas = []
    for i in range(4):  # 4 mediciones en 2 años
        dias_atras = random.randint(i*180, (i+1)*180)
        fecha = (hoy - timedelta(days=dias_atras)).strftime("%Y-%m-%d")
        fechas.append(fecha)
    
    fechas.sort()  # Ordenar cronológicamente
    
    # Generar observaciones para cada biomarcador en cada fecha
    for fecha in fechas:
        for biomarcador in BIOMARCADORES:
            observacion = generar_observacion(paciente_id, biomarcador, perfil, fecha, tendencia_general)
            recursos.append(observacion)
    
    # Generar historial de suplementación
    suplementos_asignados = []
    for suplemento in SUPLEMENTOS:
        if random.random() < perfil["probabilidad_suplemento"]:
            # Fecha de inicio aleatoria en el último año
            dias_atras = random.randint(30, 365)
            fecha_inicio = (hoy - timedelta(days=dias_atras)).strftime("%Y-%m-%d")
            
            # 30% de probabilidad de que haya terminado
            fecha_fin = None
            if random.random() < 0.3:
                dias_duracion = random.randint(30, min(dias_atras-1, 180))
                fecha_fin = (hoy - timedelta(days=dias_atras-dias_duracion)).strftime("%Y-%m-%d")
            
            medicacion = generar_medicacion(paciente_id, suplemento, fecha_inicio, fecha_fin)
            recursos.append(medicacion)
            suplementos_asignados.append(suplemento["codigo"])
    
    # Asegurar que al menos un paciente con perfil cardiovascular tenga Omega3
    if perfil["nombre"] == "Perfil Cardiovascular" and "Omega3" not in suplementos_asignados:
        dias_atras = random.randint(30, 180)
        fecha_inicio = (hoy - timedelta(days=dias_atras)).strftime("%Y-%m-%d")
        suplemento = next(s for s in SUPLEMENTOS if s["codigo"] == "Omega3")
        medicacion = generar_medicacion(paciente_id, suplemento, fecha_inicio)
        recursos.append(medicacion)
    
    # Asegurar que al menos un paciente con deficiencia nutricional tenga VitD
    if perfil["nombre"] == "Perfil Deficiencia Nutricional" and "VitD" not in suplementos_asignados:
        dias_atras = random.randint(30, 180)
        fecha_inicio = (hoy - timedelta(days=dias_atras)).strftime("%Y-%m-%d")
        suplemento = next(s for s in SUPLEMENTOS if s["codigo"] == "VitD")
        medicacion = generar_medicacion(paciente_id, suplemento, fecha_inicio)
        recursos.append(medicacion)
    
    return recursos

def generar_datos_prueba(num_pacientes=10):
    """Genera un conjunto completo de datos de prueba"""
    bundle = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": []
    }
    
    # Distribuir pacientes entre perfiles
    for i in range(num_pacientes):
        # Seleccionar perfil con pesos para asegurar distribución
        perfil = random.choices(PERFILES, weights=[0.2, 0.25, 0.2, 0.15, 0.2], k=1)[0]
        
        # Generar paciente
        paciente = generar_paciente(perfil)
        
        # Añadir paciente al bundle
        bundle["entry"].append({
            "resource": paciente,
            "request": {
                "method": "POST",
                "url": "Patient"
            }
        })
        
        # Generar historial
        recursos_historial = generar_historial_paciente(paciente, perfil)
        
        # Añadir recursos al bundle
        for recurso in recursos_historial:
            tipo_recurso = recurso["resourceType"]
            bundle["entry"].append({
                "resource": recurso,
                "request": {
                    "method": "POST",
                    "url": tipo_recurso
                }
            })
    
    return bundle

def guardar_bundle_json(bundle, filename="datos_prueba.json"):
    """Guarda el bundle en un archivo JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(bundle, f, ensure_ascii=False, indent=2)
    print(f"Datos guardados en {filename}")

def importar_a_postgres(bundle):
    """Importa los datos a PostgreSQL usando la API"""
    max_intentos = 5
    for intento in range(max_intentos):
        try:
            # Verificar primero si el backend está disponible
            health_check = requests.get("http://backend:8000/health", timeout=5)
            if health_check.status_code == 200:
                print("Backend disponible, importando datos...")
                
                response = requests.post(
                    "http://backend:8000/fhir/import",
                    json=bundle,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                # Considerar 201 Created como éxito
                if response.status_code in [200, 201]:
                    print(f"Datos importados correctamente a través de la API (status: {response.status_code})")
                    print(f"Respuesta: {response.text}")
                    return True
                else:
                    print(f"Error al importar datos: {response.status_code}")
                    print(f"Respuesta: {response.text}")
            else:
                print(f"Backend no disponible (status: {health_check.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"Error al conectar con la API (intento {intento+1}/{max_intentos}): {e}")
        
        # Esperar antes de reintentar
        if intento < max_intentos - 1:
            tiempo_espera = 5 * (intento + 1)  # Espera progresiva
            print(f"Reintentando en {tiempo_espera} segundos...")
            time.sleep(tiempo_espera)
    
    print("No se pudo importar los datos después de varios intentos")
    return False

if __name__ == "__main__":
    # Esperar un poco para asegurarse de que el backend esté listo
    print("Esperando a que el backend esté completamente inicializado...")
    time.sleep(10)
    
    # Verificar si el backend está disponible
    backend_disponible = False
    for _ in range(5):
        try:
            response = requests.get("http://backend:8000/health", timeout=2)
            if response.status_code == 200:
                backend_disponible = True
                print("Backend disponible, procediendo con la generación de datos...")
                break
        except requests.exceptions.RequestException:
            pass
        print("Backend no disponible, esperando...")
        time.sleep(5)
    
    if not backend_disponible:
        print("No se pudo conectar con el backend después de varios intentos")
        print("Generando datos de todas formas, pero no se importarán automáticamente")
    
    # Generar datos de prueba
    num_pacientes = 15
    bundle = generar_datos_prueba(num_pacientes)
    
    # Guardar en archivo JSON
    guardar_bundle_json(bundle)
    
    # Intentar importar si el backend está disponible
    if backend_disponible:
        importar_a_postgres(bundle)
    else:
        print(f"Generados datos para {num_pacientes} pacientes con sus historiales médicos")
        print("Para importar los datos manualmente, ejecuta:")
        print("curl -X POST http://localhost:8000/fhir/import -H \"Content-Type: application/json\" -d @datos_prueba.json") 
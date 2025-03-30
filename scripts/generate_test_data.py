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

# Datos para generar información aleatoria
NOMBRES = ["Juan", "María", "Pedro", "Ana", "Luis", "Carla", "Diego", "Sofía", "Miguel", "Valentina", 
           "Javier", "Catalina", "Roberto", "Fernanda", "Carlos", "Paula", "Eduardo", "Daniela"]
APELLIDOS = ["González", "Rodríguez", "Fernández", "López", "Martínez", "Pérez", "Gómez", "Sánchez", 
            "Romero", "Torres", "Flores", "Rivera", "Vargas", "Ramos", "Reyes", "Cruz", "Morales"]
COMUNAS = ["Santiago", "Providencia", "Las Condes", "Ñuñoa", "La Florida", "Maipú", "Puente Alto", 
          "Vitacura", "Conchalí", "Recoleta", "Independencia", "Huechuraba", "Quilicura"]
CALLES = ["Av. Providencia", "Av. Apoquindo", "Av. Las Condes", "Av. Vicuña Mackenna", "Av. Libertador", 
         "Av. Los Leones", "Av. Tobalaba", "Av. Irarrázaval", "Av. Grecia", "Av. Macul", "Av. Departamental"]

# Datos para suplementos
SUPLEMENTOS = [
    {"codigo": "Omega3", "nombre": "Omega-3", "dosis": ["1000mg", "2000mg", "3000mg", "500mg"]},
    {"codigo": "VitD", "nombre": "Vitamina D", "dosis": ["1000UI", "2000UI", "5000UI", "10000UI"]},
    {"codigo": "Multi", "nombre": "Multivitamínico", "dosis": ["1 tableta", "1 cápsula", "2 cápsulas"]},
    {"codigo": "Magnesio", "nombre": "Magnesio", "dosis": ["200mg", "400mg", "600mg"]},
    {"codigo": "CoQ10", "nombre": "Coenzima Q10", "dosis": ["50mg", "100mg", "200mg"]}
]

# Datos para biomarcadores
BIOMARCADORES = [
    {"codigo": "2093-3", "nombre": "Colesterol total", "unidad": "mg/dL", "min": 100, "optimo": 180, "max": 300},
    {"codigo": "2571-8", "nombre": "Triglicéridos", "unidad": "mg/dL", "min": 50, "optimo": 100, "max": 500},
    {"codigo": "14635-7", "nombre": "Vitamina D, 25-OH", "unidad": "ng/mL", "min": 10, "optimo": 40, "max": 80},
    {"codigo": "omega3_index", "nombre": "Índice de Omega-3", "unidad": "%", "min": 2, "optimo": 8, "max": 12}
]

# Perfiles de paciente
PERFILES = [
    {
        "nombre": "Perfil Saludable",
        "probabilidad_suplemento": 0.3,  # 30% de tener suplementos
        "modificadores": {
            "colesterol": 0.9,     # Colesterol 10% por debajo del óptimo
            "trigliceridos": 0.85, # Triglicéridos 15% por debajo del óptimo
            "vitamina_d": 1.1,     # Vitamina D 10% por encima del óptimo
            "omega3": 1.15         # Omega-3 15% por encima del óptimo
        }
    },
    {
        "nombre": "Perfil Cardiovascular",
        "probabilidad_suplemento": 0.7,  # 70% de tener suplementos
        "modificadores": {
            "colesterol": 1.4,     # Colesterol 40% por encima del óptimo
            "trigliceridos": 1.5,  # Triglicéridos 50% por encima del óptimo
            "vitamina_d": 0.9,     # Vitamina D 10% por debajo del óptimo
            "omega3": 0.7          # Omega-3 30% por debajo del óptimo
        }
    },
    {
        "nombre": "Perfil Deficiencia Nutricional",
        "probabilidad_suplemento": 0.8,  # 80% de tener suplementos
        "modificadores": {
            "colesterol": 1.1,     # Colesterol 10% por encima del óptimo
            "trigliceridos": 1.15, # Triglicéridos 15% por encima del óptimo
            "vitamina_d": 0.6,     # Vitamina D 40% por debajo del óptimo
            "omega3": 0.7          # Omega-3 30% por debajo del óptimo
        }
    },
    {
        "nombre": "Perfil Metabólico",
        "probabilidad_suplemento": 0.6,  # 60% de tener suplementos
        "modificadores": {
            "colesterol": 1.25,    # Colesterol 25% por encima del óptimo
            "trigliceridos": 1.4,  # Triglicéridos 40% por encima del óptimo
            "vitamina_d": 0.8,     # Vitamina D 20% por debajo del óptimo
            "omega3": 0.85         # Omega-3 15% por debajo del óptimo
        }
    },
    {
        "nombre": "Perfil Deportista",
        "probabilidad_suplemento": 0.9,  # 90% de tener suplementos
        "modificadores": {
            "colesterol": 0.95,    # Colesterol 5% por debajo del óptimo
            "trigliceridos": 0.9,  # Triglicéridos 10% por debajo del óptimo
            "vitamina_d": 1.2,     # Vitamina D 20% por encima del óptimo
            "omega3": 1.2          # Omega-3 20% por encima del óptimo
        }
    }
]

def generar_rut():
    """Genera un RUT chileno válido"""
    num = random.randint(10000000, 25000000)
    return f"{num}-{random.randint(0, 9)}"

def generar_telefono():
    """Genera un número de teléfono chileno"""
    return f"+569{random.randint(10000000, 99999999)}"

def generar_direccion():
    """Genera una dirección aleatoria"""
    return f"{random.choice(CALLES)} {random.randint(100, 9999)}, {random.choice(COMUNAS)}"

def generar_fecha_nacimiento():
    """Genera una fecha de nacimiento para un adulto"""
    anio = random.randint(1950, 2005)
    mes = random.randint(1, 12)
    dia = random.randint(1, 28)  # Para evitar problemas con febrero
    return f"{anio}-{mes:02d}-{dia:02d}"

def generar_paciente(perfil):
    """Genera datos de un paciente"""
    # Información básica
    sexo_m = random.choice([True, False])
    sexo = "male" if sexo_m else "female"
    nombre = random.choice([n for n in NOMBRES if (sexo_m and n in ["Juan", "Pedro", "Luis", "Diego", "Miguel", "Javier", "Roberto", "Carlos", "Eduardo"]) or 
                          (not sexo_m and n in ["María", "Ana", "Carla", "Sofía", "Valentina", "Catalina", "Fernanda", "Paula", "Daniela"])])
    fecha_nacimiento = generar_fecha_nacimiento()
    
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
    
    # Añadir patrones de respuesta a la suplementación
    if random.random() < 0.7:  # 70% de efectividad del suplemento
        # Este suplemento mejora un biomarcador específico
        if suplemento["codigo"] == "Omega3":
            # Mejorar colesterol y omega3_indice en observaciones posteriores
            # Esta lógica se implementaría en generar_observacion
            pass
        elif suplemento["codigo"] == "VitD":
            # Mejorar vitamina_d en observaciones posteriores
            pass
    
    return medicacion

def generar_historial_paciente(paciente, perfil):
    """Genera historial completo para un paciente incluyendo observaciones y medicaciones"""
    paciente_id = paciente["id"]
    recursos = []
    
    # Generar fechas en retroactivo (más recientes primero)
    num_fechas = random.randint(6, 10)  # Aumentar número de puntos de datos
    
    fechas = []
    hoy = datetime.now()
    for i in range(num_fechas):
        # Distribuir las fechas en los últimos 2 años para mejor visualización de tendencias
        dias_atras = int(720 * (num_fechas - i) / num_fechas)
        fecha = (hoy - timedelta(days=dias_atras)).strftime("%Y-%m-%d")
        fechas.append(fecha)
    
    # Asignar suplementos según perfil de paciente
    suplementos_asignados = []
    for suplemento in SUPLEMENTOS:
        if random.random() < perfil["probabilidad_suplemento"]:
            suplementos_asignados.append(suplemento["codigo"])
    
    # Valores base de biomarcadores
    valores_base = {}
    for marcador in BIOMARCADORES:
        # Aplicar modificadores según perfil
        modificador = 1.0
        if marcador["nombre"] == "Colesterol total":
            modificador = perfil["modificadores"]["colesterol"]
        elif marcador["nombre"] == "Triglicéridos":
            modificador = perfil["modificadores"]["trigliceridos"]
        elif marcador["nombre"] == "Vitamina D, 25-OH":
            modificador = perfil["modificadores"]["vitamina_d"]
        elif marcador["nombre"] == "Índice de Omega-3":
            modificador = perfil["modificadores"]["omega3"]
        
        valor_base = marcador["optimo"] * modificador
        valores_base[marcador["codigo"]] = valor_base
    
    # Para cada fecha, generar observaciones con variación
    for fecha_idx, fecha in enumerate(fechas):
        for marcador in BIOMARCADORES:
            codigo = marcador["codigo"]
            
            # Si no es la primera fecha, aplicar tendencia (mejora si toma suplemento relacionado)
            if fecha_idx > 0:
                valor_previo = valores_base[codigo]
                
                # Calcular mejora por suplementos
                mejora = 0
                for suplemento in suplementos_asignados:
                    # Mejora por Omega-3 en lípidos y omega3_index
                    if suplemento == "Omega3" and codigo in ["2093-3", "2571-8", "omega3_index"]:
                        mejora += random.uniform(0.02, 0.05)
                    # Mejora por Vitamina D 
                    elif suplemento == "VitD" and codigo == "14635-7":
                        mejora += random.uniform(0.03, 0.06)
                
                # Tendencia natural (ligero empeoramiento o estabilidad)
                tendencia_natural = random.uniform(-0.02, 0.01)
                
                # Combinar tendencias
                cambio_total = tendencia_natural + mejora
                
                # Aplicar cambio y añadir ruido aleatorio para realismo
                valor_nuevo = valor_previo * (1 + cambio_total) * random.uniform(0.97, 1.03)
                
                # Limitar a rangos razonables
                valor_nuevo = max(marcador["min"], min(marcador["max"], valor_nuevo))
                valores_base[codigo] = valor_nuevo
            
            # Crear observación FHIR
            valor = valores_base[codigo]
            observacion = {
                "resourceType": "Observation",
                "id": str(uuid.uuid4()),
                "status": "final",
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": codigo,
                            "display": marcador["nombre"]
                        }
                    ]
                },
                "subject": {
                    "reference": f"Patient/{paciente_id}"
                },
                "effectiveDateTime": fecha,
                "valueQuantity": {
                    "value": round(valor, 1) if codigo == "omega3_index" else int(valor),
                    "unit": marcador["unidad"],
                    "system": "http://unitsofmeasure.org",
                    "code": marcador["unidad"]
                }
            }
            recursos.append(observacion)
        
        # Generar declaraciones de medicación (MedicationStatement)
        for suplemento_codigo in suplementos_asignados:
            suplemento = next((s for s in SUPLEMENTOS if s["codigo"] == suplemento_codigo), None)
            if suplemento:
                # La fecha de inicio del suplemento será anterior a la fecha actual del ciclo
                dias_atras = (hoy - datetime.strptime(fecha, "%Y-%m-%d")).days
                
                # Asegurarse de que el rango para randint sea válido
                max_duracion = max(31, min(dias_atras, 180))  # Asegurar que sea al menos 31
                dias_duracion = random.randint(30, max_duracion)
                
                fecha_inicio = (datetime.strptime(fecha, "%Y-%m-%d") - timedelta(days=dias_duracion)).strftime("%Y-%m-%d")
                
                medicacion = {
                    "resourceType": "MedicationStatement",
                    "id": str(uuid.uuid4()),
                    "status": "active",
                    "medicationCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://suplementos.org",
                                "code": suplemento["codigo"],
                                "display": suplemento["nombre"]
                            }
                        ],
                        "text": suplemento["nombre"]
                    },
                    "subject": {
                        "reference": f"Patient/{paciente_id}"
                    },
                    "effectiveDateTime": fecha_inicio,
                    "dosage": [
                        {
                            "text": random.choice(suplemento["dosis"]) + " diario"
                        }
                    ]
                }
                recursos.append(medicacion)
    
    return recursos

def generar_historial(paciente_id):
    """Genera datos de historial médico con suplementos y biomarcadores"""
    return {
        "paciente_id": paciente_id,  # Ahora es UUID string
        "suplemento": random.choice(["Omega3", "Vitamina D", "Multivitamínico", "Magnesio", "CoQ10"]),
        "dosis": f"{random.randint(1, 5)*500}mg" if random.choice([True, False]) else f"{random.randint(1, 3)*1000}UI",
        "fecha_inicio": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
        "duracion": f"{random.randint(1, 12)} meses",
        "colesterol_total": random.randint(150, 300),
        "trigliceridos": random.randint(70, 400),
        "vitamina_d": random.randint(10, 60),
        "omega3_indice": random.randint(2, 12),
        "observaciones": random.choice([
            "Mejoría en niveles de energía",
            "Sin efectos adversos reportados", 
            "Ajuste de dosis requerido",
            "Control periódico recomendado"
        ])
    }

def generar_datos_prueba(num_pacientes=50):  # Aumentado de 30 a 50 pacientes
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

def verificar_backend():
    """Verifica si el backend está disponible"""
    for _ in range(5):
        try:
            response = requests.get("http://backend:8000/health", timeout=2)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        print("Backend no disponible, esperando...")
        time.sleep(5)
    return False

def main():
    # Verificar si el backend está disponible
    backend_disponible = verificar_backend()
    
    if not backend_disponible:
        print("No se pudo conectar con el backend después de varios intentos")
        print("Generando datos de todas formas, pero no se importarán automáticamente")
    
    # Aumentar el número de pacientes para mejores pruebas de IA
    num_pacientes = 50  # Más pacientes para análisis estadísticos
    
    # Generar datos de prueba
    bundle = generar_datos_prueba(num_pacientes)
    
    # Guardar en archivo JSON
    guardar_bundle_json(bundle)
    
    if backend_disponible:
        # Primero, crear un bundle solo con pacientes
        pacientes_bundle = {
            "resourceType": "Bundle",
            "type": "transaction",
            "entry": []
        }
        
        # Extraer solo los pacientes del bundle original
        for entry in bundle["entry"]:
            if entry["resource"]["resourceType"] == "Patient":
                pacientes_bundle["entry"].append(entry)
        
        # Importar solo los pacientes primero
        print("Importando pacientes...")
        response = requests.post(
            "http://backend:8000/fhir/import",
            json=pacientes_bundle
        )
        
        if response.status_code != 200:
            print(f"Error importando pacientes: {response.text}")
            return
        
        print("Pacientes importados correctamente")
        
        # Esperar un momento para asegurar que los pacientes estén en la base de datos
        time.sleep(2)
        
        # Ahora crear los historiales médicos uno por uno
        for paciente_entry in pacientes_bundle["entry"]:
            paciente_id = paciente_entry["resource"]["id"]
            
            # Verificar que el paciente existe en la base de datos
            response = requests.get(f"http://backend:8000/pacientes/{paciente_id}")
            if response.status_code != 200:
                print(f"Paciente {paciente_id} no encontrado en la base de datos, saltando...")
                continue
                
            print(f"Creando historiales para paciente {paciente_id}")
            
            # Crear 2-5 historiales para este paciente
            for _ in range(random.randint(2, 5)):
                historial_data = generar_historial(paciente_id)
                response = requests.post(
                    "http://backend:8000/historial",
                    json=historial_data
                )
                
                if response.status_code not in [200, 201]:
                    print(f"Error creando historial: {response.text}")
                else:
                    print("Historial creado correctamente")
        
        # Ahora importar observaciones y medicaciones
        observaciones_medicaciones_bundle = {
            "resourceType": "Bundle",
            "type": "transaction",
            "entry": []
        }
        
        # Extraer observaciones y medicaciones del bundle original
        for entry in bundle["entry"]:
            if entry["resource"]["resourceType"] in ["Observation", "MedicationStatement"]:
                observaciones_medicaciones_bundle["entry"].append(entry)
        
        # Importar observaciones y medicaciones
        if observaciones_medicaciones_bundle["entry"]:
            print("Importando observaciones y medicaciones...")
            response = requests.post(
                "http://backend:8000/fhir/import",
                json=observaciones_medicaciones_bundle
            )
            
            if response.status_code != 200:
                print(f"Error importando observaciones y medicaciones: {response.text}")
            else:
                print("Observaciones y medicaciones importadas correctamente")
    
    print("Generación de datos de prueba completada.")

if __name__ == "__main__":
    main() 
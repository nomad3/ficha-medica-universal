# Sistema de Ficha Médica Digital con Seguimiento de Suplementos Nutricionales

![Docker](https://img.shields.io/badge/Docker-Containers-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![React](https://img.shields.io/badge/Frontend-React-61DAFB)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue)
![FHIR](https://img.shields.io/badge/Interoperabilidad-HL7%20FHIR-orange)

Sistema integral para la gestión de fichas médicas electrónicas con seguimiento de suplementos nutricionales, diseñado para monitorear el impacto de suplementos como Omega-3 y multivitamínicos en los niveles bioquímicos de los pacientes. Implementa completamente el estándar HL7 FHIR para interoperabilidad entre instituciones de salud.

## 📌 Características Principales

- **Gestión completa de pacientes** con datos personales y médicos
- **Seguimiento de suplementación** (Omega-3, Multivitamínicos, Vitamina D)
- **Monitoreo de biomarcadores** (colesterol, triglicéridos, vitamina D, índice omega-3)
- **Arquitectura moderna** con API REST, React y PostgreSQL
- **Despliegue simplificado** mediante contenedores Docker
- **Interoperabilidad HL7 FHIR** para conectividad con sistemas nacionales e internacionales

## 🛠 Requisitos Previos

- Docker 20.10+
- Docker Compose 2.0+
- Git

## 🚀 Instalación

1. Clonar repositorio:
```bash
git clone https://github.com/tu-usuario/ficha-medica-suplementos.git
cd ficha-medica-suplementos
```

2. Iniciar servicios:
```bash
docker-compose up --build
```

3. Acceder a:
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs

## 📊 Estructura de la API FHIR

### Endpoints FHIR

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/fhir/Patient` | Listar todos los pacientes |
| GET | `/fhir/Patient/{rut}` | Obtener paciente por RUT |
| GET | `/fhir/Observation/{paciente_id}` | Obtener observaciones clínicas |
| GET | `/fhir/MedicationStatement/{paciente_id}` | Obtener historial de suplementos |
| GET | `/fhir/Patient/{rut}/complete` | Obtener ficha completa (Bundle) |
| POST | `/fhir/import` | Importar datos desde otros sistemas |

### Recursos FHIR Implementados

#### Patient
```json
{
  "resourceType": "Patient",
  "id": "1",
  "identifier": [
    {
      "system": "http://minsal.cl/rut",
      "value": "12.345.678-9"
    }
  ],
  "name": [
    {
      "family": "Pérez",
      "given": ["Juan"]
    }
  ],
  "gender": "male",
  "birthDate": "1985-05-15",
  "telecom": [
    {
      "system": "phone",
      "value": "+56912345678"
    }
  ],
  "address": [
    {
      "text": "Av. Principal 123"
    }
  ],
  "contact": [
    {
      "name": {
        "text": "María Pérez +56987654321"
      }
    }
  ]
}
```

#### Observation
```json
{
  "resourceType": "Observation",
  "id": "col-1",
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
    "reference": "Patient/1"
  },
  "effectiveDateTime": "2023-05-01",
  "valueQuantity": {
    "value": 185,
    "unit": "mg/dL",
    "system": "http://unitsofmeasure.org",
    "code": "mg/dL"
  }
}
```

#### MedicationStatement
```json
{
  "resourceType": "MedicationStatement",
  "id": "med-1",
  "status": "active",
  "medicationCodeableConcept": {
    "coding": [
      {
        "system": "http://suplementos.cl/codigo",
        "code": "Omega3",
        "display": "Omega3"
      }
    ],
    "text": "Omega3"
  },
  "subject": {
    "reference": "Patient/1"
  },
  "effectivePeriod": {
    "start": "2023-05-01"
  },
  "dosage": [
    {
      "text": "1000mg"
    }
  ],
  "note": [
    {
      "text": "Paciente reporta mejor estado de ánimo"
    }
  ]
}
```

## 📂 Estructura del Proyecto

```
ficha-medica-suplementos/
├── backend/
│   ├── main.py            # API FHIR y endpoints
│   ├── models.py          # Modelos SQLAlchemy
│   ├── database.py        # Configuración de base de datos
│   ├── create_tables.py   # Script de inicialización
│   └── requirements.txt   # Dependencias Python (incluye fhir.resources)
│
├── frontend/
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   │   ├── PacienteList.jsx           # Lista de pacientes FHIR
│   │   │   ├── PacienteDetail.jsx         # Detalle de paciente FHIR
│   │   │   ├── SupplementHistoryForm.jsx  # Formulario FHIR
│   │   │   ├── SupplementHistoryList.jsx  # Historial FHIR
│   │   │   └── FHIRViewer.jsx             # Visualizador de recursos FHIR
│   │   └── App.js         # Rutas principales
│   └── Dockerfile         # Configuración frontend
│
└── docker-compose.yml     # Orquestación de servicios
```

## 🧪 Desarrollo Local

```bash
# Ver logs específicos
docker-compose logs -f backend

# Acceder a la base de datos
docker-compose exec db psql -U salud_user -d salud_db

# Reiniciar un servicio específico
docker-compose restart backend
```

## 📊 Ejemplos de Uso

### Crear un nuevo paciente (FHIR)
```bash
curl -X POST http://localhost:8000/fhir/import \
  -H "Content-Type: application/json" \
  -d '{
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "resource": {
          "resourceType": "Patient",
          "identifier": [
            {
              "system": "http://minsal.cl/rut",
              "value": "16.789.123-5"
            }
          ],
          "name": [
            {
              "family": "González",
              "given": ["María"]
            }
          ],
          "gender": "female",
          "birthDate": "1985-08-15",
          "telecom": [
            {
              "system": "phone",
              "value": "+56951234567"
            }
          ],
          "address": [
            {
              "text": "Av. Providencia 1234, Santiago"
            }
          ],
          "contact": [
            {
              "name": {
                "text": "Juan Pérez +56987654321"
              }
            }
          ]
        }
      }
    ]
  }'
```

### Obtener ficha completa en formato FHIR
```bash
curl -X GET http://localhost:8000/fhir/Patient/12.345.678-9/complete
```

## 🔄 Interoperabilidad

El sistema implementa completamente el estándar HL7 FHIR, permitiendo:

- Exportar datos a otros sistemas de salud
- Importar datos desde sistemas externos
- Compatibilidad con aplicaciones móviles y portales de pacientes
- Integración con sistemas nacionales de salud

## 🤝 Contribución

1. Crear un fork del proyecto
2. Crear branch de características: `git checkout -b feature/nueva-funcionalidad`
3. Commitear cambios: `git commit -m 'Agrega nueva funcionalidad'`
4. Hacer push al branch: `git push origin feature/nueva-funcionalidad`
5. Abrir Pull Request

## 📄 Licencia

Distribuido bajo licencia MIT. Ver `LICENSE` para más detalles.

## ✉ Contacto

Simón Aguilera - [thesimonaguilera@gmail.com](mailto:thesimonaguilera@gmail.com)

---

_⚠️ Importante: Este sistema está diseñado para fines educativos y de investigación. Para uso clínico real, se requieren validaciones adicionales y cumplimiento con normativas de salud locales._
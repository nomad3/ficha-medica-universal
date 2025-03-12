# Sistema de Ficha Médica Digital con Seguimiento de Suplementos Nutricionales

![Docker](https://img.shields.io/badge/Docker-Containers-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![React](https://img.shields.io/badge/Frontend-React-61DAFB)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue)
![FHIR](https://img.shields.io/badge/Interoperabilidad-HL7%20FHIR-orange)

Sistema integral para la gestión de fichas médicas electrónicas con seguimiento de suplementos nutricionales, diseñado para monitorear el impacto de suplementos como Omega-3 y multivitamínicos en los niveles bioquímicos de los pacientes. Compatible con estándares HL7 FHIR para interoperabilidad entre instituciones de salud.

## 📌 Características Principales

- **Gestión completa de pacientes** con datos personales y médicos
- **Seguimiento de suplementación** (Omega-3, Multivitamínicos, Vitamina D)
- **Monitoreo de biomarcadores** (colesterol, triglicéridos, vitamina D, índice omega-3)
- **Arquitectura moderna** con API REST, React y PostgreSQL
- **Despliegue simplificado** mediante contenedores Docker
- **Interoperabilidad HL7 FHIR** para conectividad con sistemas nacionales e internacionales

## �� Requisitos Previos

- Docker 20.10+
- Docker Compose 2.0+
- Git

## 🛠 Instalación

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

## 📊 Estructura de la API

### Endpoints de Pacientes

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/pacientes/` | Listar todos los pacientes |
| GET | `/pacientes/{id}` | Obtener detalles de un paciente |
| POST | `/pacientes/` | Crear nuevo paciente |
| PUT | `/pacientes/{id}` | Actualizar datos de paciente |
| DELETE | `/pacientes/{id}` | Eliminar paciente |
| GET | `/fhir/Patient/{rut}` | Obtener paciente en formato FHIR |
| GET | `/fhir/Observation/{paciente_id}` | Obtener observaciones FHIR |

### Endpoints de Historial Médico

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/pacientes/{id}/historial` | Obtener historial médico completo |
| POST | `/historial/{paciente_id}` | Registrar nuevo seguimiento de suplemento |
| GET | `/historial/{id}` | Obtener detalle de un registro específico |

### Modelos de Datos

#### Paciente
```json
{
  "id": 1,
  "rut": "12.345.678-9",
  "nombre": "Juan",
  "apellido": "Pérez",
  "fecha_nacimiento": "1985-05-15",
  "sexo": "masculino",
  "direccion": "Av. Principal 123",
  "telefono": "+56912345678",
  "email": "juan.perez@email.cl",
  "isapre": "FONASA",
  "seguros_medicos": "Seguro complementario",
  "contacto_emergencia": "María Pérez +56987654321",
  "consentimiento_datos": true
}
```

#### Historial Médico (Suplemento)
```json
{
  "id": 1,
  "paciente_id": 1,
  "suplemento": "Omega3",
  "dosis": "1000mg",
  "fecha_inicio": "2023-05-01",
  "duracion": "3 meses",
  "colesterol_total": 185,
  "trigliceridos": 150,
  "vitamina_d": 35,
  "omega3_indice": 8,
  "observaciones": "Paciente reporta mejor estado de ánimo"
}
```

## 📂 Estructura del Proyecto

```
ficha-medica-suplementos/
├── backend/
│   ├── main.py            # API principal y endpoints
│   ├── models.py          # Modelos SQLAlchemy
│   ├── database.py        # Configuración de base de datos
│   ├── create_tables.py   # Script de inicialización
│   └── requirements.txt   # Dependencias Python
│
├── frontend/
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   │   ├── PacienteList.jsx           # Lista de pacientes
│   │   │   ├── PacienteDetail.jsx         # Detalle de paciente
│   │   │   ├── SupplementHistoryForm.jsx  # Formulario de suplementos
│   │   │   └── SupplementHistoryList.jsx  # Historial de suplementos
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

### Crear un nuevo paciente
```bash
curl -X POST http://localhost:8000/pacientes/ \
  -H "Content-Type: application/json" \
  -d '{
    "rut": "16.789.123-5",
    "nombre": "María",
    "apellido": "González",
    "fecha_nacimiento": "1985-08-15",
    "sexo": "femenino",
    "direccion": "Av. Providencia 1234, Santiago",
    "telefono": "+56951234567",
    "contacto_emergencia": "Juan Pérez +56987654321",
    "consentimiento_datos": true,
    "isapre": "FONASA",
    "seguros_medicos": "Seguro complementario XYZ",
    "email": "maria.gonzalez@email.cl"
  }'
```

### Registrar seguimiento de suplemento
```bash
curl -X POST http://localhost:8000/historial/1 \
  -H "Content-Type: application/json" \
  -d '{
    "suplemento": "Omega3",
    "dosis": "1000mg",
    "fecha_inicio": "2023-06-01",
    "duracion": "3 meses",
    "colesterol_total": 190,
    "trigliceridos": 145,
    "vitamina_d": 40,
    "omega3_indice": 7,
    "observaciones": "Paciente reporta mejora en concentración"
  }'
```

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
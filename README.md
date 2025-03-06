# Sistema de Ficha Médica Digital con Asesor Virtual Nutricional

![Docker](https://img.shields.io/badge/Docker-Containers-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![React](https://img.shields.io/badge/Frontend-React-61DAFB)

Sistema integral para la gestión de fichas médicas electrónicas con recomendaciones inteligentes de suplementos nutricionales, diseñado para cumplir con los requisitos de la normativa chilena de salud digital.

## 📌 Características Principales

- **Ficha clínica digital interoperable** según estándares chilenos
- **Asesor virtual inteligente** para recomendación de suplementos (Omega3, Multivitamínicos)
- **Gestión completa de pacientes** con historial médico y seguimiento
- **Arquitectura moderna** con microservicios y contenedores Docker
- **Seguridad de datos** con autenticación y cifrado (Ley 19.628)

## 🚀 Requisitos Previos

- Docker 20.10+
- Docker Compose 2.0+
- Node.js 18.x (solo para desarrollo frontend)
- Python 3.9+ (solo para desarrollo backend)

```bash
# Verificar instalaciones
docker --version
docker-compose --version
```

## 🛠 Instalación

1. Clonar repositorio:
```bash
git clone https://github.com/nomad3/ficha-medica-digital.git
cd ficha-medica-digital
```

2. Iniciar servicios:
```bash
docker-compose up --build
```

_La primera ejecución puede tomar 5-10 minutos (descarga de imágenes e instalación de dependencias)_

## 📂 Estructura del Proyecto

```
ficha-medica-digital/
├── backend/
│   ├── main.py            # API principal
│   ├── models.py          # Modelos de base de datos
│   ├── database.py        # Configuración PostgreSQL
│   └── requirements.txt   # Dependencias Python
│
├── frontend/
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   └── App.js         # Rutas principales
│   ├── public/            # Assets estáticos
│   └── Dockerfile         # Configuración frontend
│
└── docker-compose.yml     # Orquestación de servicios
```

## ⚙ Configuración del Entorno

### Variables de Entorno (Backend)
```python
DATABASE_URL=postgresql://usuario:contraseña@db:5432/nombre_bd
SECRET_KEY=clave-secreta-para-JWT
```

### Variables de Entorno (Frontend)
```javascript
REACT_APP_API_URL=http://localhost:8000  # URL de la API
```

_Modificar mediante archivo `.env` en cada directorio correspondiente_

## 🖥 Uso del Sistema

1. Acceder al frontend: `http://localhost:3000`
2. Interfaz administrativa de la API: `http://localhost:8000/docs`
3. Credenciales iniciales:
   - Usuario: `admin@clinica.cl`
   - Contraseña: `Admin1234`

**Funcionalidades clave:**
- Registro de pacientes con RUT chileno
- Historial médico completo con antecedentes familiares
- Sistema de alertas de contraindicaciones
- Generación automática de recomendaciones nutricionales
- API RESTful para integración con otros sistemas

## 🧪 Desarrollo Local

```bash
# Iniciar todos los servicios
docker-compose up

# Reconstruir contenedores después de cambios
docker-compose up --build

# Ver logs específicos
docker-compose logs -f backend
```

**Comandos útiles:**
```bash
# Detener todos los servicios
docker-compose down

# Limpiar recursos no utilizados
docker system prune -a

# Ejecutar migraciones de base de datos
docker-compose exec backend python -m alembic upgrade head
```

## 🤝 Contribución

1. Crear un fork del proyecto
2. Crear branch de características: `git checkout -b feature/nueva-funcionalidad`
3. Commitear cambios: `git commit -m 'Agrega nueva funcionalidad'`
4. Hacer push al branch: `git push origin feature/nueva-funcionalidad`
5. Abrir Pull Request

**Requisitos para contribuciones:**
- Pruebas unitarias para nuevas funcionalidades
- Documentación actualizada
- Cumplimiento de estándares PEP8 (Python) y ESLint (JavaScript)

## 📄 Licencia

Distribuido bajo licencia MIT. Ver `LICENSE` para más detalles.

## ✉ Contacto

Simón Aguilera - [thesimonaguilera@gmail.com](mailto:thesimonaguilera@gmail.com)

---

_⚠️ Importante: Este sistema debe utilizarse como base y requiere configuración adicional para uso en producción, incluyendo:_
- Certificado SSL
- Autenticación con ClaveÚnica
- Backup automatizado de base de datos
- Monitorización de rendimiento
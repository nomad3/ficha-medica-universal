from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base  # Asegurar importación correcta
from sqlalchemy.dialects.postgresql import UUID
import uuid

class HistorialMedico(Base):
    __tablename__ = "historial_medico"
    id = Column(Integer, primary_key=True)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey('pacientes.id'))
    grupo_sanguineo = Column(String(3))
    antecedentes_familiares = Column(Text)
    tratamientos_actuales = Column(Text)
    habitos = Column(Text)
    suplemento = Column(String(50))          # Omega3, Multivitamínico, etc
    dosis = Column(String(20))               # 1000mg/día
    fecha_inicio = Column(String)            # Fecha inicio suplementación
    duracion = Column(String)                # 3 meses
    colesterol_total = Column(Integer)       # mg/dL
    trigliceridos = Column(Integer)          # mg/dL
    vitamina_d = Column(Integer)             # ng/mL
    omega3_indice = Column(Integer)          # Porcentaje
    observaciones = Column(Text)
    
    paciente = relationship("Paciente", back_populates="historial")

class Paciente(Base):
    __tablename__ = "pacientes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rut = Column(String(12), unique=True)
    nombre = Column(String(50))
    apellido = Column(String(50))
    fecha_nacimiento = Column(String)
    sexo = Column(String(10))
    direccion = Column(String(100))
    isapre = Column(String(50), nullable=True)
    seguros_medicos = Column(String(100), nullable=True)
    telefono = Column(String(20))
    email = Column(String(50), nullable=True)
    contacto_emergencia = Column(String(100))
    consentimiento_datos = Column(Boolean, default=False)
    tipo_sangre = Column(String(3))
    alergias = Column(Text)
    actividad_fisica = Column(String(20))
    dieta = Column(String(20))
    problema_salud_principal = Column(String(50))
    objetivo_suplementacion = Column(Text)
    
    historial = relationship("HistorialMedico", back_populates="paciente")
    medicaciones = relationship("Medicacion", back_populates="paciente")
    # ... resto de campos ... 

class Medicacion(Base):
    __tablename__ = "medicaciones"
    
    id = Column(Integer, primary_key=True)
    paciente_id = Column(UUID(as_uuid=True), ForeignKey('pacientes.id'))
    codigo = Column(String(50))  # Código del medicamento o suplemento
    nombre = Column(String(100), nullable=True)  # Nombre descriptivo
    estado = Column(String(20))  # active, completed, etc.
    fecha_inicio = Column(String)  # Fecha de inicio
    fecha_fin = Column(String, nullable=True)  # Fecha de fin (opcional)
    dosis = Column(String(100))  # Información de dosificación
    
    # Relación con el paciente
    paciente = relationship("Paciente", back_populates="medicaciones") 
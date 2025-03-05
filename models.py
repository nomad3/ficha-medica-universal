from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Paciente(Base):
    __tablename__ = "pacientes"
    rut = Column(String(12), unique=True)  # Requerido en Chile
    prevision = Column(String(50))  # FONASA/ISAPRE
    contacto_emergencia = Column(String(100))
    consentimiento_datos = Column(Boolean, default=False)  # Ley de protección de datos

class HistorialMedico(Base):
    __tablename__ = "historial_medico"
    grupo_sanguineo = Column(String(3))
    antecedentes_familiares = Column(Text)
    tratamientos_actuales = Column(Text)
    habitos = Column(Text)  # Ejercicio, tabaquismo, alcohol 
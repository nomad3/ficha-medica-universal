# Sistema de Asesor Nutricional con IA para optimización de suplementos
import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class AsesorNutricional:
    """
    Clase principal que implementa la lógica de recomendación y análisis
    de suplementos nutricionales utilizando la API del sistema.
    """
    
    def __init__(self, api_base_url="http://localhost:8000"):
        """
        Inicializa el asesor nutricional.
        
        Args:
            api_base_url: URL base de la API
        """
        self.api_base_url = api_base_url
    
    def generar_recomendacion(self, paciente_id):
        """
        Genera recomendaciones de suplementos basadas en el perfil del paciente
        y su historial médico utilizando la API.
        
        Args:
            paciente_id: ID del paciente
            
        Returns:
            Dict con recomendaciones y advertencias
        """
        try:
            response = requests.post(
                f"{self.api_base_url}/ai/recomendaciones",
                json={"paciente_id": paciente_id}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener recomendaciones: {e}")
            return {
                "recomendaciones": [],
                "advertencias": ["No se pudieron generar recomendaciones. Servicio no disponible."]
            }
    
    def predecir_tendencias(self, paciente_id, biomarcador, dias_prediccion=90):
        """
        Predice la evolución de un biomarcador basado en el historial y la
        suplementación actual utilizando la API.
        
        Args:
            paciente_id: ID del paciente
            biomarcador: Biomarcador a predecir (colesterol_total, trigliceridos, etc.)
            dias_prediccion: Número de días a predecir
            
        Returns:
            Dict con predicciones, tendencia y recomendaciones
        """
        try:
            response = requests.post(
                f"{self.api_base_url}/ai/prediccion-tendencias",
                json={
                    "paciente_id": paciente_id,
                    "biomarcador": biomarcador,
                    "dias_prediccion": dias_prediccion
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener predicciones: {e}")
            return {
                "mensaje": "No se pudieron generar predicciones. Servicio no disponible.",
                "predicciones": []
            }
    
    def detectar_anomalias(self, paciente_id):
        """
        Detecta valores anómalos en los biomarcadores del paciente utilizando la API.
        
        Args:
            paciente_id: ID del paciente
            
        Returns:
            Dict con anomalías detectadas y recomendaciones
        """
        try:
            response = requests.post(
                f"{self.api_base_url}/ai/deteccion-anomalias",
                json={"paciente_id": paciente_id}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al detectar anomalías: {e}")
            return {
                "mensaje": "No se pudieron detectar anomalías. Servicio no disponible.",
                "anomalias": [],
                "fecha_analisis": datetime.now().strftime("%Y-%m-%d")
            }
    
    def optimizar_suplementacion(self, paciente_id, objetivo=None):
        """
        Genera un plan optimizado de suplementación utilizando la API.
        
        Args:
            paciente_id: ID del paciente
            objetivo: Objetivo específico de salud (opcional)
            
        Returns:
            Dict con plan de suplementación optimizado
        """
        try:
            payload = {"paciente_id": paciente_id}
            if objetivo:
                payload["objetivo"] = objetivo
                
            response = requests.post(
                f"{self.api_base_url}/ai/optimizacion-suplementos",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al optimizar suplementación: {e}")
            return {
                "mensaje": "No se pudo generar plan de suplementación. Servicio no disponible.",
                "suplementos_recomendados": []
            }

# Clase para integración con FHIR
class AsesorFHIR:
    """
    Clase para obtener y procesar datos en formato FHIR.
    Permite la interoperabilidad con otros sistemas de salud.
    """
    
    def __init__(self, api_base_url="http://localhost:8000"):
        """
        Inicializa el adaptador FHIR.
        
        Args:
            api_base_url: URL base de la API
        """
        self.api_base_url = api_base_url
    
    def obtener_paciente(self, rut):
        """
        Obtiene datos del paciente en formato FHIR.
        
        Args:
            rut: RUT del paciente
            
        Returns:
            Recurso Patient de FHIR
        """
        try:
            response = requests.get(f"{self.api_base_url}/fhir/Patient/{rut}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener paciente: {e}")
            return None
    
    def obtener_observaciones(self, paciente_id):
        """
        Obtiene observaciones del paciente en formato FHIR.
        
        Args:
            paciente_id: ID del paciente
            
        Returns:
            Lista de recursos Observation de FHIR
        """
        try:
            response = requests.get(f"{self.api_base_url}/fhir/Observation/{paciente_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener observaciones: {e}")
            return []
    
    def obtener_medicamentos(self, paciente_id):
        """
        Obtiene historial de medicamentos/suplementos en formato FHIR.
        
        Args:
            paciente_id: ID del paciente
            
        Returns:
            Lista de recursos MedicationStatement de FHIR
        """
        try:
            response = requests.get(f"{self.api_base_url}/fhir/MedicationStatement/{paciente_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener medicamentos: {e}")
            return []
    
    def obtener_ficha_completa(self, rut):
        """
        Obtiene la ficha completa del paciente en formato FHIR Bundle.
        
        Args:
            rut: RUT del paciente
            
        Returns:
            Bundle FHIR con todos los recursos del paciente
        """
        try:
            response = requests.get(f"{self.api_base_url}/fhir/Patient/{rut}/complete")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener ficha completa: {e}")
            return None

# Ejemplo de uso
if __name__ == "__main__":
    # Crear instancias de los asesores
    asesor = AsesorNutricional()
    asesor_fhir = AsesorFHIR()
    
    # Ejemplo: obtener recomendaciones para un paciente
    paciente_id = 1
    recomendaciones = asesor.generar_recomendacion(paciente_id)
    print(f"Recomendaciones para paciente {paciente_id}:")
    print(json.dumps(recomendaciones, indent=2, ensure_ascii=False))
    
    # Ejemplo: predecir tendencia de colesterol
    predicciones = asesor.predecir_tendencias(paciente_id, "colesterol_total", 90)
    print(f"\nPredicciones de colesterol para paciente {paciente_id}:")
    print(json.dumps(predicciones, indent=2, ensure_ascii=False))
    
    # Ejemplo: detectar anomalías
    anomalias = asesor.detectar_anomalias(paciente_id)
    print(f"\nAnomalías detectadas para paciente {paciente_id}:")
    print(json.dumps(anomalias, indent=2, ensure_ascii=False))
    
    # Ejemplo: obtener datos FHIR
    rut = "12.345.678-9"
    paciente_fhir = asesor_fhir.obtener_paciente(rut)
    if paciente_fhir:
        print(f"\nDatos FHIR del paciente con RUT {rut}:")
        print(f"Nombre: {paciente_fhir.get('name', [{}])[0].get('given', [''])[0]} {paciente_fhir.get('name', [{}])[0].get('family', '')}")
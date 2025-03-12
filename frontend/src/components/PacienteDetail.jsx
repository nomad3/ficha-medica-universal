import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import SupplementHistoryForm from './SupplementHistoryForm';
import SupplementHistoryList from './SupplementHistoryList';
import FHIRViewer from './FHIRViewer';
import AIRecommendations from './AIRecommendations';
import PredictiveTrends from './PredictiveTrends';
import AnomalyDetection from './AnomalyDetection';
import SupplementOptimization from './SupplementOptimization';

const PacienteDetail = () => {
  const { id } = useParams();
  const [paciente, setPaciente] = useState(null);
  const [observaciones, setObservaciones] = useState([]);
  const [medicamentos, setMedicamentos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('historial');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Obtener datos del paciente en formato FHIR por ID
        const patientResponse = await axios.get(`http://localhost:8000/fhir/Patient/${id}`);
        setPaciente(patientResponse.data);
        
        // Obtener observaciones en formato FHIR
        const observationsResponse = await axios.get(`http://localhost:8000/fhir/Observation/${id}`);
        setObservaciones(observationsResponse.data);
        
        // Obtener medicamentos/suplementos en formato FHIR
        const medicationsResponse = await axios.get(`http://localhost:8000/fhir/MedicationStatement/${id}`);
        setMedicamentos(medicationsResponse.data);
        
        setLoading(false);
      } catch (err) {
        console.error('Error al cargar datos del paciente:', err);
        setError('Error al cargar datos del paciente');
        setLoading(false);
      }
    };
    
    if (id) {
      fetchData();
    }
  }, [id]);

  if (loading) return <div>Cargando datos del paciente...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!paciente) return <div>No se encontró el paciente</div>;

  // Extraer datos del paciente del formato FHIR con verificación
  const nombre = paciente.name && paciente.name[0] && paciente.name[0].given ? paciente.name[0].given[0] : 'Sin nombre';
  const apellido = paciente.name && paciente.name[0] ? paciente.name[0].family : 'Sin apellido';
  const fechaNacimiento = paciente.birthDate || 'No disponible';
  const rut = paciente.identifier && paciente.identifier[0] ? paciente.identifier[0].value : 'Sin RUT';
  const contactoEmergencia = paciente.contact && paciente.contact[0] && paciente.contact[0].name ? 
    paciente.contact[0].name.text : 'No disponible';

  return (
    <div className="paciente-detail">
      <div className="paciente-header">
        <h2>Ficha Clínica: {nombre} {apellido}</h2>
        <div className="paciente-info">
          <p><strong>RUT:</strong> {rut}</p>
          <p><strong>Fecha Nacimiento:</strong> {fechaNacimiento}</p>
          <p><strong>Contacto Emergencia:</strong> {contactoEmergencia}</p>
        </div>
        <Link to="/" className="btn-back">Volver al listado</Link>
      </div>
      
      <div className="tabs">
        <button 
          className={activeTab === 'historial' ? 'active' : ''} 
          onClick={() => setActiveTab('historial')}
        >
          Historial de Suplementos
        </button>
        <button 
          className={activeTab === 'recomendaciones' ? 'active' : ''} 
          onClick={() => setActiveTab('recomendaciones')}
        >
          Recomendaciones IA
        </button>
        <button 
          className={activeTab === 'predicciones' ? 'active' : ''} 
          onClick={() => setActiveTab('predicciones')}
        >
          Análisis Predictivo
        </button>
        <button 
          className={activeTab === 'anomalias' ? 'active' : ''} 
          onClick={() => setActiveTab('anomalias')}
        >
          Detección de Anomalías
        </button>
        <button 
          className={activeTab === 'optimizacion' ? 'active' : ''} 
          onClick={() => setActiveTab('optimizacion')}
        >
          Plan Óptimo
        </button>
        <button 
          className={activeTab === 'fhir' ? 'active' : ''} 
          onClick={() => setActiveTab('fhir')}
        >
          Datos FHIR
        </button>
      </div>
      
      <div className="tab-content">
        {activeTab === 'historial' && (
          <div>
            <SupplementHistoryForm pacienteId={id} />
            {medicamentos && medicamentos.length > 0 ? (
              <SupplementHistoryList data={medicamentos} />
            ) : (
              <p>No hay registros de suplementos</p>
            )}
          </div>
        )}
        
        {activeTab === 'recomendaciones' && (
          <AIRecommendations pacienteId={id} />
        )}
        
        {activeTab === 'predicciones' && (
          <PredictiveTrends pacienteId={id} />
        )}
        
        {activeTab === 'anomalias' && (
          <AnomalyDetection pacienteId={id} />
        )}
        
        {activeTab === 'optimizacion' && (
          <SupplementOptimization pacienteId={id} />
        )}
        
        {activeTab === 'fhir' && (
          <FHIRViewer 
            paciente={paciente} 
            observaciones={observaciones || []} 
            medicamentos={medicamentos || []} 
          />
        )}
      </div>
    </div>
  );
};

export default PacienteDetail; 
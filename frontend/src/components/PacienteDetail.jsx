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
  const [historial, setHistorial] = useState([]);
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
        
        // Obtener observaciones (biomarcadores) del paciente
        const observationsResponse = await axios.get(`http://localhost:8000/fhir/Observation/${id}`);
        console.log('Observaciones:', observationsResponse.data);
        setObservaciones(observationsResponse.data);
        
        // Obtener medicamentos (suplementos) del paciente
        const medicationsResponse = await axios.get(`http://localhost:8000/fhir/MedicationStatement/${id}`);
        console.log('Medicamentos:', medicationsResponse.data);
        setMedicamentos(medicationsResponse.data);
        
        // Convertir medicamentos a formato para SupplementHistoryList
        const historialData = medicationsResponse.data.map(med => {
          // Extraer valores de biomarcadores de las observaciones relacionadas
          const fecha = med.effectivePeriod?.start || '';
          const observacionesRelacionadas = observationsResponse.data.filter(
            obs => obs.effectiveDateTime === fecha
          );
          
          // Buscar valores específicos
          const colesterol = observacionesRelacionadas.find(
            obs => obs.code?.coding?.[0]?.code === '2093-3'
          )?.valueQuantity?.value || 0;
          
          const trigliceridos = observacionesRelacionadas.find(
            obs => obs.code?.coding?.[0]?.code === '2571-8'
          )?.valueQuantity?.value || 0;
          
          const vitaminaD = observacionesRelacionadas.find(
            obs => obs.code?.coding?.[0]?.code === '14635-7'
          )?.valueQuantity?.value || 0;
          
          const omega3 = observacionesRelacionadas.find(
            obs => obs.code?.coding?.[0]?.code === 'omega3_indice' || obs.code?.coding?.[0]?.code === 'omega3-index'
          )?.valueQuantity?.value || 0;
          
          return {
            suplemento: med.medicationCodeableConcept?.coding?.[0]?.display || 'Desconocido',
            dosis: med.dosage?.[0]?.text || '',
            fecha_inicio: fecha,
            colesterol_total: colesterol,
            trigliceridos: trigliceridos,
            vitamina_d: vitaminaD,
            omega3_indice: omega3,
            observaciones: med.note?.[0]?.text || ''
          };
        });
        
        setHistorial(historialData);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching patient data:', error);
        setError('Error al cargar los datos del paciente');
        setLoading(false);
      }
    };
    
    fetchData();
  }, [id]);

  if (loading) return <div>Cargando datos del paciente...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!paciente) return <div>No se encontró el paciente</div>;

  return (
    <div className="paciente-detail">
      <div className="paciente-header">
        <h2>
          {paciente.name?.[0]?.given?.[0] || ''} {paciente.name?.[0]?.family || ''}
        </h2>
        <p>RUT: {paciente.identifier?.[0]?.value || 'No disponible'}</p>
        <p>Fecha de nacimiento: {paciente.birthDate || 'No disponible'}</p>
        <Link to="/" className="back-link">← Volver a la lista</Link>
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
          Tendencias Predictivas
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
          Optimización de Suplementos
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
            <SupplementHistoryList data={historial} />
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

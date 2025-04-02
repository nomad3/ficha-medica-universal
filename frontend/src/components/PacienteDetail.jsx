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

  // Use consistent loading/error messages
  if (loading) return <div className="loading-message">Cargando datos del paciente...</div>;
  if (error) return <div className="error-message">{error}</div>;
  if (!paciente) return <div className="card"><p>No se encontró el paciente</p></div>; // Wrap message in card

  // Combine name parts safely
  const nombreCompleto = [
    paciente.name?.[0]?.given?.join(' '),
    paciente.name?.[0]?.family
  ].filter(Boolean).join(' ') || 'Nombre no disponible';

  return (
    <div className="paciente-detail card"> {/* Apply card class to the main container */}
      <div className="paciente-header mb-3"> {/* Add margin bottom */}
        <Link to="/" className="back-link mb-2">← Volver a la lista</Link> {/* Style back link */}
        <h2 className="paciente-detail-name">
          {nombreCompleto}
        </h2>
        <div className="paciente-detail-meta"> {/* Group meta info */}
          <span>RUT: {paciente.identifier?.[0]?.value || 'No disponible'}</span>
          <span>Fecha de nacimiento: {paciente.birthDate || 'No disponible'}</span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tabs mb-3">
        <button
          className={`tab-button ${activeTab === 'historial' ? 'active' : ''}`}
          onClick={() => setActiveTab('historial')}
        >
          Historial
        </button>
        <button
          className={`tab-button ${activeTab === 'recomendaciones' ? 'active' : ''}`}
          onClick={() => setActiveTab('recomendaciones')}
        >
          Recomendaciones
        </button>
        <button
          className={`tab-button ${activeTab === 'predicciones' ? 'active' : ''}`}
          onClick={() => setActiveTab('predicciones')}
        >
          Tendencias
        </button>
        <button
          className={`tab-button ${activeTab === 'anomalias' ? 'active' : ''}`}
          onClick={() => setActiveTab('anomalias')}
        >
          Anomalías
        </button>
        <button
          className={`tab-button ${activeTab === 'optimizacion' ? 'active' : ''}`}
          onClick={() => setActiveTab('optimizacion')}
        >
          Optimización
        </button>
        <button
          className={`tab-button ${activeTab === 'fhir' ? 'active' : ''}`}
          onClick={() => setActiveTab('fhir')}
        >
          Datos FHIR
        </button>
      </div>

      {/* Tab Content Area */}
      <div className="tab-content">
        {activeTab === 'historial' && (
          <div className="tab-pane"> {/* Add class for potential tab-specific padding/margins */}
            <SupplementHistoryForm pacienteId={id} />
            <SupplementHistoryList data={historial} />
          </div>
        )}

        {activeTab === 'recomendaciones' && (
          <div className="tab-pane">
            <AIRecommendations pacienteId={id} />
          </div>
        )}

        {activeTab === 'predicciones' && (
          <div className="tab-pane">
            <PredictiveTrends pacienteId={id} />
          </div>
        )}

        {activeTab === 'anomalias' && (
          <div className="tab-pane">
            <AnomalyDetection pacienteId={id} />
          </div>
        )}

        {activeTab === 'optimizacion' && (
          <div className="tab-pane">
            <SupplementOptimization pacienteId={id} />
          </div>
        )}

        {activeTab === 'fhir' && (
          <div className="tab-pane">
            <FHIRViewer
              paciente={paciente}
              observaciones={observaciones || []}
              medicamentos={medicamentos || []}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default PacienteDetail;

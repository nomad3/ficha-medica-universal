import React, { useState, useEffect } from 'react';
import axios from 'axios';

const FHIRViewer = ({ pacienteId, rut }) => {
  const [fhirData, setFhirData] = useState(null);
  const [observations, setObservations] = useState([]);
  const [medications, setMedications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFHIRData = async () => {
      try {
        setLoading(true);
        // Obtener datos del paciente en formato FHIR
        const patientResponse = await axios.get(`http://localhost:8000/fhir/Patient/${rut}`);
        setFhirData(patientResponse.data);
        
        // Obtener observaciones en formato FHIR
        const observationsResponse = await axios.get(`http://localhost:8000/fhir/Observation/${pacienteId}`);
        setObservations(observationsResponse.data);
        
        // Obtener medicamentos/suplementos en formato FHIR
        const medicationsResponse = await axios.get(`http://localhost:8000/fhir/MedicationStatement/${pacienteId}`);
        setMedications(medicationsResponse.data);
        
        setLoading(false);
      } catch (err) {
        setError('Error al cargar datos FHIR');
        setLoading(false);
        console.error(err);
      }
    };
    
    if (rut && pacienteId) {
      fetchFHIRData();
    }
  }, [rut, pacienteId]);

  if (loading) return <div>Cargando datos FHIR...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!fhirData) return null;

  return (
    <div className="fhir-viewer">
      <h3>Datos FHIR</h3>
      <div className="fhir-section">
        <h4>Paciente</h4>
        <pre>{JSON.stringify(fhirData, null, 2)}</pre>
      </div>
      
      {observations.length > 0 && (
        <div className="fhir-section">
          <h4>Observaciones</h4>
          {observations.map((obs, index) => (
            <div key={index} className="observation-card">
              <h5>{obs.code.coding[0].display}</h5>
              <p>Valor: {obs.valueQuantity.value} {obs.valueQuantity.unit}</p>
              <p>Fecha: {obs.effectiveDateTime}</p>
            </div>
          ))}
        </div>
      )}
      
      {medications.length > 0 && (
        <div className="fhir-section">
          <h4>Suplementos</h4>
          {medications.map((med, index) => (
            <div key={index} className="medication-card">
              <h5>{med.medicationCodeableConcept.text}</h5>
              <p>Dosis: {med.dosage[0].text}</p>
              <p>Inicio: {med.effectivePeriod.start}</p>
              {med.note && <p>Observaciones: {med.note[0].text}</p>}
            </div>
          ))}
        </div>
      )}
      
      <div className="fhir-info">
        <p>Estos datos son compatibles con el estándar HL7 FHIR para interoperabilidad entre sistemas de salud.</p>
      </div>
    </div>
  );
};

export default FHIRViewer; 
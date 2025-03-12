import React, { useState } from 'react';

const FHIRViewer = ({ paciente, observaciones, medicamentos }) => {
  const [activeResource, setActiveResource] = useState('paciente');

  const formatJSON = (json) => {
    return JSON.stringify(json, null, 2);
  };

  return (
    <div className="fhir-viewer">
      <h3>Visualizador de Datos FHIR</h3>
      
      <div className="resource-selector">
        <button 
          className={activeResource === 'paciente' ? 'active' : ''} 
          onClick={() => setActiveResource('paciente')}
        >
          Patient
        </button>
        <button 
          className={activeResource === 'observaciones' ? 'active' : ''} 
          onClick={() => setActiveResource('observaciones')}
        >
          Observations
        </button>
        <button 
          className={activeResource === 'medicamentos' ? 'active' : ''} 
          onClick={() => setActiveResource('medicamentos')}
        >
          MedicationStatements
        </button>
      </div>
      
      <div className="resource-content">
        <pre>
          {activeResource === 'paciente' && formatJSON(paciente)}
          {activeResource === 'observaciones' && formatJSON(observaciones)}
          {activeResource === 'medicamentos' && formatJSON(medicamentos)}
        </pre>
      </div>
      
      <div className="fhir-info">
        <p>
          <strong>FHIR (Fast Healthcare Interoperability Resources)</strong> es un estándar 
          para el intercambio electrónico de información sanitaria.
        </p>
      </div>
    </div>
  );
};

export default FHIRViewer; 
import React, { useState } from 'react';

const FHIRViewer = ({ paciente, observaciones, medicamentos }) => {
  const [activeResource, setActiveResource] = useState('paciente');

  const formatJSON = (json) => {
    return JSON.stringify(json, null, 2);
  };

  return (
    <div className="fhir-viewer-section"> {/* Section container */}
      <h4 className="mb-2">Visualizador de Datos FHIR</h4>

      {/* Resource Selector Buttons */}
      <div className="resource-selector mb-2">
        <button
          className={`resource-button ${activeResource === 'paciente' ? 'active' : ''}`}
          onClick={() => setActiveResource('paciente')}
        >
          Patient
        </button>
        <button
          className={`resource-button ${activeResource === 'observaciones' ? 'active' : ''}`}
          onClick={() => setActiveResource('observaciones')}
        >
          Observations
        </button>
        <button
          className={`resource-button ${activeResource === 'medicamentos' ? 'active' : ''}`}
          onClick={() => setActiveResource('medicamentos')}
        >
          MedicationStatements
        </button>
      </div>

      {/* JSON Content Display */}
      <div className="resource-content card"> {/* Wrap pre in a card */}
        <pre className="fhir-json-pre">
          {activeResource === 'paciente' && formatJSON(paciente ?? {})}
          {activeResource === 'observaciones' && formatJSON(observaciones ?? [])}
          {activeResource === 'medicamentos' && formatJSON(medicamentos ?? [])}
        </pre>
      </div>

      {/* Info Text */}
      <div className="fhir-info mt-2">
        <p>
          <strong>FHIR (Fast Healthcare Interoperability Resources)</strong> es un estándar
          para el intercambio electrónico de información sanitaria. Los datos se muestran en formato JSON.
        </p>
      </div>
    </div>
  );
};

export default FHIRViewer;

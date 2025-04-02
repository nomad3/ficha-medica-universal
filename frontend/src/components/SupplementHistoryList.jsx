import React from 'react';

const SupplementHistoryList = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="no-data-message">
        <h4>Historial de Suplementación</h4>
        <p>No hay registros de suplementación para este paciente.</p>
      </div>
    );
  }

  return (
    <div className="supplement-history-list">
      <h4 className="mb-2">Historial de Suplementación</h4>
      <div className="history-entries">
        {data.map((item, index) => (
          <div key={index} className="history-entry card mb-2"> {/* Use card style for each entry */}
            <div className="entry-header mb-1">
              <span className="suplemento-name">{item.suplemento || 'N/A'}</span>
              <span className="fecha-inicio">({item.fecha_inicio || 'Fecha N/A'})</span>
            </div>
            <div className="entry-details">
              <p><strong>Dosis:</strong> {item.dosis || 'N/A'}</p>
              {item.observaciones && <p><strong>Observaciones:</strong> {item.observaciones}</p>}
            </div>
            <div className="entry-biomarkers mt-1">
              <span className="biomarker"><strong>Colesterol:</strong> {item.colesterol_total ?? 'N/A'} mg/dL</span>
              <span className="biomarker"><strong>Triglicéridos:</strong> {item.trigliceridos ?? 'N/A'} mg/dL</span>
              <span className="biomarker"><strong>Vit. D:</strong> {item.vitamina_d ?? 'N/A'} ng/mL</span>
              <span className="biomarker"><strong>Omega-3:</strong> {item.omega3_indice ?? 'N/A'}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SupplementHistoryList;

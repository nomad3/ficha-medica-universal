import React, { useState } from 'react';
import axios from 'axios';

const AnomalyDetection = ({ pacienteId }) => {
  const [anomalies, setAnomalies] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const detectAnomalies = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post('http://localhost:8000/ai/deteccion-anomalias', {
        paciente_id: pacienteId
      });
      
      setAnomalies(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error al detectar anomalías:', err);
      setError('No se pudieron detectar anomalías');
      setLoading(false);
    }
  };

  // Return CSS class modifier based on type
  const getAnomalyClass = (tipo) => {
    return tipo === 'alto' ? 'anomaly-card--alto' : 'anomaly-card--bajo'; // Assuming 'bajo' is the other type
  };

  return (
    <div className="anomaly-detection-section"> {/* Section container */}
      <h4 className="mb-2">Detección de Anomalías en Biomarcadores</h4>

      {!anomalies && !loading && (
        <button onClick={detectAnomalies} className="form-button"> {/* Consistent button */}
          Analizar Valores Anómalos
        </button>
      )}

      {/* Use consistent loading/error messages */}
      {loading && <p className="loading-message mt-2">Analizando datos y detectando anomalías...</p>}
      {error && <p className="error-message mt-2">{error}</p>}

      {anomalies && (
        <div className="anomalies-results-container mt-2">
          <div className="analysis-summary card mb-2"> {/* Wrap summary in card */}
            <p className="analysis-date mb-1">
              <strong>Fecha de análisis:</strong> {anomalies.fecha_analisis ?? 'N/A'}
            </p>
            {/* Use specific classes for message styling */}
            <p className={`analysis-message ${anomalies.anomalias.length > 0 ? 'message--warning' : 'message--success'}`}>
              {anomalies.mensaje}
            </p>
          </div>

          {anomalies.anomalias.length > 0 ? (
            <div className="anomalies-list-container">
              <h5 className="mb-1">Valores fuera de rango detectados:</h5>
              <div className="anomalies-grid"> {/* Grid layout for anomaly cards */}
                {anomalies.anomalias.map((anomaly, index) => (
                  // Use card base class + modifier for type
                  <div key={index} className={`card anomaly-card ${getAnomalyClass(anomaly.tipo)}`}>
                    <h6 className="anomaly-biomarker mb-1">{anomaly.biomarcador ?? 'N/A'}</h6>
                    <p className="anomaly-value">
                      <strong>{anomaly.valor ?? 'N/A'} {anomaly.unidad ?? ''}</strong>
                      <span className="anomaly-type"> ({anomaly.tipo ?? 'N/A'})</span>
                    </p>
                    <p className="anomaly-range">
                      Rango normal: {anomaly.rango_normal ?? 'N/A'}
                    </p>
                    <p className="anomaly-recommendation mt-1">
                      <strong>Recomendación:</strong> {anomaly.recomendacion ?? 'N/A'}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            // No specific message needed if handled by analysis-message
            null
          )}
        </div>
      )}
    </div>
  );
};

export default AnomalyDetection;

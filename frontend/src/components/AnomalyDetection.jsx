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

  const getAnomalyColor = (tipo) => {
    return tipo === 'alto' ? 'red' : 'orange';
  };

  return (
    <div className="anomaly-detection">
      <h3>Detección de Anomalías en Biomarcadores</h3>
      
      {!anomalies && !loading && (
        <button onClick={detectAnomalies} className="btn-primary">
          Analizar Valores Anómalos
        </button>
      )}
      
      {loading && <p>Analizando datos y detectando anomalías...</p>}
      
      {error && <p className="error">{error}</p>}
      
      {anomalies && (
        <div className="anomalies-results">
          <p className="analysis-date">
            <strong>Fecha de análisis:</strong> {anomalies.fecha_analisis}
          </p>
          
          <p className={anomalies.anomalias.length > 0 ? 'message warning' : 'message success'}>
            {anomalies.mensaje}
          </p>
          
          {anomalies.anomalias.length > 0 ? (
            <div className="anomalies-list">
              <h4>Valores fuera de rango:</h4>
              {anomalies.anomalias.map((anomaly, index) => (
                <div key={index} className="anomaly-card" style={{borderColor: getAnomalyColor(anomaly.tipo)}}>
                  <h5>{anomaly.biomarcador}</h5>
                  <p className="anomaly-value" style={{color: getAnomalyColor(anomaly.tipo)}}>
                    <strong>{anomaly.valor} {anomaly.unidad}</strong> 
                    <span className="anomaly-type">({anomaly.tipo})</span>
                  </p>
                  <p className="normal-range">
                    Rango normal: {anomaly.rango_normal}
                  </p>
                  <p className="recommendation">
                    <strong>Recomendación:</strong> {anomaly.recomendacion}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="no-anomalies">Todos los biomarcadores están dentro de rangos normales.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default AnomalyDetection; 
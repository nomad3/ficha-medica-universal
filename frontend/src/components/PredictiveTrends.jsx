import React, { useState } from 'react';
import axios from 'axios';

const PredictiveTrends = ({ pacienteId }) => {
  const [selectedBiomarker, setSelectedBiomarker] = useState('colesterol_total');
  const [predictionDays, setPredictionDays] = useState(90);
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const biomarkers = [
    { value: 'colesterol_total', label: 'Colesterol Total', unit: 'mg/dL' },
    { value: 'trigliceridos', label: 'Triglicéridos', unit: 'mg/dL' },
    { value: 'vitamina_d', label: 'Vitamina D', unit: 'ng/mL' },
    { value: 'omega3_indice', label: 'Índice Omega-3', unit: '%' }
  ];

  const getPredictions = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post('http://localhost:8000/ai/prediccion-tendencias', {
        paciente_id: pacienteId,
        biomarcador: selectedBiomarker,
        dias_prediccion: predictionDays
      });
      
      setPredictions(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error al obtener predicciones:', err);
      setError('No se pudieron generar predicciones');
      setLoading(false);
    }
  };

  const getBiomarkerLabel = (value) => {
    const biomarker = biomarkers.find(b => b.value === value);
    return biomarker ? biomarker.label : value;
  };

  const getBiomarkerUnit = (value) => {
    const biomarker = biomarkers.find(b => b.value === value);
    return biomarker ? biomarker.unit : '';
  };

  const getTrendEmoji = () => {
    if (!predictions) return '';
    
    switch (predictions.tendencia) {
      case 'ascendente_rapida': return '🔺';
      case 'ascendente_lenta': return '↗️';
      case 'descendente_rapida': return '🔻';
      case 'descendente_lenta': return '↘️';
      case 'estable': return '➡️';
      default: return '';
    }
  };

  return (
    <div className="predictive-trends">
      <h3>Análisis Predictivo de Biomarcadores</h3>
      
      <div className="prediction-controls">
        <div className="form-group">
          <label>Biomarcador:</label>
          <select 
            value={selectedBiomarker} 
            onChange={(e) => setSelectedBiomarker(e.target.value)}
          >
            {biomarkers.map(b => (
              <option key={b.value} value={b.value}>{b.label}</option>
            ))}
          </select>
        </div>
        
        <div className="form-group">
          <label>Días de predicción:</label>
          <select 
            value={predictionDays} 
            onChange={(e) => setPredictionDays(parseInt(e.target.value))}
          >
            <option value={30}>30 días</option>
            <option value={90}>90 días</option>
            <option value={180}>180 días</option>
          </select>
        </div>
        
        <button onClick={getPredictions} className="btn-primary">
          Generar Predicción
        </button>
      </div>
      
      {loading && <p>Analizando datos y generando predicciones...</p>}
      
      {error && <p className="error">{error}</p>}
      
      {predictions && (
        <div className="predictions-results">
          <div className="prediction-summary">
            <h4>
              {getBiomarkerLabel(selectedBiomarker)}: {predictions.valor_actual} {getBiomarkerUnit(selectedBiomarker)}
            </h4>
            <p>
              <strong>Tendencia:</strong> {getTrendEmoji()} {predictions.tendencia.replace('_', ' ')}
            </p>
            <p className="recommendation">
              <strong>Recomendación:</strong> {predictions.recomendacion}
            </p>
          </div>
          
          <div className="prediction-table">
            <h4>Valores Proyectados</h4>
            <table>
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Valor Proyectado</th>
                </tr>
              </thead>
              <tbody>
                {predictions.predicciones.map((pred, index) => (
                  <tr key={index}>
                    <td>{pred.fecha}</td>
                    <td>{pred.valor_predicho} {getBiomarkerUnit(selectedBiomarker)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default PredictiveTrends; 
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
    <div className="predictive-trends-section"> {/* Section container */}
      <h4 className="mb-2">Análisis Predictivo de Biomarcadores</h4>

      {/* Controls Section */}
      <div className="prediction-controls card mb-3"> {/* Wrap controls in a card */}
        <div className="controls-grid"> {/* Grid layout for controls */}
          <div className="form-group">
            <label className="form-label" htmlFor="biomarker-select">Biomarcador:</label>
            <select
              id="biomarker-select"
              value={selectedBiomarker}
              onChange={(e) => setSelectedBiomarker(e.target.value)}
              className="form-select"
            >
              {biomarkers.map(b => (
                <option key={b.value} value={b.value}>{b.label}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="days-select">Días de predicción:</label>
            <select
              id="days-select"
              value={predictionDays}
              onChange={(e) => setPredictionDays(parseInt(e.target.value))}
              className="form-select"
            >
              <option value={30}>30 días</option>
              <option value={90}>90 días</option>
              <option value={180}>180 días</option>
            </select>
          </div>

          <button onClick={getPredictions} className="form-button align-self-end"> {/* Align button */}
            Generar Predicción
          </button>
        </div>
      </div>

      {/* Loading/Error Messages */}
      {loading && <p className="loading-message mt-2">Analizando datos y generando predicciones...</p>}
      {error && <p className="error-message mt-2">{error}</p>}

      {/* Results Section */}
      {predictions && (
        <div className="predictions-results-container mt-2">
          {/* Summary Card */}
          <div className="prediction-summary card mb-2">
            <h5 className="mb-1">
              Resumen: {getBiomarkerLabel(selectedBiomarker)}
            </h5>
            <p className="current-value">
              <strong>Valor Actual:</strong> {predictions.valor_actual ?? 'N/A'} {getBiomarkerUnit(selectedBiomarker)}
            </p>
            <p className="trend">
              <strong>Tendencia:</strong> {getTrendEmoji()} {predictions.tendencia?.replace('_', ' ') ?? 'N/A'}
            </p>
            <p className="recommendation">
              <strong>Recomendación:</strong> {predictions.recomendacion ?? 'N/A'}
            </p>
          </div>

          {/* Projections Table Card */}
          <div className="prediction-table-card card">
            <h5 className="mb-1">Valores Proyectados ({predictionDays} días)</h5>
            <table className="data-table"> {/* Add class for styling */}
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Valor ({getBiomarkerUnit(selectedBiomarker)})</th>
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

import React, { useState } from 'react';
import axios from 'axios';

const AIRecommendations = ({ pacienteId }) => {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post('http://localhost:8000/ai/recomendaciones', {
        paciente_id: pacienteId
      });
      
      setRecommendations(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error al obtener recomendaciones:', err);
      setError('No se pudieron generar recomendaciones');
      setLoading(false);
    }
  };

  return (
    <div className="ai-recommendations-section"> {/* Use a specific class for the section */}
      <h4 className="mb-2">Recomendaciones Personalizadas con IA</h4>

      {!recommendations && !loading && (
        <button onClick={getRecommendations} className="form-button"> {/* Use consistent button style */}
          Generar Recomendaciones
        </button>
      )}

      {/* Use consistent loading/error messages */}
      {loading && <p className="loading-message mt-2">Analizando datos y generando recomendaciones...</p>}
      {error && <p className="error-message mt-2">{error}</p>}

      {recommendations && (
        <div className="recommendations-content mt-2">
          <div className="recommendations-list card mb-2"> {/* Wrap list in a card */}
            <h5 className="mb-1">Recomendaciones Sugeridas:</h5>
            <ul>
              {recommendations.recomendaciones?.map((rec, index) => ( // Add safe navigation
                <li key={index} className="recommendation-item mb-1">
                  <strong className="recommendation-type">{rec.tipo}:</strong>
                  <span className="recommendation-desc">{rec.descripcion}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="explanation-section card"> {/* Wrap explanation in a card */}
            <h5 className="mb-1">Análisis Detallado:</h5>
            <p className="explanation-text">{recommendations.explicacion}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIRecommendations;

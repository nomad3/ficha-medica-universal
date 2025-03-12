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
    <div className="ai-recommendations">
      <h3>Recomendaciones Personalizadas con IA</h3>
      
      {!recommendations && !loading && (
        <button onClick={getRecommendations} className="btn-primary">
          Generar Recomendaciones
        </button>
      )}
      
      {loading && <p>Analizando datos y generando recomendaciones...</p>}
      
      {error && <p className="error">{error}</p>}
      
      {recommendations && (
        <div className="recommendations-container">
          <h4>Recomendaciones Sugeridas:</h4>
          <ul>
            {recommendations.recomendaciones.map((rec, index) => (
              <li key={index}>
                <strong>{rec.tipo}:</strong> {rec.descripcion}
              </li>
            ))}
          </ul>
          
          <div className="explanation">
            <h4>Análisis Detallado:</h4>
            <p>{recommendations.explicacion}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIRecommendations; 
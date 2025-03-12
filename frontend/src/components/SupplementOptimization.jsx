import React, { useState } from 'react';
import axios from 'axios';

const SupplementOptimization = ({ pacienteId }) => {
  const [supplementPlan, setSupplementPlan] = useState(null);
  const [customObjective, setCustomObjective] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  const getOptimizedPlan = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.post('http://localhost:8000/ai/optimizacion-suplementos', {
        paciente_id: pacienteId,
        objetivo: customObjective || undefined
      });
      
      setSupplementPlan(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Error al obtener plan de suplementación:', err);
      setError('No se pudo generar el plan de suplementación');
      setLoading(false);
    }
  };

  return (
    <div className="supplement-optimization">
      <h3>Plan Personalizado de Suplementación</h3>
      
      {!supplementPlan && !loading && (
        <div className="optimization-form">
          <div className="form-group">
            <label>Objetivo específico (opcional):</label>
            <input 
              type="text" 
              value={customObjective}
              onChange={(e) => setCustomObjective(e.target.value)}
              placeholder="Ej: Mejorar niveles de colesterol"
            />
          </div>
          
          <button onClick={getOptimizedPlan} className="btn-primary">
            Generar Plan Personalizado
          </button>
        </div>
      )}
      
      {loading && <p>Analizando perfil y generando plan óptimo de suplementación...</p>}
      
      {error && <p className="error">{error}</p>}
      
      {supplementPlan && (
        <div className="supplement-plan">
          <h4>Plan de Suplementación: {supplementPlan.objetivo}</h4>
          
          <div className="supplements-list">
            {supplementPlan.suplementos_recomendados.map((suplemento, index) => (
              <div key={index} className="supplement-card">
                <h5>{suplemento.nombre}</h5>
                <div className="supplement-details">
                  <p><strong>Dosis:</strong> {suplemento.dosis}</p>
                  <p><strong>Frecuencia:</strong> {suplemento.frecuencia}</p>
                  <p><strong>Momento:</strong> {suplemento.momento}</p>
                  <p><strong>Duración:</strong> {suplemento.duracion}</p>
                </div>
                <p className="supplement-justification">
                  <strong>Justificación:</strong> {suplemento.justificacion}
                </p>
              </div>
            ))}
          </div>
          
          <div className="plan-considerations">
            <p><strong>Consideraciones:</strong> {supplementPlan.consideraciones}</p>
            <p><strong>Seguimiento:</strong> {supplementPlan.seguimiento_recomendado}</p>
          </div>
          
          <div className="plan-details-toggle">
            <button 
              onClick={() => setShowDetails(!showDetails)}
              className="btn-secondary"
            >
              {showDetails ? 'Ocultar detalles' : 'Mostrar explicación detallada'}
            </button>
          </div>
          
          {showDetails && (
            <div className="plan-detailed-explanation">
              <h4>Explicación Detallada</h4>
              <p>{supplementPlan.explicacion_detallada}</p>
            </div>
          )}
          
          <div className="plan-actions">
            <button onClick={() => setSupplementPlan(null)} className="btn-secondary">
              Generar nuevo plan
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SupplementOptimization;
      
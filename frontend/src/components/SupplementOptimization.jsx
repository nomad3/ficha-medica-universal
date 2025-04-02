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
    <div className="supplement-optimization-section"> {/* Section container */}
      <h4 className="mb-2">Plan Personalizado de Suplementación</h4>

      {/* Initial Form */}
      {!supplementPlan && !loading && (
        <div className="optimization-form card"> {/* Wrap form in card */}
          <div className="form-group mb-2">
            <label className="form-label" htmlFor="custom-objective">Objetivo específico (opcional):</label>
            <input
              id="custom-objective"
              type="text"
              value={customObjective}
              onChange={(e) => setCustomObjective(e.target.value)}
              placeholder="Ej: Mejorar niveles de colesterol"
              className="form-input"
            />
          </div>

          <button onClick={getOptimizedPlan} className="form-button">
            Generar Plan Personalizado
          </button>
        </div>
      )}

      {/* Loading/Error Messages */}
      {loading && <p className="loading-message mt-2">Analizando perfil y generando plan óptimo de suplementación...</p>}
      {error && <p className="error-message mt-2">{error}</p>}

      {/* Generated Plan Display */}
      {supplementPlan && (
        <div className="supplement-plan-container mt-2">
          <div className="plan-header card mb-2"> {/* Card for header */}
            <h5 className="mb-1">Plan Generado</h5>
            <p><strong>Objetivo:</strong> {supplementPlan.objetivo ?? 'General'}</p>
          </div>

          {/* Recommended Supplements List */}
          <div className="supplements-list-container mb-2">
            <h5 className="mb-1">Suplementos Recomendados:</h5>
            <div className="supplements-grid"> {/* Grid for supplement cards */}
              {supplementPlan.suplementos_recomendados?.map((suplemento, index) => ( // Safe navigation
                <div key={index} className="supplement-card card"> {/* Card for each supplement */}
                  <h6 className="supplement-name mb-1">{suplemento.nombre ?? 'N/A'}</h6>
                  <div className="supplement-details mb-1">
                    <p><strong>Dosis:</strong> {suplemento.dosis ?? 'N/A'}</p>
                    <p><strong>Frecuencia:</strong> {suplemento.frecuencia ?? 'N/A'}</p>
                    <p><strong>Momento:</strong> {suplemento.momento ?? 'N/A'}</p>
                    <p><strong>Duración:</strong> {suplemento.duracion ?? 'N/A'}</p>
                  </div>
                  <p className="supplement-justification">
                    <strong>Justificación:</strong> {suplemento.justificacion ?? 'N/A'}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Considerations Card */}
          <div className="plan-considerations card mb-2">
            <h5 className="mb-1">Consideraciones y Seguimiento</h5>
            <p><strong>Consideraciones:</strong> {supplementPlan.consideraciones ?? 'N/A'}</p>
            <p><strong>Seguimiento:</strong> {supplementPlan.seguimiento_recomendado ?? 'N/A'}</p>
          </div>

          {/* Detailed Explanation (Toggle) */}
          <div className="plan-explanation-toggle mb-2">
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="form-button form-button--secondary" /* Secondary style button */
            >
              {showDetails ? 'Ocultar Explicación' : 'Mostrar Explicación Detallada'}
            </button>
          </div>

          {showDetails && (
            <div className="plan-detailed-explanation card mb-2">
              <h5 className="mb-1">Explicación Detallada</h5>
              <p>{supplementPlan.explicacion_detallada ?? 'No disponible.'}</p>
            </div>
          )}

          {/* Action Button */}
          <div className="plan-actions">
            <button onClick={() => setSupplementPlan(null)} className="form-button form-button--secondary">
              Generar Nuevo Plan
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SupplementOptimization;

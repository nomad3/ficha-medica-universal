import React, { useEffect, useState } from 'react';
import { useIAHealth } from '../hooks/useIAHealth';

const AsesorVirtual = ({ paciente }) => {
  const [recomendaciones, setRecomendaciones] = useState([]);
  const { analizarSalud } = useIAHealth();

  useEffect(() => {
    const cargarRecomendaciones = async () => {
      const resultado = await analizarSalud(paciente.id);
      setRecomendaciones(resultado);
    };
    cargarRecomendaciones();
  }, [paciente]);

  return (
    <div className="asesor-container">
      <h3>Plan de Suplementación Personalizado</h3>
      <div className="alertas">
        {recomendaciones.advertencias?.map((adv, i) => (
          <div key={i} className="alerta peligro">{adv}</div>
        ))}
      </div>
      <div className="recomendaciones-grid">
        {recomendaciones.map((suple, i) => (
          <div key={i} className="suplemento-card">
            <h4>{suple.suplemento}</h4>
            <p>Dosis: {suple.dosis}</p>
            <p>Indicación: {suple.motivo}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AsesorVirtual; 
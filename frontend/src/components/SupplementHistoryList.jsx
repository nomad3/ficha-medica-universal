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
    <div className="supplement-history">
      <h4>Historial de Suplementación</h4>
      <table className="data-table">
        <thead>
          <tr>
            <th>Suplemento</th>
            <th>Dosis</th>
            <th>Fecha Inicio</th>
            <th>Colesterol</th>
            <th>Triglicéridos</th>
            <th>Vitamina D</th>
            <th>Índice Omega-3</th>
            <th>Observaciones</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={index}>
              <td>{item.suplemento}</td>
              <td>{item.dosis}</td>
              <td>{item.fecha_inicio}</td>
              <td>{item.colesterol_total} mg/dL</td>
              <td>{item.trigliceridos} mg/dL</td>
              <td>{item.vitamina_d} ng/mL</td>
              <td>{item.omega3_indice}%</td>
              <td>{item.observaciones}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default SupplementHistoryList; 
import React from 'react';

const SupplementHistoryList = ({ data }) => {
  return (
    <div>
      <h4>Historial de Suplementación</h4>
      <table>
        <thead>
          <tr>
            <th>Suplemento</th>
            <th>Dosis</th>
            <th>Fecha Inicio</th>
            <th>Niveles</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={index}>
              <td>{item.suplemento}</td>
              <td>{item.dosis}</td>
              <td>{item.fecha_inicio}</td>
              <td>
                Ω3: {item.omega3_indice}% | 
                VitD: {item.vitamina_d}ng/mL
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default SupplementHistoryList; 
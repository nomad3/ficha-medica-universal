import React, { useState } from 'react';
import axios from 'axios';

const SupplementHistoryForm = ({ pacienteId }) => {
  const [formData, setFormData] = useState({
    suplemento: 'Omega3',
    dosis: '1000mg',
    fecha_inicio: new Date().toISOString().split('T')[0],
    duracion: '3 meses',
    colesterol_total: 0,
    trigliceridos: 0,
    vitamina_d: 0,
    omega3_indice: 0,
    observaciones: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`http://localhost:8000/historial/${pacienteId}`, formData);
      alert('Registro guardado!');
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3>Registro de Suplementación</h3>
      <div>
        <label>Suplemento:</label>
        <select name="suplemento" value={formData.suplemento} onChange={handleChange}>
          <option value="Omega3">Omega 3</option>
          <option value="Multivitaminico">Multivitamínico</option>
          <option value="VitaminaD">Vitamina D</option>
        </select>
      </div>
      <div>
        <label>Dosis:</label>
        <input 
          type="text" 
          name="dosis" 
          value={formData.dosis} 
          onChange={handleChange} 
        />
      </div>
      {/* Añade más campos según necesites */}
      <button type="submit">Guardar</button>
    </form>
  );
};

export default SupplementHistoryForm; 
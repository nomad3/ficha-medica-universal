import React, { useState } from 'react';
import axios from 'axios';

const SupplementHistoryForm = ({ pacienteId }) => {
  const [formData, setFormData] = useState({
    suplemento: 'Omega3',
    dosis: '1000mg',
    fecha_inicio: '',
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

  return (
    <form onSubmit={handleSubmit}>
      <h3>Registro de Suplementación</h3>
      {/* Campos del formulario aquí */}
    </form>
  );
};

export default SupplementHistoryForm; 
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const PacienteList = () => {
  const [pacientes, setPacientes] = useState([]);

  useEffect(() => {
    const fetchPacientes = async () => {
      try {
        const response = await axios.get('http://localhost:8000/pacientes/');
        setPacientes(response.data);
      } catch (error) {
        console.error('Error fetching pacientes:', error);
      }
    };
    fetchPacientes();
  }, []);

  return (
    <div>
      <h2>Listado de Pacientes</h2>
      <ul>
        {pacientes.map(paciente => (
          <li key={paciente.id}>
            <Link to={`/pacientes/${paciente.id}`}>
              {paciente.nombre} {paciente.apellido} - RUT: {paciente.rut}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default PacienteList; 
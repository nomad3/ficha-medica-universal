import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const PacienteList = () => {
  const [pacientes, setPacientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPacientes = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:8000/fhir/Patient');
        setPacientes(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching pacientes:', error);
        setError('Error al cargar los pacientes');
        setLoading(false);
      }
    };
    fetchPacientes();
  }, []);

  if (loading) return <div>Cargando pacientes...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div>
      <h2>Listado de Pacientes</h2>
      <ul>
        {pacientes.map(paciente => {
          const id = paciente.id;
          const rut = paciente.identifier[0]?.value || '';
          const nombre = paciente.name[0]?.given[0] || '';
          const apellido = paciente.name[0]?.family || '';
          
          return (
            <li key={id}>
              <Link to={`/pacientes/${id}/${rut}`}>
                {nombre} {apellido} - RUT: {rut}
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default PacienteList; 
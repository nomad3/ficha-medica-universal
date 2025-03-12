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
        if (Array.isArray(response.data)) {
          setPacientes(response.data);
        } else {
          console.error('Formato de respuesta inesperado:', response.data);
          setError('Formato de datos inesperado');
        }
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
      {pacientes.length === 0 ? (
        <p>No hay pacientes registrados</p>
      ) : (
        <ul>
          {pacientes.map(paciente => {
            const id = paciente.id || '';
            const rut = paciente.identifier && paciente.identifier[0] ? paciente.identifier[0].value : 'Sin RUT';
            const nombre = paciente.name && paciente.name[0] && paciente.name[0].given ? paciente.name[0].given[0] : 'Sin nombre';
            const apellido = paciente.name && paciente.name[0] ? paciente.name[0].family : 'Sin apellido';
            
            return (
              <li key={id}>
                <Link to={`/pacientes/${id}`}>
                  {nombre} {apellido} - RUT: {rut}
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
};

export default PacienteList; 
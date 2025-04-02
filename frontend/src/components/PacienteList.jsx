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
        console.log('Respuesta de la API:', response.data);
        
        // Verificar la estructura de la respuesta
        if (response.data && response.data.entry && Array.isArray(response.data.entry)) {
          // Si la respuesta es un Bundle FHIR
          const pacientesData = response.data.entry.map(entry => entry.resource);
          setPacientes(pacientesData);
        } else if (Array.isArray(response.data)) {
          // Si la respuesta es un array directo
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

  // Use consistent loading/error message styling
  if (loading) return <div className="loading-message">Cargando pacientes...</div>;
  if (error) return <div className="error-message">{error}</div>;

  return (
    <div>
      <h2 className="mb-3">Listado de Pacientes</h2>
      {pacientes.length === 0 ? (
        <p className="no-data-message">No hay pacientes registrados</p> // Style this message too
      ) : (
        <div className="paciente-grid"> {/* Grid container */}
          {pacientes.map(paciente => {
            const id = paciente.id || '';
            const rut = paciente.identifier?.[0]?.value ?? 'Sin RUT';
            // Handle potential missing name parts gracefully
            const nombreCompleto = [
              paciente.name?.[0]?.given?.join(' '),
              paciente.name?.[0]?.family
            ].filter(Boolean).join(' ') || 'Nombre no disponible';

            return (
              <Link to={`/pacientes/${id}`} key={id} className="paciente-card-link"> {/* Link wraps the card */}
                <div className="card paciente-card"> {/* Apply card class */}
                  <h3 className="paciente-card-name">{nombreCompleto}</h3>
                  <p className="paciente-card-rut">RUT: {rut}</p>
                  {/* Add more details if available, e.g., age, gender */}
                  {/* <p>Edad: {calculateAge(paciente.birthDate)}</p> */}
                  {/* <p>Género: {paciente.gender}</p> */}
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default PacienteList;

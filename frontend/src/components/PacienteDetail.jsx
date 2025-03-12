import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import SupplementHistoryForm from './SupplementHistoryForm';
import SupplementHistoryList from './SupplementHistoryList';
import FHIRViewer from './FHIRViewer';

const PacienteDetail = () => {
  const { id } = useParams();
  const [paciente, setPaciente] = useState(null);
  const [historial, setHistorial] = useState([]);

  useEffect(() => {
    const fetchPaciente = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/pacientes/${id}`);
        if(response.data) {
          setPaciente(response.data);
        }
      } catch (error) {
        console.error('Error:', error.response?.data || error.message);
      }
    };
    const fetchHistorial = async () => {
      const response = await axios.get(`http://localhost:8000/pacientes/${id}/historial`);
      setHistorial(response.data);
    };
    if(id) {
      fetchPaciente();
      fetchHistorial();
    }
  }, [id]);

  if (!paciente) return <div>Cargando...</div>;

  return (
    <div>
      <h2>Ficha Clínica: {paciente.nombre} {paciente.apellido}</h2>
      <p>RUT: {paciente.rut}</p>
      <p>Fecha Nacimiento: {paciente.fecha_nacimiento}</p>
      <p>Contacto Emergencia: {paciente.contacto_emergencia}</p>
      <Link to="/">Volver al listado</Link>
      <SupplementHistoryForm pacienteId={id} />
      <SupplementHistoryList data={historial} />
      <FHIRViewer pacienteId={id} rut={paciente.rut} />
    </div>
  );
};

export default PacienteDetail; 
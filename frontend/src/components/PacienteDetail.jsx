import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import SupplementHistoryForm from './SupplementHistoryForm';
import SupplementHistoryList from './SupplementHistoryList';
import FHIRViewer from './FHIRViewer';

const PacienteDetail = () => {
  const { id, rut } = useParams();
  const [paciente, setPaciente] = useState(null);
  const [observaciones, setObservaciones] = useState([]);
  const [medicamentos, setMedicamentos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Obtener datos del paciente en formato FHIR
        const patientResponse = await axios.get(`http://localhost:8000/fhir/Patient/${rut}`);
        setPaciente(patientResponse.data);
        
        // Obtener observaciones en formato FHIR
        const observationsResponse = await axios.get(`http://localhost:8000/fhir/Observation/${id}`);
        setObservaciones(observationsResponse.data);
        
        // Obtener medicamentos/suplementos en formato FHIR
        const medicationsResponse = await axios.get(`http://localhost:8000/fhir/MedicationStatement/${id}`);
        setMedicamentos(medicationsResponse.data);
        
        setLoading(false);
      } catch (err) {
        setError('Error al cargar datos del paciente');
        setLoading(false);
        console.error(err);
      }
    };
    
    if (rut && id) {
      fetchData();
    }
  }, [rut, id]);

  if (loading) return <div>Cargando datos del paciente...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!paciente) return null;

  // Extraer datos del paciente del formato FHIR
  const nombre = paciente.name[0]?.given[0] || '';
  const apellido = paciente.name[0]?.family || '';
  const fechaNacimiento = paciente.birthDate || '';
  const contactoEmergencia = paciente.contact?.[0]?.name?.text || '';

  return (
    <div>
      <h2>Ficha Clínica: {nombre} {apellido}</h2>
      <p>RUT: {paciente.identifier[0]?.value}</p>
      <p>Fecha Nacimiento: {fechaNacimiento}</p>
      <p>Contacto Emergencia: {contactoEmergencia}</p>
      <Link to="/">Volver al listado</Link>
      
      <SupplementHistoryForm pacienteId={id} />
      <SupplementHistoryList data={medicamentos} />
      
      <FHIRViewer paciente={paciente} observaciones={observaciones} medicamentos={medicamentos} />
    </div>
  );
};

export default PacienteDetail; 
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import SupplementHistoryForm from './SupplementHistoryForm';
import SupplementHistoryList from './SupplementHistoryList';
import FHIRViewer from './FHIRViewer';

const PacienteDetail = () => {
  const { id } = useParams();
  const [paciente, setPaciente] = useState(null);
  const [observaciones, setObservaciones] = useState([]);
  const [medicamentos, setMedicamentos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Obtener datos del paciente en formato FHIR por ID
        const patientResponse = await axios.get(`http://localhost:8000/fhir/Patient/${id}`);
        setPaciente(patientResponse.data);
        
        // Obtener observaciones en formato FHIR
        const observationsResponse = await axios.get(`http://localhost:8000/fhir/Observation/${id}`);
        setObservaciones(observationsResponse.data);
        
        // Obtener medicamentos/suplementos en formato FHIR
        const medicationsResponse = await axios.get(`http://localhost:8000/fhir/MedicationStatement/${id}`);
        setMedicamentos(medicationsResponse.data);
        
        setLoading(false);
      } catch (err) {
        console.error('Error al cargar datos del paciente:', err);
        setError('Error al cargar datos del paciente');
        setLoading(false);
      }
    };
    
    if (id) {
      fetchData();
    }
  }, [id]);

  if (loading) return <div>Cargando datos del paciente...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!paciente) return <div>No se encontró el paciente</div>;

  // Extraer datos del paciente del formato FHIR con verificación
  const nombre = paciente.name && paciente.name[0] && paciente.name[0].given ? paciente.name[0].given[0] : 'Sin nombre';
  const apellido = paciente.name && paciente.name[0] ? paciente.name[0].family : 'Sin apellido';
  const fechaNacimiento = paciente.birthDate || 'No disponible';
  const rut = paciente.identifier && paciente.identifier[0] ? paciente.identifier[0].value : 'Sin RUT';
  const contactoEmergencia = paciente.contact && paciente.contact[0] && paciente.contact[0].name ? 
    paciente.contact[0].name.text : 'No disponible';

  return (
    <div>
      <h2>Ficha Clínica: {nombre} {apellido}</h2>
      <p>RUT: {rut}</p>
      <p>Fecha Nacimiento: {fechaNacimiento}</p>
      <p>Contacto Emergencia: {contactoEmergencia}</p>
      <Link to="/">Volver al listado</Link>
      
      <SupplementHistoryForm pacienteId={id} />
      
      {medicamentos && medicamentos.length > 0 ? (
        <SupplementHistoryList data={medicamentos} />
      ) : (
        <p>No hay registros de suplementos</p>
      )}
      
      <FHIRViewer 
        paciente={paciente} 
        observaciones={observaciones || []} 
        medicamentos={medicamentos || []} 
      />
    </div>
  );
};

export default PacienteDetail; 
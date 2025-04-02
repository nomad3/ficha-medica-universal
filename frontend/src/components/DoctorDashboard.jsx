import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import GridLayout from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

// Placeholder layout for Doctor Dashboard
const layout = [
  { i: 'patient-list', x: 0, y: 0, w: 4, h: 8 },
  { i: 'alerts', x: 4, y: 0, w: 8, h: 4 },
  { i: 'analytics-overview', x: 4, y: 4, w: 8, h: 4 },
];

function DoctorDashboard() {
  const [patients, setPatients] = useState([]);
  const [loadingPatients, setLoadingPatients] = useState(true);
  const [errorPatients, setErrorPatients] = useState(null);

  // TODO: Fetch doctor-specific alerts and analytics data

  // Fetch patients on component mount
  useEffect(() => {
    const fetchPatients = async () => {
      setLoadingPatients(true);
      setErrorPatients(null);
      try {
        const response = await axios.get('http://localhost:8000/fhir/Patient');
        // Assuming the response is an array of FHIR Patient resources
        if (Array.isArray(response.data)) {
          setPatients(response.data);
        } else {
           console.error('Unexpected patient data format:', response.data);
           setErrorPatients('Formato de datos de paciente inesperado');
        }
      } catch (err) {
        console.error('Error fetching patients:', err);
        setErrorPatients('Error al cargar pacientes');
      } finally {
        setLoadingPatients(false);
      }
    };
    fetchPatients();
  }, []);

  // Helper to format patient name from FHIR resource
  const formatPatientName = (patient) => {
    const name = patient?.name?.[0];
    if (!name) return 'Nombre no disponible';
    return `${name.given?.join(' ') ?? ''} ${name.family ?? ''}`.trim();
  };

  return (
    // Adjust rowHeight and width as needed, or make width responsive
    <GridLayout className="dashboard-grid-layout" layout={layout} cols={12} rowHeight={50} width={1120} isDraggable={true} isResizable={true}>
      {/* Patient List Widget */}
      <div key="patient-list" className="card dashboard-widget">
        <h5 className="widget-title mb-1">My Patients</h5>
        {loadingPatients && <p>Cargando pacientes...</p>}
        {errorPatients && <p className="error-message">{errorPatients}</p>}
        {!loadingPatients && !errorPatients && (
          <ul className="widget-list">
            {patients.length > 0 ? (
              patients.map(patient => (
                <li key={patient.id}>
                  <Link to={`/pacientes/${patient.id}`}>
                    {formatPatientName(patient)}
                  </Link>
                </li>
              ))
            ) : (
              <li>No patients found.</li>
            )}
          </ul>
        )}
      </div>

      {/* Alerts Widget */}
      <div key="alerts" className="card dashboard-widget">
        <h5 className="widget-title mb-1">Alerts & Notifications</h5>
        {/* Placeholder for alerts */}
        <ul className="widget-list">
          <li>John Doe - High heart rate detected</li>
          <li>Jane Smith - Medication refill needed</li>
        </ul>
      </div>

      {/* Analytics Overview Widget */}
      <div key="analytics-overview" className="card dashboard-widget">
        <h5 className="widget-title mb-1">Analytics Overview</h5>
        {/* Placeholder for analytics charts/widgets */}
        <div className="chart-placeholder mb-1">Chart: Patient Compliance Trend</div>
        <p>New Patients This Month: 5</p>
      </div>
    </GridLayout>
  );
}

export default DoctorDashboard;

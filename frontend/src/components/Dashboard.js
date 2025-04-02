import React from 'react';
import PatientDashboard from './PatientDashboard.jsx'; // Will create this next
import DoctorDashboard from './DoctorDashboard.jsx'; // Will create this next

// Assume userRole is passed as a prop or obtained from context
// For now, let's simulate a role. Replace 'patient' with 'doctor' to test.
const simulatedUserRole = 'patient'; // Change to 'doctor' to see the other dashboard

function Dashboard() {
  // Default to Patient Dashboard if role is unknown or not provided
  const role = simulatedUserRole || 'patient';

  return (
    <div>
      <h1>{role === 'patient' ? 'Patient Dashboard' : 'Doctor Dashboard'}</h1>
      {role === 'patient' ? <PatientDashboard /> : <DoctorDashboard />}
    </div>
  );
}

export default Dashboard;

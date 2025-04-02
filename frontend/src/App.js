import React, { useState, useEffect } from 'react'; // Import hooks
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import PacienteList from './components/PacienteList';
import PacienteDetail from './components/PacienteDetail';
import Navbar from './components/Navbar';
// Import specific dashboards
import PatientDashboard from './components/PatientDashboard.jsx';
import DoctorDashboard from './components/DoctorDashboard.jsx';


function App() {
  // State for dark mode, initializing from localStorage or default to false
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const savedMode = localStorage.getItem('darkMode');
    // Check for system preference if no saved mode
    return savedMode ? JSON.parse(savedMode) : window.matchMedia?.('(prefers-color-scheme: dark)').matches ?? false;
  });

  // Effect to update body class and localStorage when isDarkMode changes
  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add('dark-mode');
    } else {
      document.body.classList.remove('dark-mode');
    }
    localStorage.setItem('darkMode', JSON.stringify(isDarkMode));
  }, [isDarkMode]);

  // Function to toggle dark mode
  const toggleDarkMode = () => {
    setIsDarkMode(prevMode => !prevMode);
  };

  return (
    <BrowserRouter>
      {/* Removed outer div className="App", class is applied to body */}
      <div>
        {/* Pass state and toggle function to Navbar */}
        <Navbar isDarkMode={isDarkMode} toggleDarkMode={toggleDarkMode} />
        <div className="container">
          <Routes>
            <Route path="/" element={<PacienteList />} />
            <Route path="/pacientes/:id" element={<PacienteDetail />} />
            {/* Add specific routes for each dashboard */}
            <Route path="/dashboard/patient" element={<PatientDashboard />} />
            <Route path="/dashboard/doctor" element={<DoctorDashboard />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;

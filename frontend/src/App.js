import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AsesorVirtual from './components/AsesorVirtual';
import PacienteList from './components/PacienteList';
import Navbar from './components/Navbar';
import PacienteDetail from './components/PacienteDetail';

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <div className="container">
        <Routes>
          <Route path="/" element={<PacienteList />} />
          <Route path="/asesor" element={<AsesorVirtual />} />
          <Route path="/pacientes/:id" element={<PacienteDetail />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App; 
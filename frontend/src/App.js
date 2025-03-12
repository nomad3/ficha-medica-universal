import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import PacienteList from './components/PacienteList';
import PacienteDetail from './components/PacienteDetail';
import Navbar from './components/Navbar';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Navbar />
        <div className="container">
          <Routes>
            <Route path="/" element={<PacienteList />} />
            <Route path="/pacientes/:id" element={<PacienteDetail />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App; 
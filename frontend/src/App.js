import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AsesorVirtual from './components/AsesorVirtual';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AsesorVirtual />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App; 
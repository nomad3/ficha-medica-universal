import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav>
      <ul>
        <li><Link to="/">Pacientes</Link></li>
        <li><Link to="/asesor">Asesor Virtual</Link></li>
      </ul>
    </nav>
  );
};

export default Navbar; 
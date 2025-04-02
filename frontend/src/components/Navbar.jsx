import React from 'react';
import { Link } from 'react-router-dom';

// Accept props for dark mode state and toggle function
const Navbar = ({ isDarkMode, toggleDarkMode }) => {
  return (
    <nav>
      <div className="container"> {/* Apply container class */}
        <Link to="/" className="navbar-brand"> {/* Use class for brand */}
          Ficha Universal
        </Link>
        <div className="navbar-right-section"> {/* Wrapper for links and button */}
          <ul className="navbar-links">
            <li><Link to="/">Pacientes</Link></li>
            {/* Add specific dashboard links */}
            <li><Link to="/dashboard/patient">Mi Dashboard</Link></li>
            <li><Link to="/dashboard/doctor">Doctor Dashboard</Link></li>
            {/* <li><Link to="/asesor">Asesor Virtual</Link></li> */}
          </ul>
          {/* Dark Mode Toggle Button */}
          <button onClick={toggleDarkMode} className="theme-toggle-button">
            {isDarkMode ? '☀️ Light' : '🌙 Dark'} {/* Change text/icon based on mode */}
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

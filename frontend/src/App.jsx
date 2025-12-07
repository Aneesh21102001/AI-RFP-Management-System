import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';

import Dashboard from './components/Dashboard';
import CreateRFP from './components/CreateRFP';
import RFPList from './components/RFPList';
import RFPDetail from './components/RFPDetail';
import VendorList from './components/VendorList';
import VendorForm from './components/VendorForm';

function App() {
  return (
    <Router>
      <div className="App">
        {/* Navigation Header */}
        <nav className="navbar">
          <div className="nav-container">
            <Link to="/" className="nav-logo">
              RFP Management System
            </Link>

            <div className="nav-links">
              <Link to="/" className="nav-link">Dashboard</Link>
              <Link to="/rfps" className="nav-link">RFPs</Link>
              <Link to="/rfps/create" className="nav-link">Create RFP</Link>
              <Link to="/vendors" className="nav-link">Vendors</Link>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/rfps" element={<RFPList />} />
            <Route path="/rfps/create" element={<CreateRFP />} />
            <Route path="/rfps/:id" element={<RFPDetail />} />

            {/* Vendor Routes */}
            <Route path="/vendors" element={<VendorList />} />
            <Route path="/vendors/new" element={<VendorForm />} />
            <Route path="/vendors/:id/edit" element={<VendorForm />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

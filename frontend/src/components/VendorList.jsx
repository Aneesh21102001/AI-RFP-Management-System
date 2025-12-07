// ------------------------------------------------------
// Displays a list of all vendors with options to add,
// edit, or delete vendors. Fetches vendor data on load
// and updates list after modifications.
// ------------------------------------------------------

import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { vendorsApi } from '../api/vendors';

const VendorList = () => {
  const [vendors, setVendors] = useState([]);    // Vendor list
  const [loading, setLoading] = useState(true);  // Loading indicator
  const navigate = useNavigate();

  // Load vendor list when component mounts
  useEffect(() => {
    loadVendors();
  }, []);

  // Fetch all vendors from backend
  const loadVendors = async () => {
    try {
      const data = await vendorsApi.getAll();
      setVendors(data);
    } catch (error) {
      console.error('Failed to load vendors:', error);
    } finally {
      setLoading(false);
    }
  };

  // Delete a vendor after confirmation
  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this vendor?')) {
      return;
    }

    try {
      await vendorsApi.delete(id);
      await loadVendors(); // Reload updated list
    } catch (error) {
      console.error('Failed to delete vendor:', error);
      alert('Failed to delete vendor');
    }
  };

  // Show loading state
  if (loading) {
    return <div className="loading">Loading vendors...</div>;
  }

  return (
    <div>
      {/* Header with Add Vendor button */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '2rem',
        }}
      >
        <h1>Vendors</h1>

        {/* Navigate to vendor creation form */}
        <Link to="/vendors/new" className="btn btn-primary">
          Add New Vendor
        </Link>
      </div>

      {/* Vendor table or empty state */}
      {vendors.length === 0 ? (
        <div className="card">
          <p>
            No vendors yet. <Link to="/vendors/new">Add your first vendor</Link>
          </p>
        </div>
      ) : (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Contact Person</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {/* Render each vendor row */}
              {vendors.map((vendor) => (
                <tr key={vendor.id}>
                  <td>{vendor.name}</td>
                  <td>{vendor.email}</td>
                  <td>{vendor.phone || 'N/A'}</td>
                  <td>{vendor.contact_person || 'N/A'}</td>

                  <td>
                    {/* Edit vendor */}
                    <button
                      onClick={() => navigate(`/vendors/${vendor.id}/edit`)}
                      className="btn btn-secondary"
                      style={{
                        padding: '0.5rem 1rem',
                        fontSize: '0.875rem',
                        marginRight: '0.5rem',
                      }}
                    >
                      Edit
                    </button>

                    {/* Delete vendor */}
                    <button
                      onClick={() => handleDelete(vendor.id)}
                      className="btn btn-danger"
                      style={{
                        padding: '0.5rem 1rem',
                        fontSize: '0.875rem',
                      }}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default VendorList;

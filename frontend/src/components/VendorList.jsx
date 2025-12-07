import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { vendorsApi } from '../api/vendors';

const VendorList = () => {
  const [vendors, setVendors] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadVendors();
  }, []);

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

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this vendor?')) {
      return;
    }

    try {
      await vendorsApi.delete(id);
      await loadVendors();
    } catch (error) {
      console.error('Failed to delete vendor:', error);
      alert('Failed to delete vendor');
    }
  };

  if (loading) {
    return <div className="loading">Loading vendors...</div>;
  }

  return (
    <div>
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '2rem',
        }}
      >
        <h1>Vendors</h1>
        <Link to="/vendors/new" className="btn btn-primary">
          Add New Vendor
        </Link>
      </div>

      {/* Vendor Table */}
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
              {vendors.map((vendor) => (
                <tr key={vendor.id}>
                  <td>{vendor.name}</td>
                  <td>{vendor.email}</td>
                  <td>{vendor.phone || 'N/A'}</td>
                  <td>{vendor.contact_person || 'N/A'}</td>

                  <td>
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

// ------------------------------------------------------
// This component is used for both creating and editing vendors.
// If an ID is provided, it loads the vendor and pre-fills the form;
// otherwise, it creates a new vendor.
// ------------------------------------------------------

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { vendorsApi } from '../api/vendors';

const VendorForm = () => {
  const { id } = useParams();        // Extract vendor ID from URL
  const navigate = useNavigate();    // For redirecting after save

  // General UI and API states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Form data for vendor fields
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    contact_person: '',
    notes: '',
  });

  // Load vendor details when editing
  useEffect(() => {
    const loadVendor = async () => {
      try {
        const vendor = await vendorsApi.getById(Number(id));

        // Populate form with vendor details
        setFormData({
          name: vendor.name,
          email: vendor.email,
          phone: vendor.phone || '',
          address: vendor.address || '',
          contact_person: vendor.contact_person || '',
          notes: vendor.notes || '',
        });
      } catch (error) {
        console.error('Failed to load vendor:', error);
        setError('Failed to load vendor');
      }
    };

    if (id && id !== 'new') {
      loadVendor();
    }
  }, [id]);

  // Handle form submission for create/update
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (id && id !== 'new') {
        // Editing existing vendor
        await vendorsApi.update(Number(id), formData);
      } else {
        // Creating new vendor
        await vendorsApi.create(formData);
      }

      // Redirect back to vendor list
      navigate('/vendors');
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to save vendor');
    } finally {
      setLoading(false);
    }
  };

  // Update form state on each keystroke
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div>
      {/* Back navigation */}
      <div style={{ marginBottom: '1rem' }}>
        <button onClick={() => navigate('/vendors')} className="btn btn-secondary">
          ← Back to Vendors
        </button>
      </div>

      {/* Page Title */}
      <h1>{id && id !== 'new' ? 'Edit Vendor' : 'Add New Vendor'}</h1>

      {/* Error banner */}
      {error && <div className="error">{error}</div>}

      <div className="card">
        <form onSubmit={handleSubmit}>

          {/* Name */}
          <div className="form-group">
            <label className="form-label">Name *</label>
            <input
              type="text"
              name="name"
              className="form-input"
              required
              value={formData.name}
              onChange={handleChange}
            />
          </div>

          {/* Email */}
          <div className="form-group">
            <label className="form-label">Email *</label>
            <input
              type="email"
              name="email"
              className="form-input"
              required
              value={formData.email}
              onChange={handleChange}
            />
          </div>

          {/* Phone */}
          <div className="form-group">
            <label className="form-label">Phone</label>
            <input
              type="tel"
              name="phone"
              className="form-input"
              value={formData.phone}
              onChange={handleChange}
            />
          </div>

          {/* Address */}
          <div className="form-group">
            <label className="form-label">Address</label>
            <textarea
              name="address"
              className="form-textarea"
              rows={3}
              value={formData.address}
              onChange={handleChange}
            />
          </div>

          {/* Contact Person */}
          <div className="form-group">
            <label className="form-label">Contact Person</label>
            <input
              type="text"
              name="contact_person"
              className="form-input"
              value={formData.contact_person}
              onChange={handleChange}
            />
          </div>

          {/* Notes */}
          <div className="form-group">
            <label className="form-label">Notes</label>
            <textarea
              name="notes"
              className="form-textarea"
              rows={4}
              value={formData.notes}
              onChange={handleChange}
            />
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading
                ? 'Saving...'
                : id && id !== 'new'
                ? 'Update Vendor'
                : 'Create Vendor'}
            </button>

            <button
              type="button"
              onClick={() => navigate('/vendors')}
              className="btn btn-secondary"
            >
              Cancel
            </button>
          </div>

        </form>
      </div>
    </div>
  );
};

export default VendorForm;

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { rfpsApi } from '../api/rfps';

const RFPList = () => {
  const [rfps, setRfps] = useState([]);
  const [loading, setLoading] = useState(true);

  // Load RFPs when component mounts
  useEffect(() => {
    loadRfps();
  }, []);

  // Fetch RFPs from API
  const loadRfps = async () => {
    try {
      const data = await rfpsApi.getAll(); // API call
      setRfps(data); // Save results
    } catch (error) {
      console.error('Failed to load RFPs:', error);
    } finally {
      setLoading(false); // Stop loading animation
    }
  };

  // Show loading message until data loads
  if (loading) {
    return <div className="loading">Loading RFPs...</div>;
  }

  return (
    <div>
      {/* Header section with page title + button */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '2rem',
        }}
      >
        <h1>RFPs</h1>

        {/* Navigate to Create RFP page */}
        <Link to="/rfps/create" className="btn btn-primary">
          Create New RFP
        </Link>
      </div>

      {/* If no RFPs exist */}
      {rfps.length === 0 ? (
        <div className="card">
          <p>
            No RFPs yet. <Link to="/rfps/create">Create your first RFP</Link>
          </p>
        </div>
      ) : (
        // RFP table section
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Budget</th>
                <th>Delivery</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {/* Loop through RFP list */}
              {rfps.map((rfp) => (
                <tr key={rfp.id}>
                  {/* Title column */}
                  <td>
                    <Link
                      to={`/rfps/${rfp.id}`}
                      style={{ fontWeight: 500 }}
                    >
                      {rfp.title}
                    </Link>
                  </td>

                  {/* Budget column */}
                  <td>
                    {rfp.budget ? `$${rfp.budget.toLocaleString()}` : 'N/A'}
                  </td>

                  {/* Delivery Days column */}
                  <td>
                    {rfp.delivery_days
                      ? `${rfp.delivery_days} days`
                      : 'N/A'}
                  </td>

                  {/* Status badge column */}
                  <td>
                    <span
                      className={`badge badge-${
                        rfp.status === 'sent'
                          ? 'success'
                          : rfp.status === 'closed'
                          ? 'info'
                          : 'warning'
                      }`}
                    >
                      {rfp.status}
                    </span>
                  </td>

                  {/* Created date */}
                  <td>{new Date(rfp.created_at).toLocaleDateString()}</td>

                  {/* View button */}
                  <td>
                    <Link
                      to={`/rfps/${rfp.id}`}
                      className="btn btn-primary"
                      style={{
                        padding: '0.5rem 1rem',
                        fontSize: '0.875rem',
                      }}
                    >
                      View
                    </Link>
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

export default RFPList;

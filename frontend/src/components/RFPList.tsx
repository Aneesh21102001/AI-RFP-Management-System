import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { rfpsApi, RFP } from '../api/rfps';

const RFPList: React.FC = () => {
  const [rfps, setRfps] = useState<RFP[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRfps();
  }, []);

  const loadRfps = async () => {
    try {
      const data = await rfpsApi.getAll();
      setRfps(data);
    } catch (error) {
      console.error('Failed to load RFPs:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading RFPs...</div>;
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>RFPs</h1>
        <Link to="/rfps/create" className="btn btn-primary">Create New RFP</Link>
      </div>

      {rfps.length === 0 ? (
        <div className="card">
          <p>No RFPs yet. <Link to="/rfps/create">Create your first RFP</Link></p>
        </div>
      ) : (
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
              {rfps.map((rfp) => (
                <tr key={rfp.id}>
                  <td>
                    <Link to={`/rfps/${rfp.id}`} style={{ fontWeight: 500 }}>
                      {rfp.title}
                    </Link>
                  </td>
                  <td>
                    {rfp.budget ? `$${rfp.budget.toLocaleString()}` : 'N/A'}
                  </td>
                  <td>
                    {rfp.delivery_days ? `${rfp.delivery_days} days` : 'N/A'}
                  </td>
                  <td>
                    <span className={`badge badge-${rfp.status === 'sent' ? 'success' : rfp.status === 'closed' ? 'info' : 'warning'}`}>
                      {rfp.status}
                    </span>
                  </td>
                  <td>{new Date(rfp.created_at).toLocaleDateString()}</td>
                  <td>
                    <Link to={`/rfps/${rfp.id}`} className="btn btn-primary" style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}>
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

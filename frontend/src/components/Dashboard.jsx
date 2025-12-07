import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { rfpsApi } from '../api/rfps';
import { vendorsApi } from '../api/vendors';
import { proposalsApi } from '../api/proposals';
import './Dashboard.css';

const Dashboard = () => {
  const [rfps, setRfps] = useState([]);
  const [vendors, setVendors] = useState([]);
  const [proposals, setProposals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [rfpsData, vendorsData, proposalsData] = await Promise.all([
        rfpsApi.getAll(),
        vendorsApi.getAll(),
        proposalsApi.getAll(),
      ]);

      setRfps(rfpsData);
      setVendors(vendorsData);
      setProposals(proposalsData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  const recentRfps = rfps.slice(0, 5);
  const recentProposals = proposals.slice(0, 5);

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total RFPs</h3>
          <p className="stat-number">{rfps.length}</p>
        </div>

        <div className="stat-card">
          <h3>Total Vendors</h3>
          <p className="stat-number">{vendors.length}</p>
        </div>

        <div className="stat-card">
          <h3>Total Proposals</h3>
          <p className="stat-number">{proposals.length}</p>
        </div>

        <div className="stat-card">
          <h3>Active RFPs</h3>
          <p className="stat-number">{rfps.filter((r) => r.status === 'sent').length}</p>
        </div>
      </div>

      <div className="dashboard-grid">
        {/* Recent RFPs */}
        <div className="card">
          <div className="card-header">
            <h2>Recent RFPs</h2>
            <Link to="/rfps" className="btn btn-secondary">View All</Link>
          </div>

          {recentRfps.length === 0 ? (
            <p>
              No RFPs yet. <Link to="/rfps/create">Create your first RFP</Link>
            </p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {recentRfps.map((rfp) => (
                  <tr key={rfp.id}>
                    <td>
                      <Link to={`/rfps/${rfp.id}`}>{rfp.title}</Link>
                    </td>

                    <td>
                      <span
                        className={`badge badge-${rfp.status === 'sent' ? 'success' : 'warning'}`}
                      >
                        {rfp.status}
                      </span>
                    </td>

                    <td>{new Date(rfp.created_at).toLocaleDateString()}</td>

                    <td>
                      <Link
                        to={`/rfps/${rfp.id}`}
                        className="btn btn-primary"
                        style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Recent Proposals */}
        <div className="card">
          <div className="card-header">
            <h2>Recent Proposals</h2>
          </div>

          {recentProposals.length === 0 ? (
            <p>No proposals received yet.</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Vendor</th>
                  <th>RFP</th>
                  <th>Price</th>
                  <th>Received</th>
                </tr>
              </thead>

              <tbody>
                {recentProposals.map((proposal) => (
                  <tr key={proposal.id}>
                    <td>{proposal.vendor?.name || 'Unknown'}</td>
                    <td>RFP #{proposal.rfp_id}</td>

                    <td>
                      {proposal.total_price
                        ? `$${proposal.total_price.toLocaleString()}`
                        : 'N/A'}
                    </td>

                    <td>{new Date(proposal.received_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

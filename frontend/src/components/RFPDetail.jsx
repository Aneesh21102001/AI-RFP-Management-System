// ------------------------------------------------------
// This component shows full details of a single RFP.
// It loads RFP info, vendors, and proposals, allows sending
// RFPs to vendors, and performs AI-based proposal comparison.
// ------------------------------------------------------

import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { rfpsApi } from '../api/rfps';
import { vendorsApi } from '../api/vendors';
import { proposalsApi } from '../api/proposals';
import { emailApi } from '../api/email';
import './RFPDetail.css';

const RFPDetail = () => {
  const { id } = useParams();        // Extract RFP ID from URL
  const navigate = useNavigate();    // For navigation actions

  // RFP-related state
  const [rfp, setRfp] = useState(null);
  const [vendors, setVendors] = useState([]);
  const [proposals, setProposals] = useState([]);

  // AI comparison result
  const [comparison, setComparison] = useState(null);
  const [showComparison, setShowComparison] = useState(false);

  // Vendor selection for sending RFP
  const [selectedVendors, setSelectedVendors] = useState([]);

  // UI states
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [loadingComparison, setLoadingComparison] = useState(false);

  // Error/success notifications
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Load data when component mounts or when ID changes
  useEffect(() => {
    if (id) loadData();
  }, [id, loadData]);

  // Wrapped in useCallback to avoid infinite loops in useEffect
  const loadData = useCallback(async () => {
    try {
      // Fetch RFP, vendors, and proposals simultaneously
      const [rfpData, vendorsData, proposalsData] = await Promise.all([
        rfpsApi.getById(Number(id)),
        vendorsApi.getAll(),
        proposalsApi.getAll(Number(id)),
      ]);

      // Update state
      setRfp(rfpData);
      setVendors(vendorsData);
      setProposals(proposalsData);
    } catch (error) {
      console.error('Failed to load data:', error);
      setError('Failed to load RFP details');
    } finally {
      setLoading(false);
    }
  }, [id]);

  // ------------------------------------------------------
  // Sending RFPs to selected vendors
  // ------------------------------------------------------
  const handleSendRFP = async () => {
    if (selectedVendors.length === 0) {
      setError('Please select at least one vendor');
      return;
    }

    setSending(true);
    setError(null);
    setSuccess(null);

    try {
      // Call backend email API
      await emailApi.sendRFP({
        rfp_id: Number(id),
        vendor_ids: selectedVendors,
      });

      setSuccess(`RFP sent successfully to ${selectedVendors.length} vendor(s)`);
      setSelectedVendors([]);  // Reset selection
      await loadData();        // Refresh RFP status after sending
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to send RFP');
    } finally {
      setSending(false);
    }
  };

  // ------------------------------------------------------
  // AI comparison handler
  // ------------------------------------------------------
  const handleCompare = async () => {
    if (proposals.length < 2) {
      setError('Need at least 2 proposals to compare');
      return;
    }

    setLoadingComparison(true);
    setError(null);

    try {
      // Request AI-driven comparison from backend
      const result = await proposalsApi.compare(Number(id));
      setComparison(result);
      setShowComparison(true);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to compare proposals');
    } finally {
      setLoadingComparison(false);
    }
  };

  // Handles selection/deselection of vendor checkboxes
  const toggleVendorSelection = (vendorId) => {
    setSelectedVendors((prev) =>
      prev.includes(vendorId)
        ? prev.filter((id) => id !== vendorId)
        : [...prev, vendorId]
    );
  };

  // Loading states
  if (loading) return <div className="loading">Loading RFP details...</div>;
  if (!rfp) return <div className="error">RFP not found</div>;

  return (
    <div className="rfp-detail">

      {/* Back navigation */}
      <div style={{ marginBottom: '1rem' }}>
        <button onClick={() => navigate('/rfps')} className="btn btn-secondary">
          ← Back to RFPs
        </button>
      </div>

      <h1>{rfp.title}</h1>

      {/* Notification banners */}
      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      {/* ------------------------------------------------------
          RFP MAIN DETAILS SECTION
      ------------------------------------------------------ */}
      <div className="rfp-detail-grid">
        <div className="card">
          <h2>Details</h2>

          <div className="detail-item">
            <strong>Description:</strong>
            <p>{rfp.description || 'No description provided'}</p>
          </div>

          {rfp.budget && (
            <div className="detail-item">
              <strong>Budget:</strong>
              <p>${rfp.budget.toLocaleString()}</p>
            </div>
          )}

          {rfp.delivery_days && (
            <div className="detail-item">
              <strong>Delivery Required:</strong>
              <p>{rfp.delivery_days} days</p>
            </div>
          )}

          {rfp.payment_terms && (
            <div className="detail-item">
              <strong>Payment Terms:</strong>
              <p>{rfp.payment_terms}</p>
            </div>
          )}

          {rfp.warranty_required && (
            <div className="detail-item">
              <strong>Warranty Required:</strong>
              <p>{rfp.warranty_required}</p>
            </div>
          )}

          <div className="detail-item">
            <strong>Status:</strong>
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
          </div>
        </div>

        {/* ITEMS TABLE */}
        {rfp.items && rfp.items.length > 0 && (
          <div className="card">
            <h2>Items</h2>
            <table className="table">
              <thead>
                <tr>
                  <th>Item</th>
                  <th>Quantity</th>
                  <th>Specifications</th>
                </tr>
              </thead>

              <tbody>
                {rfp.items.map((item, idx) => (
                  <tr key={idx}>
                    <td>{item.name || 'N/A'}</td>
                    <td>{item.quantity || 'N/A'}</td>
                    <td>
                      {item.specifications
                        ? Object.entries(item.specifications)
                            .map(([k, v]) => `${k}: ${v}`)
                            .join(', ')
                        : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* ADDITIONAL REQUIREMENTS */}
        {rfp.requirements && rfp.requirements.length > 0 && (
          <div className="card">
            <h2>Additional Requirements</h2>
            <ul>
              {rfp.requirements.map((req, idx) => (
                <li key={idx}>{req}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* ------------------------------------------------------
          SEND RFP SECTION (Only when in "draft" state)
      ------------------------------------------------------ */}
      {rfp.status === 'draft' && (
        <div className="card">
          <h2>Send RFP to Vendors</h2>

          {/* No vendors available */}
          {vendors.length === 0 ? (
            <p>No vendors available. <a href="/vendors">Add vendors</a> first.</p>
          ) : (
            <>
              {/* Vendor list with checkboxes */}
              <div className="vendor-selection">
                {vendors.map((vendor) => (
                  <label key={vendor.id} className="vendor-checkbox">
                    <input
                      type="checkbox"
                      checked={selectedVendors.includes(vendor.id)}
                      onChange={() => toggleVendorSelection(vendor.id)}
                    />
                    <span>
                      {vendor.name} ({vendor.email})
                    </span>
                  </label>
                ))}
              </div>

              {/* Send button */}
              <button
                onClick={handleSendRFP}
                className="btn btn-success"
                disabled={sending || selectedVendors.length === 0}
              >
                {sending
                  ? 'Sending...'
                  : `Send RFP to ${selectedVendors.length} Vendor(s)`}
              </button>
            </>
          )}
        </div>
      )}

      {/* ------------------------------------------------------
          PROPOSALS SECTION
      ------------------------------------------------------ */}
      {proposals.length > 0 && (
        <div className="card">

          {/* Header with compare button */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '1rem',
            }}
          >
            <h2>Proposals ({proposals.length})</h2>

            {proposals.length >= 2 && (
              <button
                onClick={handleCompare}
                className="btn btn-primary"
                disabled={loadingComparison}
              >
                {loadingComparison ? 'Comparing...' : 'Compare & Get Recommendation'}
              </button>
            )}
          </div>

          {/* AI COMPARISON RESULTS */}
          {showComparison && comparison && (
            <div className="comparison-section">
              <h3>AI Recommendation</h3>

              <div className="recommendation-card">
                <h4>
                  Recommended: {comparison.recommendation.recommended_vendor}
                </h4>
                <p>
                  <strong>Reason:</strong> {comparison.recommendation.reason}
                </p>
                <p>
                  <strong>Summary:</strong> {comparison.recommendation.summary}
                </p>
              </div>

              {/* DETAILED COMPARISON TABLE */}
              <h3>Detailed Comparison</h3>
              <table className="table">
                <thead>
                  <tr>
                    <th>Vendor</th>
                    <th>Score</th>
                    <th>Price Rank</th>
                    <th>Delivery Rank</th>
                    <th>Strengths</th>
                    <th>Weaknesses</th>
                  </tr>
                </thead>

                <tbody>
                  {comparison.comparison.map((comp, idx) => (
                    <tr key={idx}>
                      <td>{comp.vendor_name}</td>
                      <td>
                        <span className="score-badge">
                          {comp.score.toFixed(1)}
                        </span>
                      </td>
                      <td>#{comp.price_rank}</td>
                      <td>#{comp.delivery_rank}</td>
                      <td>
                        <ul className="strengths-list">
                          {comp.strengths.map((s, i) => (
                            <li key={i}>{s}</li>
                          ))}
                        </ul>
                      </td>
                      <td>
                        <ul className="weaknesses-list">
                          {comp.weaknesses.map((w, i) => (
                            <li key={i}>{w}</li>
                          ))}
                        </ul>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* PROPOSAL LIST TABLE */}
          <table className="table">
            <thead>
              <tr>
                <th>Vendor</th>
                <th>Total Price</th>
                <th>Delivery</th>
                <th>Payment Terms</th>
                <th>Warranty</th>
                <th>Completeness</th>
                <th>Received</th>
              </tr>
            </thead>

            <tbody>
              {proposals.map((proposal) => (
                <tr key={proposal.id}>
                  <td>{proposal.vendor?.name || 'Unknown'}</td>

                  <td>
                    {proposal.total_price
                      ? `$${proposal.total_price.toLocaleString()}`
                      : 'N/A'}
                  </td>

                  <td>
                    {proposal.delivery_days
                      ? `${proposal.delivery_days} days`
                      : 'N/A'}
                  </td>

                  <td>{proposal.payment_terms || 'N/A'}</td>
                  <td>{proposal.warranty || 'N/A'}</td>

                  <td>
                    {proposal.completeness_score !== null &&
                    proposal.completeness_score !== undefined
                      ? `${(proposal.completeness_score * 100).toFixed(0)}%`
                      : 'N/A'}
                  </td>

                  <td>
                    {new Date(proposal.received_at).toLocaleDateString()}
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

export default RFPDetail;

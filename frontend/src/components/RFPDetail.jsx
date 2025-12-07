import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { rfpsApi } from '../api/rfps';
import { vendorsApi } from '../api/vendors';
import { proposalsApi } from '../api/proposals';
import { emailApi } from '../api/email';
import './RFPDetail.css';

const RFPDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [rfp, setRfp] = useState(null);
  const [vendors, setVendors] = useState([]);
  const [proposals, setProposals] = useState([]);
  const [comparison, setComparison] = useState(null);
  const [selectedVendors, setSelectedVendors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showComparison, setShowComparison] = useState(false);
  const [loadingComparison, setLoadingComparison] = useState(false);

  useEffect(() => {
    if (id) loadData();
  }, [id, loadData]);

  const loadData = useCallback(async () => {
    try {
      const [rfpData, vendorsData, proposalsData] = await Promise.all([
        rfpsApi.getById(Number(id)),
        vendorsApi.getAll(),
        proposalsApi.getAll(Number(id)),
      ]);

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

  const handleSendRFP = async () => {
    if (selectedVendors.length === 0) {
      setError('Please select at least one vendor');
      return;
    }

    setSending(true);
    setError(null);
    setSuccess(null);

    try {
      await emailApi.sendRFP({
        rfp_id: Number(id),
        vendor_ids: selectedVendors,
      });

      setSuccess(`RFP sent successfully to ${selectedVendors.length} vendor(s)`);
      setSelectedVendors([]);
      await loadData();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to send RFP');
    } finally {
      setSending(false);
    }
  };

  const handleCompare = async () => {
    if (proposals.length < 2) {
      setError('Need at least 2 proposals to compare');
      return;
    }

    setLoadingComparison(true);
    setError(null);

    try {
      const result = await proposalsApi.compare(Number(id));
      setComparison(result);
      setShowComparison(true);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to compare proposals');
    } finally {
      setLoadingComparison(false);
    }
  };

  const toggleVendorSelection = (vendorId) => {
    setSelectedVendors((prev) =>
      prev.includes(vendorId)
        ? prev.filter((id) => id !== vendorId)
        : [...prev, vendorId]
    );
  };

  if (loading) return <div className="loading">Loading RFP details...</div>;
  if (!rfp) return <div className="error">RFP not found</div>;

  return (
    <div className="rfp-detail">
      <div style={{ marginBottom: '1rem' }}>
        <button onClick={() => navigate('/rfps')} className="btn btn-secondary">
          ← Back to RFPs
        </button>
      </div>

      <h1>{rfp.title}</h1>

      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      {/* RFP Details */}
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

        {/* Items */}
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

        {/* Requirements */}
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

      {/* Send RFP to Vendors */}
      {rfp.status === 'draft' && (
        <div className="card">
          <h2>Send RFP to Vendors</h2>

          {vendors.length === 0 ? (
            <p>No vendors available. <a href="/vendors">Add vendors</a> first.</p>
          ) : (
            <>
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

      {/* Proposals */}
      {proposals.length > 0 && (
        <div className="card">
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

          {/* Comparison Section */}
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

          {/* Proposal List */}
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

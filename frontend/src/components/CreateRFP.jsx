import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { rfpsApi } from '../api/rfps';
import './CreateRFP.css';

const CreateRFP = () => {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [messages, setMessages] = useState([]);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;

    const userMessage = text.trim();
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setText('');
    setLoading(true);
    setError(null);

    try {
      const rfp = await rfpsApi.createFromText(userMessage);

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `I've created an RFP for you:\n\nTitle: ${rfp.title}\n${
            rfp.description ? `Description: ${rfp.description}\n` : ''
          }${rfp.budget ? `Budget: $${rfp.budget.toLocaleString()}\n` : ''}${
            rfp.delivery_days ? `Delivery: ${rfp.delivery_days} days\n` : ''
          }${
            rfp.items && rfp.items.length > 0
              ? `Items: ${rfp.items.length} item(s)\n`
              : ''
          }\nWould you like to review and send it to vendors?`
        }
      ]);

      // Auto-navigate after a short delay
      setTimeout(() => {
        navigate(`/rfps/${rfp.id}`);
      }, 2000);
    } catch (err) {
      setError(
        err?.response?.data?.detail || 'Failed to create RFP. Please try again.'
      );

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content:
            'I encountered an error processing your request. Please try rephrasing or providing more details.'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-rfp">
      <h1>Create RFP</h1>
      <p className="subtitle">
        Describe what you need to procure in natural language, and I'll create a
        structured RFP for you.
      </p>

      {error && <div className="error">{error}</div>}

      <div className="chat-container">
        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="chat-message assistant">
              <p>
                Hello! I'm here to help you create an RFP. Just describe what
                you need to procure, including:
              </p>
              <ul>
                <li>What items or services you need</li>
                <li>Quantities and specifications</li>
                <li>Budget (if known)</li>
                <li>Delivery timeline</li>
                <li>Payment terms</li>
                <li>Any other requirements</li>
              </ul>
              <p>
                For example: "I need to procure laptops and monitors for our new
                office. Budget is $50,000 total. Need delivery within 30 days.
                We need 20 laptops with 16GB RAM and 15 monitors 27-inch.
                Payment terms should be net 30, and we need at least 1 year
                warranty."
              </p>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-message ${msg.role}`}>
              <p style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</p>
            </div>
          ))}

          {loading && (
            <div className="chat-message assistant">
              <p>Processing your request...</p>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="chat-input-container">
          <input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Describe what you need to procure..."
            className="chat-input"
            disabled={loading}
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !text.trim()}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default CreateRFP;

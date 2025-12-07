// ------------------------------------------------------
// This component allows users to create an RFP using natural language.
// It communicates with the backend AI endpoint, shows a chat-style UI,
// and redirects users to the generated RFP page.
// ------------------------------------------------------

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { rfpsApi } from '../api/rfps';
import './CreateRFP.css';

const CreateRFP = () => {
  // State for user's text input
  const [text, setText] = useState('');

  // Loading spinner state during API call
  const [loading, setLoading] = useState(false);

  // Holds any error returned by API
  const [error, setError] = useState(null);

  // Holds chat message history (user + assistant)
  const [messages, setMessages] = useState([]);

  const navigate = useNavigate();

  // Handles sending natural-language text to the backend AI parser
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) return; // Ignore empty submissions

    const userMessage = text.trim();

    // Add user's message to chat
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setText('');
    setLoading(true);
    setError(null);

    try {
      // Call backend to generate structured RFP using AI
      const rfp = await rfpsApi.createFromText(userMessage);

      // Add AI assistant message showing extracted RFP summary
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

      // Auto-redirect user to the detailed RFP page after a short delay
      setTimeout(() => {
        navigate(`/rfps/${rfp.id}`);
      }, 2000);

    } catch (err) {
      // Extract error message if available
      setError(
        err?.response?.data?.detail || 'Failed to create RFP. Please try again.'
      );

      // Add assistant error message to chat
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

      {/* Show API errors */}
      {error && <div className="error">{error}</div>}

      <div className="chat-container">

        {/* Chat History Box */}
        <div className="chat-messages">

          {/* Initial assistant message when chat is empty */}
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

          {/* Display each chat message */}
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-message ${msg.role}`}>
              <p style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</p>
            </div>
          ))}

          {/* Show loading message during API call */}
          {loading && (
            <div className="chat-message assistant">
              <p>Processing your request...</p>
            </div>
          )}
        </div>

        {/* User input form */}
        <form onSubmit={handleSubmit} className="chat-input-container">
          <input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Describe what you need to procure..."
            className="chat-input"
            disabled={loading}            // Disable when API is working
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !text.trim()}  // Disable when empty or loading
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default CreateRFP;

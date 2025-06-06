import React, { useState } from 'react';

function EmailDraft({ email, onRegenerate, loading }) {
  const [feedback, setFeedback] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleRegenerateSubmit = (e) => {
    e.preventDefault();
    if (feedback.trim()) {
      onRegenerate(feedback);
      setFeedback('');
      setShowFeedback(false);
    }
  };

  const copyToClipboard = () => {
    const emailText = `To: ${email.to.join(', ')}
${email.cc && email.cc.length > 0 ? `CC: ${email.cc.join(', ')}\n` : ''}Subject: ${email.subject}

${email.body}`;
    
    navigator.clipboard.writeText(emailText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const sendTestEmail = () => {
    // This would integrate with an email service in production
    alert('Email functionality would be integrated with your email service provider.');
  };

  if (!email) {
    return <div className="loading">Loading email draft...</div>;
  }

  return (
    <div className="email-draft">
      <div className="email-header">
        <h2>Email Draft</h2>
        <div className="email-actions">
          <button 
            onClick={copyToClipboard} 
            className="btn btn-secondary"
          >
            {copied ? 'Copied!' : 'Copy to Clipboard'}
          </button>
          <button 
            onClick={sendTestEmail} 
            className="btn btn-secondary"
          >
            Send Test Email
          </button>
          <button 
            onClick={() => setShowFeedback(!showFeedback)} 
            className="btn btn-secondary"
            disabled={loading}
          >
            {showFeedback ? 'Cancel' : 'Regenerate with Feedback'}
          </button>
        </div>
      </div>

      {showFeedback && (
        <form onSubmit={handleRegenerateSubmit} className="feedback-form">
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Provide feedback on what should be changed or improved..."
            rows={3}
            className="feedback-input"
            disabled={loading}
          />
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={loading || !feedback.trim()}
          >
            {loading ? 'Regenerating...' : 'Apply Feedback'}
          </button>
        </form>
      )}

      <div className="email-content">
        <div className={`email-priority priority-${email.priority}`}>
          Priority: {email.priority.toUpperCase()}
        </div>

        <div className="email-field">
          <label>To:</label>
          <div className="recipient-list">
            {email.to.map((recipient, index) => (
              <span key={index} className="recipient">{recipient}</span>
            ))}
          </div>
        </div>

        {email.cc && email.cc.length > 0 && (
          <div className="email-field">
            <label>CC:</label>
            <div className="recipient-list">
              {email.cc.map((recipient, index) => (
                <span key={index} className="recipient">{recipient}</span>
              ))}
            </div>
          </div>
        )}

        <div className="email-field">
          <label>Subject:</label>
          <div className="email-subject">{email.subject}</div>
        </div>

        <div className="email-field">
          <label>Body:</label>
          <div className="email-body">
            <pre>{email.body}</pre>
          </div>
        </div>

        {email.attachments && email.attachments.length > 0 && (
          <div className="email-field">
            <label>Attachments:</label>
            <div className="attachment-list">
              {email.attachments.map((attachment, index) => (
                <span key={index} className="attachment">
                  📎 {attachment}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="email-preview-note">
        <p>
          <strong>Note:</strong> This is a preview of the email that will be sent to the relevant parties.
          In a production environment, this would integrate with your email service provider.
        </p>
      </div>
    </div>
  );
}

export default EmailDraft;

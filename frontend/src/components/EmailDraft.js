import React, { useState } from 'react';

function EmailDraft({ email, loading }) {
  const [copied, setCopied] = useState(false);

  // Normalize email data to ensure arrays are arrays
  const normalizeEmailData = (emailData) => {
    if (!emailData) return null;
    
    return {
      ...emailData,
      to: Array.isArray(emailData.to) ? emailData.to : 
          typeof emailData.to === 'string' ? [emailData.to] : [],
      cc: Array.isArray(emailData.cc) ? emailData.cc : 
          typeof emailData.cc === 'string' ? [emailData.cc] : 
          emailData.cc ? [] : [],
      attachments: Array.isArray(emailData.attachments) ? emailData.attachments : 
                   typeof emailData.attachments === 'string' ? [emailData.attachments] : []
    };
  };

  const normalizedEmail = normalizeEmailData(email);


  const copyToClipboard = () => {
    const emailText = `To: ${normalizedEmail.to.join(', ')}
${normalizedEmail.cc && normalizedEmail.cc.length > 0 ? `CC: ${normalizedEmail.cc.join(', ')}\n` : ''}Subject: ${normalizedEmail.subject}

${normalizedEmail.body}`;
    
    navigator.clipboard.writeText(emailText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const sendTestEmail = () => {
    // This would integrate with an email service in production
    alert('Email functionality would be integrated with your email service provider.');
  };

  if (!normalizedEmail) {
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
        </div>
      </div>


      <div className="email-content">
        <div className={`email-priority priority-${normalizedEmail.priority || 'medium'}`}>
          Priority: {(normalizedEmail.priority || 'medium').toUpperCase()}
        </div>

        <div className="email-field">
          <label>To:</label>
          <div className="recipient-list">
            {normalizedEmail.to.map((recipient, index) => (
              <span key={index} className="recipient">{recipient}</span>
            ))}
          </div>
        </div>

        {normalizedEmail.cc && normalizedEmail.cc.length > 0 && (
          <div className="email-field">
            <label>CC:</label>
            <div className="recipient-list">
              {normalizedEmail.cc.map((recipient, index) => (
                <span key={index} className="recipient">{recipient}</span>
              ))}
            </div>
          </div>
        )}

        <div className="email-field">
          <label>Subject:</label>
          <div className="email-subject">{normalizedEmail.subject || 'No subject'}</div>
        </div>

        <div className="email-field">
          <label>Body:</label>
          <div className="email-body">
            <pre>{normalizedEmail.body || 'No content'}</pre>
          </div>
        </div>

        {normalizedEmail.attachments && normalizedEmail.attachments.length > 0 && (
          <div className="email-field">
            <label>Attachments:</label>
            <div className="attachment-list">
              {normalizedEmail.attachments.map((attachment, index) => (
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

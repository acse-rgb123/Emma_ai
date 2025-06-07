import React from 'react';

function FallbackNotification({ notification, onClose }) {
  if (!notification?.show) return null;

  const getProviderName = (provider) => {
    const names = {
      'openai': 'GPT-4',
      'claude': 'Claude',
      'gemini': 'Gemini'
    };
    return names[provider] || provider;
  };

  return (
    <div className="fallback-notification">
      <div className="notification-content">
        <div className="notification-icon">⚠️</div>
        <div className="notification-text">
          <strong>Provider Switch Notice</strong>
          <p>
            {getProviderName(notification.original_provider)} was unavailable, 
            so we automatically switched to {getProviderName(notification.fallback_provider)} 
            to complete your analysis.
          </p>
        </div>
        <button 
          className="notification-close"
          onClick={onClose}
          aria-label="Close notification"
        >
          ×
        </button>
      </div>
    </div>
  );
}

export default FallbackNotification;
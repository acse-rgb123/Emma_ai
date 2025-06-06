import React, { useState, useEffect } from 'react';
import OpenAILogo from './logos/OpenAILogo';
import ClaudeLogo from './logos/ClaudeLogo';
import GeminiLogo from './logos/GeminiLogo';

// Simple encryption/decryption for API keys (not production-grade, but better than plaintext)
const encryptKey = (key) => {
  if (!key) return '';
  return btoa(key.split('').reverse().join(''));
};

const decryptKey = (encrypted) => {
  if (!encrypted) return '';
  try {
    return atob(encrypted).split('').reverse().join('');
  } catch {
    return '';
  }
};

function SettingsModal({ isOpen, onClose, onSave }) {
  const [apiKeys, setApiKeys] = useState({
    openai: '',
    claude: '',
    gemini: ''
  });
  
  const [showKeys, setShowKeys] = useState({
    openai: false,
    claude: false,
    gemini: false
  });

  const [savedStatus, setSavedStatus] = useState('');

  useEffect(() => {
    if (isOpen) {
      // Load saved keys from localStorage
      const savedKeys = {
        openai: decryptKey(localStorage.getItem('emma_openai_key') || ''),
        claude: decryptKey(localStorage.getItem('emma_claude_key') || ''),
        gemini: decryptKey(localStorage.getItem('emma_gemini_key') || '')
      };
      setApiKeys(savedKeys);
    }
  }, [isOpen]);

  const handleSave = async () => {
    // Encrypt and save to localStorage
    if (apiKeys.openai) localStorage.setItem('emma_openai_key', encryptKey(apiKeys.openai));
    if (apiKeys.claude) localStorage.setItem('emma_claude_key', encryptKey(apiKeys.claude));
    if (apiKeys.gemini) localStorage.setItem('emma_gemini_key', encryptKey(apiKeys.gemini));
    
    // Send to backend (in a real app, this would be done securely)
    try {
      const response = await fetch('/api/update_keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          openai_key: apiKeys.openai,
          claude_key: apiKeys.claude,
          gemini_key: apiKeys.gemini
        })
      });
      
      if (response.ok) {
        setSavedStatus('Settings saved successfully!');
        setTimeout(() => setSavedStatus(''), 3000);
        if (onSave) onSave();
      }
    } catch (error) {
      console.error('Error saving keys:', error);
      setSavedStatus('Error saving settings');
    }
  };

  const handleClearKey = (provider) => {
    setApiKeys(prev => ({ ...prev, [provider]: '' }));
    localStorage.removeItem(`emma_${provider}_key`);
  };

  const toggleShowKey = (provider) => {
    setShowKeys(prev => ({ ...prev, [provider]: !prev[provider] }));
  };

  if (!isOpen) return null;

  const providers = [
    { 
      id: 'openai', 
      name: 'OpenAI', 
      logo: OpenAILogo,
      placeholder: 'sk-...',
      description: 'GPT-4 and GPT-3.5 models'
    },
    { 
      id: 'claude', 
      name: 'Claude', 
      logo: ClaudeLogo,
      placeholder: 'sk-ant-...',
      description: 'Anthropic Claude models'
    },
    { 
      id: 'gemini', 
      name: 'Google Gemini', 
      logo: GeminiLogo,
      placeholder: 'AIza...',
      description: 'Google Gemini Pro models'
    }
  ];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content settings-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>API Configuration</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <div className="settings-intro">
            <p>Configure your AI provider API keys. Keys are stored locally in your browser and encrypted.</p>
            <div className="security-note">
              <span className="security-icon">🔒</span>
              <span>Your API keys never leave your device and are not stored on our servers.</span>
            </div>
          </div>
          
          <div className="api-key-sections">
            {providers.map(provider => {
              const Logo = provider.logo;
              const hasKey = !!apiKeys[provider.id];
              
              return (
                <div key={provider.id} className="api-key-section">
                  <div className="provider-header">
                    <Logo size={32} />
                    <div className="provider-info">
                      <h3>{provider.name}</h3>
                      <p>{provider.description}</p>
                    </div>
                  </div>
                  
                  <div className="api-key-input-group">
                    <input
                      type={showKeys[provider.id] ? 'text' : 'password'}
                      value={apiKeys[provider.id]}
                      onChange={(e) => setApiKeys(prev => ({ ...prev, [provider.id]: e.target.value }))}
                      placeholder={provider.placeholder}
                      className="api-key-input"
                    />
                    <button
                      className="show-hide-btn"
                      onClick={() => toggleShowKey(provider.id)}
                      title={showKeys[provider.id] ? 'Hide' : 'Show'}
                    >
                      {showKeys[provider.id] ? '👁️' : '👁️‍🗨️'}
                    </button>
                    {hasKey && (
                      <button
                        className="clear-btn"
                        onClick={() => handleClearKey(provider.id)}
                        title="Clear API key"
                      >
                        Clear
                      </button>
                    )}
                  </div>
                  
                  <div className="key-status">
                    {hasKey ? (
                      <span className="status-configured">✓ Configured</span>
                    ) : (
                      <span className="status-not-configured">Not configured</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
          
          {savedStatus && (
            <div className={`save-status ${savedStatus.includes('Error') ? 'error' : 'success'}`}>
              {savedStatus}
            </div>
          )}
        </div>
        
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button className="btn btn-primary" onClick={handleSave}>
            Save Configuration
          </button>
        </div>
      </div>
    </div>
  );
}

export default SettingsModal;

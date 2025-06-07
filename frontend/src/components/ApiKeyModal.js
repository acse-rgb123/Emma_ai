import React, { useState } from 'react';

function ApiKeyModal({ isOpen, onClose, onSave }) {
  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [saveStatus, setSaveStatus] = useState(null);

  const handleSave = async () => {
    if (!apiKey.trim()) {
      setSaveStatus({ type: 'error', message: 'Please enter an API key' });
      return;
    }

    setSaveStatus({ type: 'loading', message: 'Saving API key...' });
    
    try {
      const result = await onSave(apiKey.trim());
      if (result.success) {
        setSaveStatus({ type: 'success', message: 'API key saved successfully!' });
        setTimeout(() => {
          setSaveStatus(null);
          onClose();
        }, 1500);
      } else {
        setSaveStatus({ type: 'error', message: result.error || 'Failed to save API key' });
      }
    } catch (error) {
      setSaveStatus({ type: 'error', message: 'Error saving API key: ' + error.message });
    }
  };

  const handleTest = async () => {
    if (!apiKey.trim()) {
      setTestResult({ type: 'error', message: 'Please enter an API key to test' });
      return;
    }

    if (!apiKey.trim().startsWith('sk-')) {
      setTestResult({ type: 'error', message: 'Invalid API key format. OpenAI API keys start with "sk-"' });
      return;
    }

    setTesting(true);
    setTestResult(null);

    try {
      console.log('Testing OpenAI connection...');
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout

      const response = await fetch('/api/test_openai', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ api_key: apiKey.trim() }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('Test result:', result);
      
      if (result.success) {
        setTestResult({ 
          type: 'success', 
          message: `✅ Connection successful! Model: ${result.model || 'gpt-4o-mini'}${result.usage ? ` (${result.usage} tokens used)` : ''}` 
        });
      } else {
        setTestResult({ 
          type: 'error', 
          message: `❌ ${result.error || 'Unknown error'}` 
        });
      }
    } catch (error) {
      console.error('Test error:', error);
      
      if (error.name === 'AbortError') {
        setTestResult({ 
          type: 'error', 
          message: '❌ Connection timeout. Please check your internet connection and try again.' 
        });
      } else if (error.message.includes('Failed to fetch')) {
        setTestResult({ 
          type: 'error', 
          message: '❌ Cannot connect to server. Please ensure the backend is running.' 
        });
      } else {
        setTestResult({ 
          type: 'error', 
          message: `❌ Connection failed: ${error.message}` 
        });
      }
    } finally {
      setTesting(false);
    }
  };

  const handleClose = () => {
    setApiKey('');
    setShowKey(false);
    setTestResult(null);
    setSaveStatus(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content api-key-modal">
        <div className="modal-header">
          <h2>Configure OpenAI API Key</h2>
          <button onClick={handleClose} className="modal-close">×</button>
        </div>
        
        <div className="modal-body">
          <div className="api-key-intro">
            <p>Emma requires an OpenAI API key to analyze transcripts and generate reports. Your API key is stored securely and only used for analysis.</p>
            
            <div className="security-note">
              <span className="security-icon">🔒</span>
              <span>Your API key is stored locally and never shared with third parties.</span>
            </div>
          </div>

          <div className="api-key-section">
            <div className="provider-header">
              <div className="provider-info">
                <h3>OpenAI API Key</h3>
                <p>Get your API key from <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer">OpenAI Platform</a></p>
              </div>
            </div>

            <div className="api-key-input-group">
              <input
                type={showKey ? 'text' : 'password'}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="sk-..."
                className="api-key-input"
                onKeyPress={(e) => e.key === 'Enter' && handleTest()}
              />
              <button
                type="button"
                onClick={() => setShowKey(!showKey)}
                className="show-hide-btn"
              >
                {showKey ? '👁️' : '👁️‍🗨️'}
              </button>
              <button
                type="button"
                onClick={() => setApiKey('')}
                className="clear-btn"
                disabled={!apiKey}
              >
                Clear
              </button>
            </div>

            <div className="api-actions">
              <button
                onClick={handleTest}
                disabled={testing || !apiKey.trim()}
                className="btn btn-secondary test-btn"
              >
                {testing ? 'Testing...' : 'Test Connection'}
              </button>
            </div>

            {testResult && (
              <div className={`test-result ${testResult.type}`}>
                {testResult.message}
              </div>
            )}

            {saveStatus && (
              <div className={`save-status ${saveStatus.type}`}>
                {saveStatus.message}
              </div>
            )}
          </div>
        </div>

        <div className="modal-footer">
          <button onClick={handleClose} className="btn btn-secondary">
            Cancel
          </button>
          <button 
            onClick={handleSave} 
            className="btn btn-primary"
            disabled={!apiKey.trim() || saveStatus?.type === 'loading'}
          >
            {saveStatus?.type === 'loading' ? 'Saving...' : 'Save & Continue'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ApiKeyModal;
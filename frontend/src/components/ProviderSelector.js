import React, { useState, useEffect } from 'react';
import { switchProvider, getProviderStatus } from '../services/api';
import OpenAILogo from './logos/OpenAILogo';
import ClaudeLogo from './logos/ClaudeLogo';
import GeminiLogo from './logos/GeminiLogo';
import SettingsModal from './SettingsModal';

function ProviderSelector({ onProviderChange }) {
  const [currentProvider, setCurrentProvider] = useState('');
  const [availableProviders, setAvailableProviders] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    loadProviderStatus();
  }, []);

  const loadProviderStatus = async () => {
    try {
      const status = await getProviderStatus();
      setCurrentProvider(status.active_provider);
      setAvailableProviders(status.available_providers);
    } catch (err) {
      console.error('Failed to load provider status:', err);
    }
  };

  const handleProviderSwitch = async (provider) => {
    if (provider === currentProvider) {
      setIsOpen(false);
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const result = await switchProvider(provider);
      setCurrentProvider(result.active_provider);
      setIsOpen(false);
      
      if (onProviderChange) {
        onProviderChange(result.active_provider);
      }
      
      // Reload provider status
      await loadProviderStatus();
    } catch (err) {
      setError(err.message || 'Failed to switch provider');
    } finally {
      setLoading(false);
    }
  };

  const providerInfo = {
    openai: { name: 'GPT-4', logo: OpenAILogo, color: '#000000' },
    claude: { name: 'Claude', logo: ClaudeLogo, color: '#6b5ce7' },
    gemini: { name: 'Gemini', logo: GeminiLogo, color: '#4285f4' }
  };

  const CurrentLogo = providerInfo[currentProvider]?.logo || OpenAILogo;

  return (
    <>
      <div className="provider-selector">
        <button 
          className="provider-toggle"
          onClick={() => setIsOpen(!isOpen)}
          disabled={loading}
        >
          <CurrentLogo size={20} color="white" />
          <span className="provider-name">{providerInfo[currentProvider]?.name || 'AI'}</span>
          <span className="dropdown-arrow">{isOpen ? '▲' : '▼'}</span>
        </button>
        
        {isOpen && (
          <div className="provider-dropdown">
            {Object.entries(providerInfo).map(([key, info]) => {
              const Logo = info.logo;
              return (
                <button
                  key={key}
                  className={`provider-option ${key === currentProvider ? 'active' : ''} ${!availableProviders[key] ? 'disabled' : ''}`}
                  onClick={() => handleProviderSwitch(key)}
                  disabled={!availableProviders[key] || loading}
                  style={{ '--provider-color': info.color }}
                >
                  <Logo size={20} color={key === currentProvider ? info.color : '#666'} />
                  <span className="provider-name">{info.name}</span>
                  {!availableProviders[key] && <span className="not-configured">(Not configured)</span>}
                  {key === currentProvider && <span className="checkmark">✓</span>}
                </button>
              );
            })}
            
            <div className="dropdown-divider"></div>
            
            <button
              className="provider-option settings-option"
              onClick={() => {
                setIsOpen(false);
                setShowSettings(true);
              }}
            >
              <span className="settings-icon">⚙️</span>
              <span className="provider-name">Configure API Keys</span>
            </button>
          </div>
        )}
        
        {error && (
          <div className="provider-error">{error}</div>
        )}
      </div>
      
      <SettingsModal 
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        onSave={() => {
          loadProviderStatus();
          setShowSettings(false);
        }}
      />
    </>
  );
}

export default ProviderSelector;

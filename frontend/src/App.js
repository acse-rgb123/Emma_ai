import React, { useState, useEffect } from 'react';
import './App.css';
import ChatInterface from './components/ChatInterface';
import IncidentReport from './components/IncidentReport';
import EmailDraft from './components/EmailDraft';
import ApiKeyModal from './components/ApiKeyModal';
import { analyzeTranscript, updateAnalysis, checkHealth } from './services/api';

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [activeTab, setActiveTab] = useState('chat');
  const [sessionId] = useState(() => `session-${Date.now()}`);
  const [systemStatus, setSystemStatus] = useState(null);
  const [updateCounter, setUpdateCounter] = useState(0); // Force re-render
  const [updateSuccess, setUpdateSuccess] = useState(null); // Track successful updates
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);

  useEffect(() => {
    // Check system health on load
    checkHealth().then(status => {
      setSystemStatus(status);
      console.log('System status:', status);
      
      // Show API key modal if not configured
      if (!status.ai_configured) {
        setShowApiKeyModal(true);
      }
    }).catch(err => {
      console.error('Health check failed:', err);
      // Show API key modal if health check fails
      setShowApiKeyModal(true);
    });
  }, []);

  const handleTranscriptSubmit = async (transcript) => {
    console.log('Submitting transcript:', transcript.substring(0, 100) + '...');
    setLoading(true);
    setError(null);
    
    try {
      const result = await analyzeTranscript(transcript, sessionId);
      console.log('Analysis result received:', result);
      
      if (!result || !result.incident_report || !result.email_draft) {
        throw new Error('Incomplete analysis result received');
      }
      
      setAnalysisResult(result);
      setActiveTab('summary');
      setError(null); // Clear any previous errors
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.message || 'An error occurred while analyzing the transcript');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateAnalysis = async (newInfo, updateType) => {
    console.log('Updating analysis with:', newInfo);
    setLoading(true);
    setError(null);
    
    try {
      const result = await updateAnalysis(sessionId, newInfo, updateType);
      console.log('Update result:', result);
      
      if (result && result.status === 'success') {
        // Update the analysis result with new data
        setAnalysisResult({
          analysis_summary: result.analysis_summary,
          incident_report: result.incident_report,
          email_draft: result.email_draft,
          policy_violations: result.policy_violations,
          recommendations: result.recommendations
        });
        
        // Force component re-render
        setUpdateCounter(prev => prev + 1);
        
        // Show success message
        setError(null);
        setUpdateSuccess(`${updateType === 'incident_report' ? 'Incident report' : 'Email draft'} updated successfully!`);
      } else {
        throw new Error('Update failed');
      }
    } catch (err) {
      console.error('Update error:', err);
      setError(err.message || 'An error occurred while updating the analysis');
    } finally {
      setLoading(false);
    }
  };


  const handleReportUpdate = (updatedReport) => {
    console.log('Updating report with manual edits');
    setAnalysisResult(prev => ({
      ...prev,
      incident_report: updatedReport
    }));
    setUpdateCounter(prev => prev + 1);
  };

  const handleApiKeySave = async (apiKey) => {
    try {
      const response = await fetch('/api/update_keys', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ openai_key: apiKey })
      });

      const result = await response.json();
      
      if (result.success) {
        // Refresh system status
        const status = await checkHealth();
        setSystemStatus(status);
        return { success: true };
      } else {
        return { success: false, error: result.error };
      }
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'chat':
        return (
          <ChatInterface 
            onSubmit={handleTranscriptSubmit}
            onUpdate={handleUpdateAnalysis}
            loading={loading}
            error={error}
            hasAnalysis={!!analysisResult}
            sessionId={sessionId}
            updateSuccess={updateSuccess}
            onClearSuccess={() => setUpdateSuccess(null)}
            key={`chat-${updateCounter}`}
          />
        );
      
      case 'summary':
        if (!analysisResult) {
          return (
            <div className="empty-state">
              <p>No analysis results yet. Please submit a transcript first.</p>
              <button onClick={() => setActiveTab('chat')} className="btn btn-primary">
                Go to Chat
              </button>
            </div>
          );
        }
        return (
          <div className="summary-container" key={`summary-${updateCounter}`}>
            <h2>Analysis Summary</h2>
            <div className="summary-content">
              <div className="summary-text">
                <p>{analysisResult.analysis_summary || "Analysis completed successfully."}</p>
              </div>
              
              {analysisResult.policy_violations && analysisResult.policy_violations.length > 0 && (
                <div className="violations-section">
                  <h3>Policy Violations Detected</h3>
                  <div className="violations-list">
                    {analysisResult.policy_violations.map((violation, index) => (
                      <div key={index} className={`violation-card ${violation.severity}`}>
                        <div className="violation-header">
                          <strong>{violation.policy_section}</strong>
                          <span className={`severity-badge ${violation.severity}`}>
                            {violation.severity.toUpperCase()}
                          </span>
                        </div>
                        <p className="violation-description">{violation.description}</p>
                        <div className="required-action">
                          <strong>Required Action:</strong> {violation.required_action}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {analysisResult.recommendations && analysisResult.recommendations.length > 0 && (
                <div className="recommendations-section">
                  <h3>Recommendations</h3>
                  <ul className="recommendations-list">
                    {analysisResult.recommendations.map((rec, index) => (
                      <li key={index}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              <div className="summary-actions">
                <button 
                  onClick={() => setActiveTab('report')} 
                  className="btn btn-primary"
                >
                  View Incident Report
                </button>
                <button 
                  onClick={() => setActiveTab('email')} 
                  className="btn btn-secondary"
                >
                  View Email Draft
                </button>
              </div>
            </div>
          </div>
        );
        
      case 'report':
        if (!analysisResult || !analysisResult.incident_report) {
          return (
            <div className="empty-state">
              <p>No analysis results yet. Please submit a transcript first.</p>
              <button onClick={() => setActiveTab('chat')} className="btn btn-primary">
                Go to Chat
              </button>
            </div>
          );
        }
        return (
          <IncidentReport 
            key={`report-${updateCounter}`}
            report={analysisResult.incident_report}
            onUpdate={handleReportUpdate}
            loading={loading}
          />
        );
        
      case 'email':
        if (!analysisResult || !analysisResult.email_draft) {
          return (
            <div className="empty-state">
              <p>No analysis results yet. Please submit a transcript first.</p>
              <button onClick={() => setActiveTab('chat')} className="btn btn-primary">
                Go to Chat
              </button>
            </div>
          );
        }
        return (
          <EmailDraft 
            key={`email-${updateCounter}`}
            email={analysisResult.email_draft}
            loading={loading}
          />
        );
        
      default:
        return null;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <div className="header-info">
            <h1>Emma Incident Response System</h1>
            <p className="subtitle">AI-Enhanced Social Care Incident Analysis</p>
            {systemStatus && (
              <div className="system-status">
                <span className={`status-indicator ${systemStatus.ai_configured ? 'active' : 'inactive'}`}></span>
                <span className="status-text">
                  OpenAI {systemStatus.ai_configured ? 'Connected' : 'API Key Required'}
                </span>
              </div>
            )}
          </div>
          <div className="header-controls">
            <button 
              onClick={() => setShowApiKeyModal(true)}
              className="btn btn-secondary api-key-btn"
            >
              ⚙️ Configure API Key
            </button>
          </div>
        </div>
      </header>
      
      <nav className="main-nav">
        <button 
          className={`nav-tab ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          Chat Input
        </button>
        <button 
          className={`nav-tab ${activeTab === 'summary' ? 'active' : ''} ${!analysisResult ? 'disabled' : ''}`}
          onClick={() => setActiveTab('summary')}
          disabled={!analysisResult}
        >
          Summary
        </button>
        <button 
          className={`nav-tab ${activeTab === 'report' ? 'active' : ''} ${!analysisResult ? 'disabled' : ''}`}
          onClick={() => setActiveTab('report')}
          disabled={!analysisResult}
        >
          Incident Report
        </button>
        <button 
          className={`nav-tab ${activeTab === 'email' ? 'active' : ''} ${!analysisResult ? 'disabled' : ''}`}
          onClick={() => setActiveTab('email')}
          disabled={!analysisResult}
        >
          Email Draft
        </button>
      </nav>
      
      <main className="main-content">
        {error && (
          <div className="error-banner">
            <strong>Error:</strong> {error}
            <button onClick={() => setError(null)} className="error-close">×</button>
          </div>
        )}
        {renderContent()}
      </main>
      
      <footer className="App-footer">
        <p>&copy; 2024 Emma Care Systems. All rights reserved.</p>
        <p className="session-info">Session ID: {sessionId}</p>
      </footer>

      <ApiKeyModal 
        isOpen={showApiKeyModal}
        onClose={() => setShowApiKeyModal(false)}
        onSave={handleApiKeySave}
      />
    </div>
  );
}

export default App;

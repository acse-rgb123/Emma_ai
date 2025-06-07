import React, { useState, useEffect } from 'react';

const SAMPLE_TRANSCRIPT = `Julie Peaterson: "Good morning, Julie Peaterson speaking, how can I help you?"
Greg Jones: "Hi, uh, it's Greg... Greg Jones. I've, uh, I've fallen again."
Julie Peaterson: "Oh no, Greg! Are you alright? Where are you right now?"
Greg Jones: "I'm in the living room, on the floor... I tried getting up, but I just can't seem to manage it this time."
Julie Peaterson: "Okay, Greg, take a deep breath. Let's not rush. Are you hurt? Do you feel any pain or see any blood?"
Greg Jones: "No, no, there's no blood... I don't think anything's broken either. It's just... I don't know. I feel a bit all over the place, to be honest. Can't really remember how I ended up down here."
Julie Peaterson: "Alright, that's good to hear there's no immediate injuries. But you sound a little off. How long have you been on the floor, Greg?"
Greg Jones: "I don't know... maybe 20 minutes? It could be longer. I just—my mind's a bit fuzzy, can't really think straight right now."
Julie Peaterson: "Hmm, okay. You mentioned this has happened before. Has it been happening often?"
Greg Jones: "Yeah, this is the third time... this week. I'm just so... so frustrated, Julie. Every time I think I'm okay, and then... boom, I'm back on the floor."
Julie Peaterson: "Oh Greg, I'm really sorry to hear that. It must be so frustrating for you. Let's get you some help right away, okay? I'll make sure someone gets to you as soon as possible."
Greg Jones: "Thanks, Julie. I just... I don't know what's going on anymore."
Julie Peaterson: "Don't worry, Greg. We'll get this sorted, and we'll talk about what's been happening. It sounds like we need to look at what's going on a bit more closely."
Greg Jones: "Yeah, maybe... I just hate this feeling. I don't want it happening again."
Julie Peaterson: "I completely understand, Greg. You're doing great by calling in. We'll get you back on your feet and figure out how to prevent this from happening again."`;

function ChatInterface({ onSubmit, onUpdate, loading, error, hasAnalysis, sessionId, updateSuccess, onClearSuccess }) {
  const [transcript, setTranscript] = useState('');
  const [updateInfo, setUpdateInfo] = useState('');
  const [updateType, setUpdateType] = useState('incident_report');
  const [showUpdateForm, setShowUpdateForm] = useState(false);
  const [hasShownSuccess, setHasShownSuccess] = useState(false);
  const [currentMessage, setCurrentMessage] = useState('Welcome to the Emma Incident Response System. Please paste or type the call transcript you want to analyze.');
  const [showNewTranscript, setShowNewTranscript] = useState(false);
  const [showUpdateTranscript, setShowUpdateTranscript] = useState(false);
  const [newTranscript, setNewTranscript] = useState('');
  const [updateTranscript, setUpdateTranscript] = useState('');

  useEffect(() => {
    if (hasAnalysis && !hasShownSuccess) {
      setCurrentMessage('Analysis completed successfully! You can view the results in the Summary, Report, and Email tabs. Use the form below to update either the incident report or email draft with additional information.');
      setShowUpdateForm(true);
      setHasShownSuccess(true);
    }
  }, [hasAnalysis, hasShownSuccess]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!transcript.trim()) return;

    console.log('ChatInterface: Submitting transcript of length:', transcript.length);

    // Update status message
    setCurrentMessage('Analyzing transcript against policies...');

    onSubmit(transcript);
  };

  const handleUpdateSubmit = (e) => {
    e.preventDefault();
    if (!updateInfo.trim()) return;

    console.log('ChatInterface: Submitting update:', updateInfo);

    // Update status message
    setCurrentMessage(`Updating ${updateType === 'incident_report' ? 'incident report' : 'email draft'} with new information...`);

    onUpdate(updateInfo, updateType);
    setUpdateInfo('');
  };

  const loadSampleTranscript = () => {
    setTranscript(SAMPLE_TRANSCRIPT);
    setCurrentMessage('Sample transcript loaded. Click "Analyze Transcript" to process it.');
  };

  const handleNewTranscriptSubmit = (e) => {
    e.preventDefault();
    if (!newTranscript.trim()) return;

    console.log('ChatInterface: Submitting new transcript');
    setCurrentMessage('Analyzing new transcript against policies...');
    
    onSubmit(newTranscript);
    setNewTranscript('');
    setShowNewTranscript(false);
  };

  const handleUpdateTranscriptSubmit = (e) => {
    e.preventDefault();
    if (!updateTranscript.trim()) return;

    console.log('ChatInterface: Submitting transcript update');
    setCurrentMessage('Updating analysis with additional transcript information...');
    
    onUpdate(updateTranscript, 'transcript_update');
    setUpdateTranscript('');
    setShowUpdateTranscript(false);
  };

  useEffect(() => {
    if (error) {
      setCurrentMessage(`Error: ${error}`);
    }
  }, [error]);

  useEffect(() => {
    if (updateSuccess) {
      setCurrentMessage(updateSuccess);
      // Clear the success message after 3 seconds
      const timer = setTimeout(() => {
        onClearSuccess();
        setCurrentMessage('Analysis completed successfully! You can view the results in the Summary, Report, and Email tabs.');
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [updateSuccess, onClearSuccess]);

  return (
    <div className="chat-interface">
      {/* Initial Transcript Input - Shows when no analysis */}
      {!hasAnalysis && (
        <form onSubmit={handleSubmit} className="input-form">
          <div className="form-group">
            <div className="input-container">
              <textarea
                value={transcript}
                onChange={(e) => setTranscript(e.target.value)}
                placeholder="Paste or type the call transcript here..."
                className={`transcript-input ${loading ? 'loading' : ''}`}
                rows={6}
                disabled={loading}
              />
              {loading && (
                <div className="loading-overlay">
                  <div className="loading-content">
                    <div className="loading-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    <p>Analyzing transcript against policies...</p>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          <div className="form-actions">
            <button
              type="button"
              onClick={loadSampleTranscript}
              className="btn btn-secondary"
              disabled={loading}
            >
              Load Sample Transcript
            </button>
            
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !transcript.trim()}
            >
              {loading ? 'Analyzing...' : 'Analyze Transcript'}
            </button>
          </div>
        </form>
      )}

      {/* Post-Analysis Transcript Options */}
      {hasAnalysis && (
        <div className="transcript-options">
          <div className="transcript-actions">
            <button
              type="button"
              onClick={() => {
                setShowNewTranscript(!showNewTranscript);
                setShowUpdateTranscript(false);
              }}
              className="btn btn-secondary"
              disabled={loading}
            >
              {showNewTranscript ? 'Cancel' : 'New Transcript'}
            </button>
            
            <button
              type="button"
              onClick={() => {
                setShowUpdateTranscript(!showUpdateTranscript);
                setShowNewTranscript(false);
              }}
              className="btn btn-secondary"
              disabled={loading}
            >
              {showUpdateTranscript ? 'Cancel' : 'Update Transcript'}
            </button>
          </div>

          {/* New Transcript Form */}
          {showNewTranscript && (
            <form onSubmit={handleNewTranscriptSubmit} className="expandable-form">
              <div className="form-group">
                <label>Enter New Transcript:</label>
                <div className="input-container">
                  <textarea
                    value={newTranscript}
                    onChange={(e) => setNewTranscript(e.target.value)}
                    placeholder="Paste or type a new call transcript here..."
                    className={`transcript-input ${loading ? 'loading' : ''}`}
                    rows={6}
                    disabled={loading}
                  />
                  {loading && (
                    <div className="loading-overlay">
                      <div className="loading-content">
                        <div className="loading-dots">
                          <span></span>
                          <span></span>
                          <span></span>
                        </div>
                        <p>Analyzing new transcript...</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
              <div className="form-actions">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={loading || !newTranscript.trim()}
                >
                  {loading ? 'Analyzing...' : 'Analyze New Transcript'}
                </button>
              </div>
            </form>
          )}

          {/* Update Transcript Form */}
          {showUpdateTranscript && (
            <form onSubmit={handleUpdateTranscriptSubmit} className="expandable-form">
              <div className="form-group">
                <label>Additional Transcript Information:</label>
                <div className="input-container">
                  <textarea
                    value={updateTranscript}
                    onChange={(e) => setUpdateTranscript(e.target.value)}
                    placeholder="Provide additional transcript content or corrections..."
                    className={`transcript-input ${loading ? 'loading' : ''}`}
                    rows={4}
                    disabled={loading}
                  />
                  {loading && (
                    <div className="loading-overlay">
                      <div className="loading-content">
                        <div className="loading-dots">
                          <span></span>
                          <span></span>
                          <span></span>
                        </div>
                        <p>Updating with additional transcript...</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
              <div className="form-actions">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={loading || !updateTranscript.trim()}
                >
                  {loading ? 'Updating...' : 'Update with Transcript Info'}
                </button>
              </div>
            </form>
          )}
        </div>
      )}

      {/* Update Form - Shows after analysis */}
      {showUpdateForm && !showNewTranscript && !showUpdateTranscript && (
        <form onSubmit={handleUpdateSubmit} className="update-form">
          <h3>Update Analysis with Additional Information</h3>
          <div className="form-group">
            <label>Update Type:</label>
            <select 
              value={updateType} 
              onChange={(e) => setUpdateType(e.target.value)}
              className="update-type-select"
              disabled={loading}
            >
              <option value="incident_report">Update Incident Report</option>
              <option value="email_update">Update Email Draft</option>
            </select>
          </div>
          
          <div className="form-group">
            <textarea
              value={updateInfo}
              onChange={(e) => setUpdateInfo(e.target.value)}
              placeholder={
                updateType === 'incident_report' 
                  ? "Provide additional details to update the incident report (e.g., new injuries discovered, updated timeline, corrected information)..."
                  : "Provide information to update the email draft (e.g., change recipients, update urgency, add specific instructions)..."
              }
              className="update-input"
              rows={4}
              disabled={loading}
            />
          </div>
          
          <div className="form-actions">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !updateInfo.trim()}
            >
              {loading ? 'Updating...' : `Update ${updateType === 'incident_report' ? 'Report' : 'Email'}`}
            </button>
          </div>
        </form>
      )}

      {/* Single Status Message */}
      <div className="status-message">
        <div className="message-content">
          {loading ? (
            <div className="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          ) : (
            <p>{currentMessage}</p>
          )}
        </div>
      </div>

      <p className="session-note">Session ID: {sessionId}</p>
    </div>
  );
}

export default ChatInterface;

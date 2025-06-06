import React, { useState, useRef, useEffect } from 'react';

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

function ChatInterface({ onSubmit, onUpdate, loading, error, hasAnalysis, sessionId }) {
  const [transcript, setTranscript] = useState('');
  const [updateInfo, setUpdateInfo] = useState('');
  const [updateType, setUpdateType] = useState('general');
  const [showUpdateForm, setShowUpdateForm] = useState(false);
  const [hasShownSuccess, setHasShownSuccess] = useState(false);
  const [messages, setMessages] = useState([
    {
      type: 'system',
      content: 'Welcome to the Emma Incident Response System. Please paste or type the call transcript you want to analyze.',
    }
  ]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (hasAnalysis && !hasShownSuccess) {
      setMessages(prev => {
        const newMessages = [...prev];
        // Remove loading message if exists
        if (newMessages[newMessages.length - 1]?.loading) {
          newMessages.pop();
        }
        // Add success message
        newMessages.push({
          type: 'success',
          content: 'Analysis completed successfully! You can view the results in the Summary, Report, and Email tabs. You can also provide additional information below to update the analysis.'
        });
        return newMessages;
      });
      setShowUpdateForm(true);
      setHasShownSuccess(true);
    }
  }, [hasAnalysis, hasShownSuccess]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!transcript.trim()) return;

    console.log('ChatInterface: Submitting transcript of length:', transcript.length);

    // Add user message
    setMessages(prev => [...prev, {
      type: 'user',
      content: `Transcript submitted (${transcript.length} characters)`
    }]);

    // Add system processing message
    setMessages(prev => [...prev, {
      type: 'system',
      content: 'Analyzing transcript against policies...',
      loading: true
    }]);

    onSubmit(transcript);
  };

  const handleUpdateSubmit = (e) => {
    e.preventDefault();
    if (!updateInfo.trim()) return;

    console.log('ChatInterface: Submitting update:', updateInfo);

    // Add user message
    setMessages(prev => [...prev, {
      type: 'user',
      content: `Additional information (${updateType}): ${updateInfo}`
    }]);

    // Add system processing message
    setMessages(prev => [...prev, {
      type: 'system',
      content: 'Updating analysis with new information...',
      loading: true
    }]);

    onUpdate(updateInfo, updateType);
    setUpdateInfo('');
  };

  const loadSampleTranscript = () => {
    setTranscript(SAMPLE_TRANSCRIPT);
    setMessages(prev => [...prev, {
      type: 'system',
      content: 'Sample transcript loaded. Click "Analyze Transcript" to process it.'
    }]);
  };

  useEffect(() => {
    if (error) {
      setMessages(prev => {
        const newMessages = [...prev];
        // Remove loading message
        if (newMessages[newMessages.length - 1]?.loading) {
          newMessages.pop();
        }
        // Add error message
        newMessages.push({
          type: 'error',
          content: error
        });
        return newMessages;
      });
    }
  }, [error]);

  return (
    <div className="chat-interface">
      <div className="messages-container">
        {messages.map((message, index) => (
          <div key={index} className={`message message-${message.type}`}>
            <div className="message-content">
              {message.loading ? (
                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              ) : (
                <p>{message.content}</p>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {!hasAnalysis ? (
        <form onSubmit={handleSubmit} className="input-form">
          <div className="form-group">
            <textarea
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              placeholder="Paste or type the call transcript here..."
              className="transcript-input"
              rows={6}
              disabled={loading}
            />
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
      ) : showUpdateForm && (
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
              <option value="general">General Update</option>
              <option value="incident_details">Incident Details</option>
              <option value="email_update">Email Information</option>
              <option value="all">Update All</option>
            </select>
          </div>
          
          <div className="form-group">
            <textarea
              value={updateInfo}
              onChange={(e) => setUpdateInfo(e.target.value)}
              placeholder="Provide additional information to update the analysis..."
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
              {loading ? 'Updating...' : 'Update Analysis'}
            </button>
          </div>
        </form>
      )}

      <div className="help-text">
        <h3>How to use:</h3>
        <ol>
          <li>Paste the call transcript in the text area above</li>
          <li>Click "Analyze Transcript" to process</li>
          <li>Review the generated incident report and email draft</li>
          <li>Provide additional information to update the analysis if needed</li>
          <li>Use feedback options to refine specific components</li>
        </ol>
        <p className="session-note">Session ID: {sessionId}</p>
      </div>
    </div>
  );
}

export default ChatInterface;

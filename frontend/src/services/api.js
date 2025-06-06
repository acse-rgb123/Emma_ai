const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function handleResponse(response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
    throw new ApiError(error.detail || 'An error occurred', response.status);
  }
  return response.json();
}

export async function analyzeTranscript(transcript, sessionId = 'default') {
  console.log('API: Analyzing transcript with session:', sessionId);
  
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      transcript,
      metadata: {
        timestamp: new Date().toISOString(),
        source: 'web_interface',
        session_id: sessionId
      }
    }),
  });

  const result = await handleResponse(response);
  console.log('API: Analysis result:', result);
  return result;
}

export async function updateAnalysis(sessionId, newInfo, updateType = 'general') {
  console.log('API: Updating analysis for session:', sessionId);
  
  const response = await fetch(`${API_BASE_URL}/update_analysis`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId,
      new_information: newInfo,
      update_type: updateType
    }),
  });

  return handleResponse(response);
}

export async function regenerateComponent(component, original, feedback) {
  console.log('API: Regenerating', component);
  
  const response = await fetch(`${API_BASE_URL}/regenerate/${component}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      original,
      feedback
    }),
  });

  return handleResponse(response);
}

export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  return handleResponse(response);
}

export async function clearContext(sessionId) {
  const response = await fetch(`${API_BASE_URL}/clear_context`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId
    }),
  });

  return handleResponse(response);
}

export async function switchProvider(provider) {
  const response = await fetch(`${API_BASE_URL}/switch_provider/${provider}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  });

  return handleResponse(response);
}

export async function getProviderStatus() {
  const response = await fetch(`${API_BASE_URL}/provider_status`);
  return handleResponse(response);
}

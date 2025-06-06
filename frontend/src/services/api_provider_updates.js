// Additional API functions for provider management

export async function testProvider(provider, apiKey) {
  const response = await fetch(`${API_BASE_URL}/test_provider`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      provider,
      api_key: apiKey
    })
  });

  return handleResponse(response);
}

export async function getCurrentAnalysis() {
  const response = await fetch(`${API_BASE_URL}/current_analysis`);
  return handleResponse(response);
}

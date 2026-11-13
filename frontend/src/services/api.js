const API = (import.meta.env.VITE_API_URL || '').trim().replace(/\/+$/, '');

async function request(path, options) {
  if (import.meta.env.PROD && !API) {
    throw new Error('Production API is not configured. Set VITE_API_URL to the deployed FastAPI base URL.');
  }
  let response;
  try { response = await fetch(`${API}${path}`, options); }
  catch { throw new Error('Could not reach the API. Check that the FastAPI service is running.'); }
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(body.detail || `Request failed (${response.status}).`);
    error.status = response.status;
    error.detail = body.detail || '';
    throw error;
  }
  return body;
}
export function getAnalytics() { return request('/api/analytics'); }
export function getIncidents(filters = {}) {
  const query = new URLSearchParams(Object.entries(filters).filter(([, value]) => value));
  return request(`/api/incidents${query.size ? `?${query}` : ''}`);
}
export function analyzeIncident(text) {
  return request('/api/analyze', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text }) });
}
export function validateCsv(file) {
  const form = new FormData(); form.append('file', file);
  return request('/api/incidents/upload', { method: 'POST', body: form });
}

/**
 * Centralized API client for Retail Sales and Inventory Copilot.
 * Communicates exclusively with FastAPI backend endpoints.
 */

const API_BASE = '/api';

/**
 * Generic fetch wrapper with error handling.
 */
async function fetchJson(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const errorJson = JSON.parse(errorText);
        if (errorJson.detail) {
          errorMessage = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
        }
      } catch (e) {
        // Use default error string
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Unable to connect to the retail intelligence backend service. Please verify the backend is running.');
    }
    throw error;
  }
}

export async function getHealth() {
  return fetchJson(`${API_BASE}/health`);
}

export async function getDashboard() {
  return fetchJson(`${API_BASE}/dashboard`);
}

export async function getAttention() {
  return fetchJson(`${API_BASE}/attention`);
}

export async function getProducts() {
  return fetchJson(`${API_BASE}/products`);
}

export async function getStores() {
  return fetchJson(`${API_BASE}/stores`);
}

export async function queryCopilot(payload, options = {}) {
  return fetchJson(`${API_BASE}/copilot/query`, {
    method: 'POST',
    body: JSON.stringify(payload),
    ...options,
  });
}


/**
 * API Client Utility
 * Centralized API request handling
 */

const API_BASE = '/api';

export async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin', // Include cookies for Flask-Login
    };
    
    const config = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers,
        },
    };
    
    try {
        const response = await fetch(url, config);
        
        // Handle redirects (Flask-Login redirects to login)
        if (response.redirected && response.url.includes('/login')) {
            window.location.href = '/login';
            return null;
        }
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

export async function get(endpoint) {
    return apiRequest(endpoint, { method: 'GET' });
}

export async function post(endpoint, data) {
    return apiRequest(endpoint, {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

export async function put(endpoint, data) {
    return apiRequest(endpoint, {
        method: 'PUT',
        body: JSON.stringify(data),
    });
}

export async function del(endpoint) {
    return apiRequest(endpoint, { method: 'DELETE' });
}


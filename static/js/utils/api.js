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
        
        // Login disabled - don't redirect to login page
        // Just continue with the response
        
        let data;
        try {
            data = await response.json();
        } catch (jsonError) {
            // If response is not JSON, create error object
            const text = await response.text();
            throw new Error(`Server error: ${text || response.statusText || 'Unknown error'}`);
        }
        
        if (!response.ok) {
            // Create error object with full details
            const error = new Error(data.error || `HTTP error! status: ${response.status}`);
            error.status = response.status;
            error.details = data.details;
            error.data = data;
            throw error;
        }
        
        return data;
    } catch (error) {
        console.error('API request failed:', error);
        // If it's already our error object, re-throw it
        if (error.status || error.details) {
            throw error;
        }
        // Otherwise wrap it
        throw new Error(error.message || 'Network error');
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


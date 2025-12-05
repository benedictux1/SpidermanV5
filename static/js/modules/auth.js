/**
 * Authentication Module
 * Handles login and authentication state
 */

import { post } from '../utils/api.js';

// Login form handler
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(loginForm);
        const data = {
            username: formData.get('username'),
            password: formData.get('password'),
        };
        
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
                credentials: 'same-origin',
            });
            
            if (response.ok) {
                window.location.href = '/';
            } else {
                const error = await response.json();
                showError(error.error || 'Login failed');
            }
        } catch (error) {
            showError('Login failed. Please try again.');
        }
    });
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    const form = document.getElementById('login-form');
    if (form) {
        const existingError = form.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        form.insertBefore(errorDiv, form.firstChild);
    }
}


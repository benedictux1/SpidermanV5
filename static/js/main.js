/**
 * Main Application Entry Point
 * Initializes the application and sets up event handlers
 */

import { get, post } from './utils/api.js';
import { showNotification, showLoading, hideLoading } from './utils/ui.js';
import { loadContacts, createContact, showContactDetail, showContactsList, deleteContact, currentContactId } from './modules/contacts.js';
import { processNote, clearAnalysisResults } from './modules/notes.js';

// Check authentication on load
async function checkAuth() {
    try {
        const auth = await get('/auth/check');
        if (auth.authenticated) {
            document.getElementById('current-user').textContent = `Logged in as ${auth.user.username}`;
            await loadContacts();
        } else {
            window.location.href = '/login';
        }
    } catch (error) {
        window.location.href = '/login';
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    setupEventHandlers();
});

function setupEventHandlers() {
    // Logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            try {
                await post('/auth/logout', {});
                window.location.href = '/login';
            } catch (error) {
                console.error('Logout error:', error);
                window.location.href = '/login';
            }
        });
    }
    
    // Create contact button
    const createContactBtn = document.getElementById('create-contact-btn');
    if (createContactBtn) {
        createContactBtn.addEventListener('click', () => {
            const modal = document.getElementById('create-contact-modal');
            if (modal) {
                modal.classList.add('active');
            }
        });
    }
    
    // Create contact form
    const createContactForm = document.getElementById('create-contact-form');
    if (createContactForm) {
        createContactForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(createContactForm);
            const fullName = formData.get('full_name');
            const tier = parseInt(formData.get('tier'));
            
            try {
                await createContact(fullName, tier);
                createContactForm.reset();
                // When creating a new contact, ensure analysis panel is reset
                clearAnalysisResults();
                const modal = document.getElementById('create-contact-modal');
                if (modal) {
                    modal.classList.remove('active');
                }
            } catch (error) {
                // Error already shown in createContact
            }
        });
    }
    
    // Close modal
    const closeModal = document.querySelector('.close');
    if (closeModal) {
        closeModal.addEventListener('click', () => {
            const modal = document.getElementById('create-contact-modal');
            if (modal) {
                modal.classList.remove('active');
            }
        });
    }
    
    // Back to contacts
    const backBtn = document.getElementById('back-to-contacts');
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            showContactsList();
            // Clear analysis results when leaving contact detail view
            clearAnalysisResults();
        });
    }
    
    // Delete contact button
    const deleteContactBtn = document.getElementById('delete-contact-btn');
    if (deleteContactBtn) {
        deleteContactBtn.addEventListener('click', async () => {
            if (currentContactId) {
                await deleteContact(currentContactId);
            }
        });
    }
    
    // Add note form
    const addNoteForm = document.getElementById('add-note-form');
    if (addNoteForm) {
        addNoteForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(addNoteForm);
            const noteText = formData.get('note');
            
            if (!currentContactId) {
                showNotification('Please select a contact first', 'error');
                return;
            }
            
            if (!noteText || !noteText.trim()) {
                showNotification('Please enter a note', 'error');
                return;
            }
            
            try {
                await processNote(noteText.trim(), currentContactId);
                addNoteForm.reset();
                
                // Reload contact details to show updated categories and audit trail
                if (currentContactId) {
                    await showContactDetail(currentContactId);
                }
            } catch (error) {
                // Error already shown in processNote
            }
        });
    }
    
    // Make reloadContactDetail available globally
    window.reloadContactDetail = async () => {
        if (currentContactId) {
            await showContactDetail(currentContactId);
        }
    };
}


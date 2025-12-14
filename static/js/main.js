/**
 * Main Application Entry Point
 * Initializes the application and sets up event handlers
 */

import { get, post } from './utils/api.js';
import { showNotification, showLoading, hideLoading } from './utils/ui.js';
import { loadContacts, createContact, showContactDetail, showContactsList, deleteContact, currentContactId, openEditCategoriesModal, saveCategories } from './modules/contacts.js';
import { processNote, clearAnalysisResults } from './modules/notes.js';

// Check authentication on load (optional - login disabled)
async function checkAuth() {
    try {
        const auth = await get('/auth/check');
        if (auth.authenticated) {
            const userElement = document.getElementById('current-user');
            if (userElement) {
                userElement.textContent = `Logged in as ${auth.user.username}`;
            }
        } else {
            // Login disabled - show as guest user
            const userElement = document.getElementById('current-user');
            if (userElement) {
                userElement.textContent = 'Guest Mode';
            }
        }
        // Always load contacts (login disabled)
        await loadContacts();
    } catch (error) {
        // Login disabled - continue anyway
        console.log('Auth check failed, continuing in guest mode:', error);
        const userElement = document.getElementById('current-user');
        if (userElement) {
            userElement.textContent = 'Guest Mode';
        }
        await loadContacts();
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    setupEventHandlers();
});

function setupEventHandlers() {
    // Export CSV button
    const exportCsvBtn = document.getElementById('export-csv-btn');
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', async () => {
            try {
                showLoading();
                showNotification('Preparing CSV export...', 'info');
                
                // Fetch CSV from API
                const response = await fetch('/api/contacts/export/csv', {
                    method: 'GET',
                    credentials: 'same-origin'
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Failed to export CSV');
                }
                
                // Get CSV content
                const csvContent = await response.text();
                
                // Create download link
                const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                
                // Get filename from Content-Disposition header or use default
                const contentDisposition = response.headers.get('Content-Disposition');
                let filename = 'kith_platform_export.csv';
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
                    if (filenameMatch) {
                        filename = filenameMatch[1];
                    }
                }
                
                link.download = filename;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(url);
                
                showNotification('CSV export downloaded successfully!', 'success');
            } catch (error) {
                console.error('Export CSV error:', error);
                showNotification(error.message || 'Failed to export CSV', 'error');
            } finally {
                hideLoading();
            }
        });
    }
    
    // Logout button (disabled - login disabled)
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        // Hide logout button since login is disabled
        logoutBtn.style.display = 'none';
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
    
    // Edit Categories button
    const editCategoriesBtn = document.getElementById('edit-categories-btn');
    if (editCategoriesBtn) {
        editCategoriesBtn.addEventListener('click', () => {
            if (currentContactId) {
                openEditCategoriesModal(currentContactId);
            } else {
                showNotification('Please select a contact first', 'error');
            }
        });
    }
    
    // Save Categories button
    const saveCategoriesBtn = document.getElementById('save-categories-btn');
    if (saveCategoriesBtn) {
        saveCategoriesBtn.addEventListener('click', () => {
            if (currentContactId) {
                saveCategories(currentContactId);
            }
        });
    }
    
    // Cancel Edit Categories
    const cancelEditCategories = document.getElementById('cancel-edit-categories');
    const closeEditCategories = document.querySelector('.close-edit-categories');
    const closeEditCategoriesHandler = () => {
        const modal = document.getElementById('edit-categories-modal');
        if (modal) {
            modal.style.display = 'none';
            modal.classList.remove('active');
        }
    };
    
    if (cancelEditCategories) {
        cancelEditCategories.addEventListener('click', closeEditCategoriesHandler);
    }
    if (closeEditCategories) {
        closeEditCategories.addEventListener('click', closeEditCategoriesHandler);
    }
    
    // Add Category button
    const addCategoryBtn = document.getElementById('add-category-btn');
    if (addCategoryBtn) {
        addCategoryBtn.addEventListener('click', () => {
            const newCategorySelect = document.getElementById('new-category-select');
            const newCategoryContent = document.getElementById('new-category-content');
            
            if (!newCategorySelect || !newCategoryContent) return;
            
            const category = newCategorySelect.value;
            const content = newCategoryContent.value.trim();
            
            if (!category) {
                showNotification('Please select a category', 'error');
                return;
            }
            
            if (!content) {
                showNotification('Please enter content for the category', 'error');
                return;
            }
            
            // Check if category already exists in the form
            const editList = document.getElementById('categories-edit-list');
            const existingTextarea = editList?.querySelector(`textarea[data-category="${category}"]`);
            
            if (existingTextarea) {
                // Update existing textarea
                existingTextarea.value = content;
                showNotification(`Updated ${category} category`, 'success');
            } else {
                showNotification('Category not found in form', 'error');
            }
            
            // Clear fields
            newCategorySelect.value = '';
            newCategoryContent.value = '';
        });
    }
}


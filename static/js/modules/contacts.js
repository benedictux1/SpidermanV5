/**
 * Contacts Module
 * Handles contact management
 */

import { get, post } from '../utils/api.js';
import { showNotification, showLoading, hideLoading } from '../utils/ui.js';
import { clearAnalysisResults } from './notes.js';

let currentContactId = null;

export async function loadContacts() {
    try {
        showLoading();
        const contacts = await get('/contacts');
        renderContacts(contacts);
    } catch (error) {
        showNotification('Failed to load contacts', 'error');
        console.error('Error loading contacts:', error);
    } finally {
        hideLoading();
    }
}

function renderContacts(contacts) {
    const container = document.getElementById('contacts-list');
    if (!container) return;
    
    if (contacts.length === 0) {
        container.innerHTML = '<p>No contacts yet. Create your first contact!</p>';
        return;
    }
    
    container.innerHTML = contacts.map(contact => `
        <div class="contact-card" data-contact-id="${contact.id}">
            <h3>${escapeHtml(contact.full_name)}</h3>
            <span class="tier tier-${contact.tier}">Tier ${contact.tier}</span>
        </div>
    `).join('');
    
    // Add click handlers
    container.querySelectorAll('.contact-card').forEach(card => {
        card.addEventListener('click', () => {
            const contactId = parseInt(card.dataset.contactId);
            showContactDetail(contactId);
        });
    });
}

export async function createContact(fullName, tier = 2) {
    try {
        showLoading();
        const contact = await post('/contacts', {
            full_name: fullName,
            tier: tier
        });
        showNotification(`Contact "${contact.full_name}" created successfully`);
        await loadContacts();
        return contact;
    } catch (error) {
        // Extract error message from API response
        let errorMessage = 'Failed to create contact';
        if (error.message) {
            errorMessage = error.message;
        } else if (error.error) {
            errorMessage = error.error;
            if (error.details) {
                errorMessage += `: ${error.details}`;
            }
        }
        console.error('Create contact error:', error);
        showNotification(errorMessage, 'error');
        throw error;
    } finally {
        hideLoading();
    }
}

export async function showContactDetail(contactId) {
    currentContactId = contactId;
    
    try {
        showLoading();
        
        // Reset analysis panel and note input when switching contacts
        clearAnalysisResults();
        const noteTextArea = document.querySelector('#add-note-form textarea[name="note"]');
        if (noteTextArea) {
            noteTextArea.value = '';
        }
        
        // Hide contacts section, show detail section
        document.getElementById('contacts-section').style.display = 'none';
        document.getElementById('contact-detail-section').style.display = 'block';
        
        // Load contact details
        const contact = await get(`/contacts/${contactId}`);
        document.getElementById('contact-detail-name').textContent = contact.full_name;
        
        // Load categories
        renderCategories(contact.categorized_data || {});
        
        // Load audit trail
        await loadAuditTrail(contactId);
        
    } catch (error) {
        showNotification('Failed to load contact details', 'error');
        console.error('Error loading contact:', error);
    } finally {
        hideLoading();
    }
}

export function showContactsList() {
    currentContactId = null;
    document.getElementById('contacts-section').style.display = 'block';
    document.getElementById('contact-detail-section').style.display = 'none';
}

export async function deleteContact(contactId) {
    /** Delete a contact with confirmation */
    try {
        // Show confirmation dialog
        const contactName = document.getElementById('contact-detail-name')?.textContent || 'this contact';
        const confirmed = confirm(`Are you sure you want to delete "${contactName}"?\n\nThis will permanently delete the contact and all associated notes. This action cannot be undone.`);
        
        if (!confirmed) {
            return false;
        }
        
        showLoading();
        const { del } = await import('../utils/api.js');
        await del(`/contacts/${contactId}`);
        
        showNotification(`Contact "${contactName}" deleted successfully`);
        
        // Return to contacts list
        showContactsList();
        await loadContacts();
        
        return true;
    } catch (error) {
        showNotification(error.message || 'Failed to delete contact', 'error');
        console.error('Error deleting contact:', error);
        return false;
    } finally {
        hideLoading();
    }
}

// Store current categorized data for editing
let currentCategorizedData = {};

function renderCategories(categorizedData) {
    const container = document.getElementById('categories-list');
    if (!container) return;
    
    // Store for editing
    currentCategorizedData = categorizedData;
    
    // Define all categories in order
    const allCategories = [
        'Actionable',
        'Goals',
        'Relationship_Strategy',
        'Social',
        'Professional_Background',
        'Financial_Situation',
        'Wellbeing',
        'Avocation',
        'Environment_And_Lifestyle',
        'Psychology_And_Values',
        'Communication_Style',
        'Challenges_And_Development',
        'Deeper_Insights',
        'Admin_matters',
        'Others'
    ];
    
    // Render all categories, showing empty state for ones without data
    container.innerHTML = allCategories.map(category => {
        const items = categorizedData[category] || [];
        const hasData = items.length > 0;
        
        return `
        <div class="category-group ${!hasData ? 'category-empty' : ''}">
            <h4>${escapeHtml(category.replace(/_/g, ' '))}</h4>
            ${hasData ? items.map(item => `
                <div class="category-item">
                    <div class="category-content">${renderMarkdown(item.content)}</div>
                </div>
            `).join('') : '<div class="category-empty-message">No entries yet</div>'}
        </div>
    `;
    }).join('');
}

export async function openEditCategoriesModal(contactId) {
    try {
        showLoading();
        // Get current contact data
        const contact = await get(`/contacts/${contactId}`);
        const categorizedData = contact.categorized_data || {};
        
        // Populate edit form
        const editList = document.getElementById('categories-edit-list');
        if (!editList) {
            hideLoading();
            return;
        }
        
        // Define all categories
        const allCategories = [
            'Actionable',
            'Goals',
            'Relationship_Strategy',
            'Social',
            'Professional_Background',
            'Financial_Situation',
            'Wellbeing',
            'Avocation',
            'Environment_And_Lifestyle',
            'Psychology_And_Values',
            'Communication_Style',
            'Challenges_And_Development',
            'Deeper_Insights',
            'Admin_matters',
            'Others'
        ];
        
        editList.innerHTML = allCategories.map(category => {
            const items = categorizedData[category] || [];
            // Combine all entries for this category (in case there are multiple)
            const content = items.length > 0 ? items.map(item => item.content).join('\n\n') : '';
            // Use the first entry ID if exists (for updates), or all IDs if multiple
            const entryId = items.length > 0 ? items[0].id : null;
            
            return `
                <div class="category-edit-item" style="margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid #eee;">
                    <label style="display: block; font-weight: 600; margin-bottom: 0.5rem; color: #333;">
                        ${escapeHtml(category.replace(/_/g, ' '))}
                    </label>
                    <textarea 
                        class="form-control category-edit-textarea" 
                        data-category="${category}"
                        data-entry-id="${entryId || ''}"
                        rows="4"
                        style="width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-family: inherit; font-size: 0.95rem;"
                        placeholder="No content yet...">${escapeHtml(content)}</textarea>
                    ${content ? `<button class="btn btn-danger btn-sm clear-category-btn" data-category="${category}" style="margin-top: 0.5rem; padding: 0.25rem 0.75rem; font-size: 0.85rem;">Clear</button>` : ''}
                </div>
            `;
        }).join('');
        
        // Add event listeners for clear buttons
        editList.querySelectorAll('.clear-category-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const category = btn.dataset.category;
                const textarea = editList.querySelector(`textarea[data-category="${category}"]`);
                if (textarea) {
                    textarea.value = '';
                }
            });
        });
        
        // Show modal
        const modal = document.getElementById('edit-categories-modal');
        if (modal) {
            modal.style.display = 'block';
            modal.classList.add('active');
        }
        
        hideLoading();
    } catch (error) {
        console.error('Error opening edit categories modal:', error);
        showNotification('Failed to load categories for editing', 'error');
        hideLoading();
    }
}

export async function saveCategories(contactId) {
    try {
        const editList = document.getElementById('categories-edit-list');
        if (!editList) return;
        
        const updates = [];
        const textareas = editList.querySelectorAll('.category-edit-textarea');
        
        textareas.forEach(textarea => {
            const category = textarea.dataset.category;
            const entryId = textarea.dataset.entryId;
            const content = textarea.value.trim();
            
            // Only include if there's content or if it's an existing entry (to allow deletion)
            if (content || entryId) {
                updates.push({
                    category: category,
                    content: content,
                    entry_id: entryId || null
                });
            }
        });
        
        // Check for new category
        const newCategorySelect = document.getElementById('new-category-select');
        const newCategoryContent = document.getElementById('new-category-content');
        
        if (newCategorySelect && newCategorySelect.value && newCategoryContent && newCategoryContent.value.trim()) {
            // Check if category already exists in updates
            const categoryExists = updates.some(u => u.category === newCategorySelect.value);
            if (!categoryExists) {
                updates.push({
                    category: newCategorySelect.value,
                    content: newCategoryContent.value.trim(),
                    entry_id: null
                });
            }
        }
        
        if (updates.length === 0) {
            showNotification('No changes to save', 'info');
            return;
        }
        
        showLoading();
        
        // Call API
        const { put } = await import('../utils/api.js');
        const result = await put(`/contacts/${contactId}/categories`, { updates });
        
        showNotification(result.message || 'Categories updated successfully!', 'success');
        
        // Close modal
        const modal = document.getElementById('edit-categories-modal');
        if (modal) {
            modal.style.display = 'none';
            modal.classList.remove('active');
        }
        
        // Clear new category fields
        if (newCategorySelect) newCategorySelect.value = '';
        if (newCategoryContent) newCategoryContent.value = '';
        
        // Reload contact details
        await showContactDetail(contactId);
        
    } catch (error) {
        console.error('Error saving categories:', error);
        showNotification(error.message || 'Failed to save categories', 'error');
    } finally {
        hideLoading();
    }
}

async function loadAuditTrail(contactId) {
    try {
        const logs = await get(`/contacts/${contactId}/logs`);
        renderAuditTrail(logs.raw_notes || []);
    } catch (error) {
        console.error('Error loading audit trail:', error);
    }
}

function renderAuditTrail(notes) {
    const container = document.getElementById('logs-list');
    if (!container) return;
    
    if (notes.length === 0) {
        container.innerHTML = '<p>No notes yet.</p>';
        return;
    }
    
    container.innerHTML = notes.map(note => {
        const isManualEdit = note.source === 'manual_edit';
        const sourceBadge = isManualEdit ? '<span class="source-badge" style="background: #28a745; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.85rem; margin-left: 0.5rem;">✏️ Manual Edit</span>' : '';
        
        return `
        <div class="log-entry ${isManualEdit ? 'manual-edit-entry' : ''}" style="${isManualEdit ? 'border-left: 3px solid #28a745; padding-left: 1rem;' : ''}">
            <div class="log-date" style="display: flex; align-items: center; gap: 0.5rem;">
                ${formatDate(note.created_at)}
                ${sourceBadge}
            </div>
            <div class="log-content">${escapeHtml(note.content)}</div>
            ${note.synthesized_entries && note.synthesized_entries.length > 0 ? `
                <div class="synthesized-entries">
                    ${note.synthesized_entries.map(entry => `
                        <div class="synthesized-entry">
                            <span class="category-badge">${escapeHtml(entry.category)}</span>
                            <span class="category-content">${renderMarkdown(entry.content)}</span>
                            ${entry.confidence ? `<span class="confidence">Confidence: ${(entry.confidence * 100).toFixed(0)}%</span>` : ''}
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        </div>
    `;
    }).join('');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function renderMarkdown(text) {
    if (!text) return '';
    
    const lines = text.split('\n');
    const result = [];
    let currentList = [];
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        
        // Check if this is a bullet point
        const bulletMatch = line.match(/^(\s*)-\s+(.+)$/);
        
        if (bulletMatch) {
            const indent = bulletMatch[1].length;
            const content = bulletMatch[2];
            
            // Process inline formatting in content
            const processedContent = processInlineMarkdown(content);
            currentList.push({ indent, content: processedContent });
        } else {
            // Not a bullet point - close any open list first
            if (currentList.length > 0) {
                result.push(buildList(currentList));
                currentList = [];
            }
            
            // Add the line (or empty line)
            if (line.trim()) {
                const processed = processInlineMarkdown(line.trim());
                result.push(processed);
            } else if (i < lines.length - 1) {
                // Empty line (but not the last line)
                result.push('<br>');
            }
        }
    }
    
    // Close any remaining list
    if (currentList.length > 0) {
        result.push(buildList(currentList));
    }
    
    return result.join('');
}

function processInlineMarkdown(text) {
    // Escape HTML first
    let html = escapeHtml(text);
    
    // Convert **bold** to <strong> first (before processing single *)
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // Convert *italic* to <em> - match single asterisks that aren't part of **
    // Use a simple pattern: *text* where text doesn't contain *
    html = html.replace(/\*([^*]+?)\*/g, '<em>$1</em>');
    
    return html;
}

function buildList(listItems) {
    if (listItems.length === 0) return '';
    
    // Simple approach: group consecutive items with same indent
    let html = '';
    let currentGroup = [];
    let currentIndent = null;
    
    for (const item of listItems) {
        if (currentIndent === null || item.indent === currentIndent) {
            currentGroup.push(item);
            currentIndent = item.indent;
        } else {
            // Different indent - close current group and start new one
            if (currentGroup.length > 0) {
                const marginLeft = currentIndent > 0 ? ` style="margin-left: ${currentIndent * 1.5}em;"` : '';
                const itemsHtml = currentGroup.map(i => `<li${marginLeft}>${i.content}</li>`).join('');
                html += `<ul>${itemsHtml}</ul>`;
            }
            currentGroup = [item];
            currentIndent = item.indent;
        }
    }
    
    // Close final group
    if (currentGroup.length > 0) {
        const marginLeft = currentIndent > 0 ? ` style="margin-left: ${currentIndent * 1.5}em;"` : '';
        const itemsHtml = currentGroup.map(i => `<li${marginLeft}>${i.content}</li>`).join('');
        html += `<ul>${itemsHtml}</ul>`;
    }
    
    return html;
}

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString();
}

export { currentContactId };


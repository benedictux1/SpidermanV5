/**
 * Search Module
 * Handles contact search functionality
 */

import { get } from '../utils/api.js';
import { showContactDetail } from './contacts.js';

let searchTimeout = null;
let isSearchMode = false;

export function initSearch() {
    const searchInput = document.getElementById('search-input');
    const clearBtn = document.getElementById('clear-search-btn');
    const dropdown = document.getElementById('search-results-dropdown');
    
    if (!searchInput) return;
    
    // Real-time search with debounce
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        
        // Show/hide clear button
        if (query.length > 0) {
            clearBtn.style.display = 'block';
        } else {
            clearBtn.style.display = 'none';
            dropdown.style.display = 'none';
            isSearchMode = false;
            // Reload all contacts
            if (window.loadContacts) {
                window.loadContacts();
            }
            return;
        }
        
        // Clear previous timeout
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }
        
        // Show loading
        dropdown.innerHTML = '<div class="search-result-loading">Searching...</div>';
        dropdown.style.display = 'block';
        
        // Debounce search (300ms)
        searchTimeout = setTimeout(() => {
            performSearch(query, false);
        }, 300);
    });
    
    // Enter key - perform search and update contacts list
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            const query = searchInput.value.trim();
            if (query.length > 0) {
                performSearch(query, true);
            }
        } else if (e.key === 'Escape') {
            clearSearch();
        }
    });
    
    // Clear search button
    if (clearBtn) {
        clearBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            clearSearch();
        });
    }
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });
}

function clearSearch() {
    const searchInput = document.getElementById('search-input');
    const clearBtn = document.getElementById('clear-search-btn');
    const dropdown = document.getElementById('search-results-dropdown');
    
    if (searchInput) searchInput.value = '';
    if (clearBtn) clearBtn.style.display = 'none';
    if (dropdown) dropdown.style.display = 'none';
    
    isSearchMode = false;
    
    // Reload all contacts
    if (window.loadContacts) {
        window.loadContacts();
    }
}

async function performSearch(query, updateContactsList = false) {
    const dropdown = document.getElementById('search-results-dropdown');
    if (!dropdown) return;
    
    try {
        const response = await get(`/contacts/search?q=${encodeURIComponent(query)}`);
        const results = response.results || [];
        
        if (results.length > 0) {
            renderSearchResults(results, dropdown, query);
            dropdown.style.display = 'block';
            
            // If Enter was pressed, also update the contacts list
            if (updateContactsList) {
                isSearchMode = true;
                renderContactsFromSearch(results, query);
            }
        } else {
            dropdown.innerHTML = '<div class="search-result-empty">No contacts found matching "' + escapeHtml(query) + '"</div>';
            dropdown.style.display = 'block';
            
            if (updateContactsList) {
                const contactsList = document.getElementById('contacts-list');
                if (contactsList) {
                    contactsList.innerHTML = '<p>No contacts found matching "' + escapeHtml(query) + '"</p>';
                }
            }
        }
    } catch (error) {
        console.error('Search error:', error);
        console.error('Error details:', error.details);
        const errorMessage = error.details || error.message || 'Error searching contacts';
        dropdown.innerHTML = '<div class="search-result-empty" style="color: #dc3545;">Error: ' + escapeHtml(errorMessage) + '</div>';
        dropdown.style.display = 'block';
    }
}

function renderSearchResults(results, container, query) {
    container.innerHTML = results.map(result => {
        const matchInfo = result.matches.map(match => {
            if (match.type === 'name') {
                return 'Match in: Name';
            } else if (match.type === 'category') {
                return `Match in: ${match.category.replace(/_/g, ' ')} category`;
            } else if (match.type === 'note') {
                const sourceLabel = match.source === 'manual_edit' ? 'Manual Edit' : 'Audit Trail';
                return `Match in: ${sourceLabel}`;
            }
            return 'Match found';
        }).join(', ');
        
        const snippet = result.matches[0]?.snippet || '';
        const highlightedSnippet = highlightSearchTerm(snippet, query || '');
        
        return `
            <div class="search-result-item" data-contact-id="${result.id}">
                <div class="search-result-name">
                    ${escapeHtml(result.full_name)}
                    <span class="search-result-tier">Tier ${result.tier}</span>
                </div>
                <div class="search-result-match">${matchInfo}</div>
                ${snippet ? `<div class="search-result-snippet">${highlightedSnippet}</div>` : ''}
            </div>
        `;
    }).join('');
    
    // Add click handlers
    container.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('click', () => {
            const contactId = parseInt(item.dataset.contactId);
            if (contactId) {
                showContactDetail(contactId);
                // Close dropdown
                container.style.display = 'none';
                // Clear search
                clearSearch();
            }
        });
    });
}

function renderContactsFromSearch(results, query) {
    const contactsList = document.getElementById('contacts-list');
    if (!contactsList) return;
    
    if (results.length === 0) {
        contactsList.innerHTML = '<p>No contacts found.</p>';
        return;
    }
    
    // Use the same rendering as loadContacts but with search results
    contactsList.innerHTML = results.map(result => {
        const matchTypes = result.matches.map(m => {
            if (m.type === 'name') return 'Name match';
            if (m.type === 'category') return `${m.category.replace(/_/g, ' ')} match`;
            if (m.type === 'note') return 'Note match';
            return 'Match';
        }).join(', ');
        
        return `
        <div class="contact-card" data-contact-id="${result.id}">
            <h3>${escapeHtml(result.full_name)}</h3>
            <span class="tier tier-${result.tier}">Tier ${result.tier}</span>
            <div style="font-size: 0.85rem; color: #666; margin-top: 0.5rem;">
                ${matchTypes}
            </div>
        </div>
    `;
    }).join('');
    
    // Add click handlers
    contactsList.querySelectorAll('.contact-card').forEach(card => {
        card.addEventListener('click', () => {
            const contactId = parseInt(card.dataset.contactId);
            if (contactId) {
                showContactDetail(contactId);
            }
        });
    });
}

function highlightSearchTerm(text, query) {
    if (!query || !text) return escapeHtml(text);
    
    const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
    return escapeHtml(text).replace(regex, '<mark style="background: #ffeb3b; padding: 0.1rem 0.2rem;">$1</mark>');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}


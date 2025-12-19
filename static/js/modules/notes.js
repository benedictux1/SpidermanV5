/**
 * Notes Module
 * Handles note processing and analysis
 */

import { post } from '../utils/api.js';
import { showNotification, showLoading, hideLoading } from '../utils/ui.js';
import { currentContactId } from './contacts.js';

export async function processNote(noteText, contactId) {
    try {
        showLoading();
        const result = await post('/notes/process-note', {
            note: noteText,
            contact_id: contactId
        });
        
        if (result.success) {
            showNotification(`Note analyzed successfully! Found ${result.categories_count} categories.`);
            displayAnalysisResults(result.synthesis);
            
            // Reload contact details to show updated categories
            if (window.reloadContactDetail) {
                window.reloadContactDetail();
            }
        }
        
        return result;
    } catch (error) {
        showNotification(error.message || 'Failed to process note', 'error');
        throw error;
    } finally {
        hideLoading();
    }
}

export function clearAnalysisResults() {
    const container = document.getElementById('categories-display');
    const resultsDiv = document.getElementById('analysis-results');
    
    if (!container || !resultsDiv) return;
    
    container.innerHTML = '<p>No categories extracted.</p>';
    resultsDiv.style.display = 'none';
}

function displayAnalysisResults(synthesis) {
    const container = document.getElementById('categories-display');
    const resultsDiv = document.getElementById('analysis-results');
    
    if (!container || !resultsDiv) return;
    
    if (!synthesis || synthesis.length === 0) {
        clearAnalysisResults();
        resultsDiv.style.display = 'block';
        return;
    }
    
    container.innerHTML = synthesis.map(item => `
        <div class="category-item">
            <div><strong>${escapeHtml(item.category)}</strong></div>
            <div class="category-content">${renderMarkdown(item.content)}</div>
        </div>
    `).join('');
    
    resultsDiv.style.display = 'block';
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
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
        
        // Check if this is a bullet point - support multiple formats:
        // - `- ` (dash-space) - standard markdown
        // - `• ` (Unicode bullet)
        // - `* ` (asterisk)
        // - `+ ` (plus)
        // - `◦ ` (white circle)
        // - `▪ ` (black square)
        const bulletMatch = line.match(/^(\s*)([-•*+◦▪])\s+(.+)$/);
        
        if (bulletMatch) {
            const indent = bulletMatch[1].length;
            const content = bulletMatch[3]; // Changed from [2] to [3] to get the content after bullet
            
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


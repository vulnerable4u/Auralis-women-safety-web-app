/**
 * Admin Dashboard JavaScript
 * Handles admin dashboard functionality, user management, and system monitoring
 */

let detectabilityMap = null;
let detectabilityMarkers = [];
let systemMonitoringInterval = null;
let detectabilityRefreshInterval = null;

// Get CSRF token for API requests
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// Enhanced fetch function with CSRF token
function secureFetch(url, options = {}) {
    const csrfToken = getCsrfToken();
    
    // Set default headers
    const headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
        ...options.headers
    };
    
    return fetch(url, {
        ...options,
        headers: headers
    });
}

document.addEventListener('DOMContentLoaded', function() {
    initializeAdminDashboard();
});

function initializeAdminDashboard() {
    initializeDetectability();
    initializeUserManagement();
    initializeSystemMonitoring();
    initializeTheme();
    
    // Auto-refresh intervals
    detectabilityRefreshInterval = setInterval(loadDetectabilityData, 10000);
    systemMonitoringInterval = setInterval(loadSystemStats, 5000);
}

function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // Theme toggle button
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update theme icon
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.className = newTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// Detectability Features
function initializeDetectability() {
    // Initialize map
    try {
        detectabilityMap = L.map('detectability-map').setView([28.6139, 77.2090], 10);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(detectabilityMap);
    } catch (error) {
        console.error('Error initializing detectability map:', error);
        const mapContainer = document.getElementById('detectability-map');
        if (mapContainer) {
            mapContainer.innerHTML = '<p style="text-align: center; padding: 20px; color: #666;">Map initialization failed</p>';
        }
    }
    
    // Load detectability data
    loadDetectabilityData();
    
    // Refresh button
    const refreshBtn = document.getElementById('refresh-detectability');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            loadDetectabilityData();
        });
    }
}

function loadDetectabilityData() {
    secureFetch('/api/admin/detectability')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            updateDetectabilityMap(data.users || []);
            updateDetectabilityList(data.users || []);
        })
        .catch(error => {
            console.error('Error loading detectability data:', error);
            showDetectabilityError('Failed to load detectability data');
        });
}

function updateDetectabilityMap(users) {
    if (!detectabilityMap) return;
    
    // Clear existing markers
    detectabilityMarkers.forEach(marker => detectabilityMap.removeLayer(marker));
    detectabilityMarkers = [];
    
    const bounds = [];
    
    users.forEach(user => {
        if (user.location) {
            const color = getThreatColor(user.threat_level);
            const icon = L.divIcon({
                className: 'custom-marker',
                html: `<div style="background: ${color}; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 10px rgba(0,0,0,0.3);"></div>`,
                iconSize: [20, 20],
                iconAnchor: [10, 10]
            });
            
            const marker = L.marker([user.location.lat, user.location.lng], { icon: icon })
                .addTo(detectabilityMap)
                .bindPopup(`
                    <strong>${escapeHtml(user.username)}</strong><br>
                    Status: ${user.status}<br>
                    Threat: ${user.threat_level}<br>
                    Last Seen: ${new Date(user.last_seen).toLocaleTimeString()}
                `);
            
            detectabilityMarkers.push(marker);
            bounds.push([user.location.lat, user.location.lng]);
        }
    });
    
    if (bounds.length > 0) {
        detectabilityMap.fitBounds(bounds, { padding: [50, 50] });
    }
}

function updateDetectabilityList(users) {
    const container = document.getElementById('detectability-users');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (users.length === 0) {
        container.innerHTML = '<p class="loading-text">No active users detected</p>';
        return;
    }
    
    users.forEach(user => {
        const item = document.createElement('div');
        item.className = `user-detect-item status-${user.threat_level.toLowerCase()}`;
        
        const locationText = user.location 
            ? `Location: ${user.location.lat.toFixed(4)}, ${user.location.lng.toFixed(4)}`
            : 'Location: Not available';
        
        item.innerHTML = `
            <h4>${escapeHtml(user.username)}</h4>
            <p><i class="fas fa-circle"></i> Status: <strong>${user.status}</strong></p>
            <p><i class="fas fa-exclamation-triangle"></i> Threat: <strong>${user.threat_level}</strong></p>
            <p><i class="fas fa-map-marker-alt"></i> ${locationText}</p>
            <p><i class="fas fa-clock"></i> Last Seen: ${new Date(user.last_seen).toLocaleString()}</p>
        `;
        
        container.appendChild(item);
    });
}

function showDetectabilityError(message) {
    const container = document.getElementById('detectability-users');
    if (container) {
        container.innerHTML = `<p class="error-text">${escapeHtml(message)}</p>`;
    }
}

function getThreatColor(level) {
    const colors = {
        'SAFE': '#10b981',
        'LOW': '#f59e0b',
        'MEDIUM': '#f97316',
        'HIGH': '#ef4444',
        'CRITICAL': '#dc2626'
    };
    return colors[level] || '#6c757d';
}

// User Management
function initializeUserManagement() {
    // View contacts buttons
    document.querySelectorAll('.btn-view-contacts').forEach(btn => {
        btn.addEventListener('click', function() {
            const username = this.getAttribute('data-username');
            viewUserContacts(username);
        });
    });
    
    // View details buttons
    document.querySelectorAll('.btn-view').forEach(btn => {
        btn.addEventListener('click', function() {
            const username = this.getAttribute('data-username');
            viewUserDetails(username);
        });
    });
    
    // Delete buttons
    document.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', function() {
            const username = this.getAttribute('data-username');
            deleteUser(username);
        });
    });
}

function viewUserContacts(username) {
    secureFetch(`/api/admin/user_details/${username}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch user details');
            }
            return response.json();
        })
        .then(data => {
            const contactsHtml = data.contacts && data.contacts.length > 0 
                ? data.contacts.map(contact => `
                    <div class="contact-item">
                        <h4>${escapeHtml(contact.name)}</h4>
                        <p><i class="fas fa-phone"></i> ${escapeHtml(contact.phone)}</p>
                        ${contact.email ? `<p><i class="fas fa-envelope"></i> ${escapeHtml(contact.email)}</p>` : ''}
                        ${contact.relation ? `<p><i class="fas fa-user"></i> ${escapeHtml(contact.relation)}</p>` : ''}
                    </div>
                `).join('')
                : '<p>No contacts registered</p>';
            
            showModal(`Contacts - ${username}`, `
                <h3>Emergency Contacts for ${escapeHtml(username)}</h3>
                ${contactsHtml}
            `);
        })
        .catch(error => {
            console.error('Error loading user contacts:', error);
            showError('Error loading user contacts');
        });
}

function viewUserDetails(username) {
    secureFetch(`/api/admin/user_details/${username}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch user details');
            }
            return response.json();
        })
        .then(data => {
            const contactsHtml = data.contacts && data.contacts.length > 0 
                ? data.contacts.map(contact => `
                    <div class="contact-item">
                        <h4>${escapeHtml(contact.name)}</h4>
                        <p><i class="fas fa-phone"></i> ${escapeHtml(contact.phone)}</p>
                        ${contact.email ? `<p><i class="fas fa-envelope"></i> ${escapeHtml(contact.email)}</p>` : ''}
                        ${contact.relation ? `<p><i class="fas fa-user"></i> ${escapeHtml(contact.relation)}</p>` : ''}
                    </div>
                `).join('')
                : '<p>No contacts registered</p>';
            
            showModal(`User Details - ${username}`, `
                <div class="user-details">
                    <h3>${escapeHtml(username)}</h3>
                    <p><strong>Created:</strong> ${escapeHtml(data.created_at || 'Unknown')}</p>
                    <p><strong>Emergency Contacts:</strong> ${data.contact_count}</p>
                    <h4 style="margin-top: 1.5rem;">Contact List:</h4>
                    ${contactsHtml}
                </div>
            `);
        })
        .catch(error => {
            console.error('Error loading user details:', error);
            showError('Error loading user details');
        });
}

function deleteUser(username) {
    if (!confirm(`Are you sure you want to delete user "${username}"? This action cannot be undone.`)) {
        return;
    }
    
    secureFetch(`/api/admin/delete_user/${username}`, { 
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to delete user');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showSuccess(`User "${username}" has been deleted successfully`);
            // Reload the page to update the user list
            setTimeout(() => {
                location.reload();
            }, 1500);
        }
    })
    .catch(error => {
        console.error('Error deleting user:', error);
        showError('Failed to delete user');
    });
}

// System Monitoring
function initializeSystemMonitoring() {
    loadSystemStats();
}

function loadSystemStats() {
    secureFetch('/api/admin/system_stats')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch system stats');
            }
            return response.json();
        })
        .then(data => {
            const threatLevelEl = document.getElementById('system-threat-level');
            const threatScoreEl = document.getElementById('system-threat-score');
            
            if (threatLevelEl) threatLevelEl.textContent = data.current_threat_level || 'UNKNOWN';
            if (threatScoreEl) threatScoreEl.textContent = (data.current_threat_score || 0).toFixed(2);
            
            // Update recent events
            const eventsContainer = document.getElementById('recent-events');
            if (eventsContainer && data.recent_events && data.recent_events.length > 0) {
                eventsContainer.innerHTML = data.recent_events.slice().reverse().map(event => {
                    const severity = event.state ? event.state.toLowerCase() : 'info';
                    return `
                        <div class="event-item ${severity}">
                            <strong>${escapeHtml(event.state || 'Event')}</strong> - Score: ${(event.score || 0).toFixed(2)}<br>
                            <small>${new Date(event.timestamp).toLocaleString()}</small>
                        </div>
                    `;
                }).join('');
            } else if (eventsContainer) {
                eventsContainer.innerHTML = '<p class="loading-text">No recent events</p>';
            }
        })
        .catch(error => {
            console.error('Error loading system stats:', error);
            const eventsContainer = document.getElementById('recent-events');
            if (eventsContainer) {
                eventsContainer.innerHTML = '<p class="error-text">Failed to load system stats</p>';
            }
        });
}

// Modal Functions
function showModal(title, content) {
    const modal = document.getElementById('user-modal');
    const modalBody = document.getElementById('user-modal-body');
    
    if (!modal || !modalBody) return;
    
    modalBody.innerHTML = content;
    modal.classList.add('show');
    
    // Close button
    const closeBtn = document.querySelector('.modal-close');
    if (closeBtn) {
        closeBtn.onclick = function() {
            modal.classList.remove('show');
        };
    }
    
    // Close on outside click
    modal.onclick = function(e) {
        if (e.target === modal) {
            modal.classList.remove('show');
        }
    };
    
    // ESC key to close
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            modal.classList.remove('show');
        }
    });
}

function showError(message) {
    showNotification(message, 'error');
}

function showSuccess(message) {
    showNotification(message, 'success');
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'check-circle'}"></i>
        <span>${escapeHtml(message)}</span>
    `;
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => notification.classList.add('show'), 100);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 5000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Cleanup function
window.addEventListener('beforeunload', function() {
    if (detectabilityRefreshInterval) {
        clearInterval(detectabilityRefreshInterval);
    }
    if (systemMonitoringInterval) {
        clearInterval(systemMonitoringInterval);
    }
});

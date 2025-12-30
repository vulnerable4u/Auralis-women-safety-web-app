/**
 * Admin Login JavaScript
 * Handles admin login form validation and submission
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeAdminLogin();
});

function initializeAdminLogin() {
    const loginForm = document.querySelector('.login-form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const submitBtn = document.querySelector('.login-btn');

    if (!loginForm) return;

    // Form validation
    loginForm.addEventListener('submit', function(e) {
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        // Validate inputs
        if (!username || !password) {
            e.preventDefault();
            showError('Please enter both username and password');
            return;
        }

        // Basic client-side validation only
        if (username.length < 3 || password.length < 3) {
            e.preventDefault();
            showError('Username and password must be at least 3 characters long');
            return;
        }

        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging in...';
    });

    // Auto-focus username field
    if (usernameInput) {
        usernameInput.focus();
    }

    // Enter key navigation
    if (usernameInput && passwordInput) {
        usernameInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                passwordInput.focus();
            }
        });
    }
}

function showError(message) {
    // Remove existing error messages
    const existingError = document.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }

    // Create new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;

    // Insert before form
    const loginForm = document.querySelector('.login-form');
    loginForm.parentNode.insertBefore(errorDiv, loginForm);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 5000);
}

/**
 * Onboarding JavaScript
 * Emergency Contact Setup - Modern UI with Theme Support
 */

(function() {
    'use strict';

    // Configuration
    const CONFIG = {
        minimumContacts: 4,
        phoneDigits: 10,
        phonePattern: /^[6-9]\d{9}$/
    };

    // State
    let state = {
        contactCounter: 0,
        isSubmitting: false
    };

    // DOM Elements
    const elements = {};

    /**
     * Initialize the application
     */
    function init() {
        cacheElements();
        bindEvents();
        addInitialContact();
        updateUI();
    }

    /**
     * Cache DOM elements
     */
    function cacheElements() {
        elements.form = document.getElementById('contacts-form');
        elements.contactsContainer = document.getElementById('contacts-container');
        elements.addContactBtn = document.getElementById('add-contact-btn');
        elements.submitBtn = document.getElementById('submit-btn');
        elements.contactCount = document.getElementById('contact-count');
        elements.contactMin = document.getElementById('contact-min');
        elements.validationBox = document.getElementById('validation-box');
        elements.validationText = document.getElementById('validation-text');
        elements.loadingOverlay = document.getElementById('loading-overlay');
        elements.contactTemplate = document.getElementById('contact-template');
    }

    /**
     * Bind event listeners
     */
    function bindEvents() {
        if (elements.addContactBtn) {
            elements.addContactBtn.addEventListener('click', addContact);
        }

        if (elements.form) {
            elements.form.addEventListener('submit', handleSubmit);
        }

        // Input validation with delegation
        if (elements.contactsContainer) {
            elements.contactsContainer.addEventListener('input', handleInput);
            elements.contactsContainer.addEventListener('change', handleInput);
        }

        // Remove button delegation
        if (elements.contactsContainer) {
            elements.contactsContainer.addEventListener('click', handleRemoveClick);
        }
    }

    /**
     * Add initial contact
     */
    function addInitialContact() {
        addContact();
    }

    /**
     * Add a new contact card
     */
    function addContact() {
        state.contactCounter++;

        const card = createContactCard(state.contactCounter);
        elements.contactsContainer.appendChild(card);

        // Hide remove button for first 4 mandatory contacts
        const removeBtn = card.querySelector('.btn-remove');
        if (state.contactCounter <= 4 && removeBtn) {
            removeBtn.style.display = 'none';
        }

        // Animate in
        requestAnimationFrame(() => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(10px)';
            requestAnimationFrame(() => {
                card.style.transition = 'all 0.3s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            });
        });

        // Focus first input
        const firstInput = card.querySelector('input[type="text"]');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }

        updateUI();
    }

    /**
     * Create a contact card element
     */
    function createContactCard(index) {
        const template = elements.contactTemplate.content.cloneNode(true);
        const card = template.querySelector('.contact-card');

        // Update contact number
        const numberEl = card.querySelector('.contact-number');
        if (numberEl) {
            numberEl.textContent = index;
        }

        // Hide remove button for first 4 mandatory contacts
        const removeBtn = card.querySelector('.btn-remove');
        if (index <= 4 && removeBtn) {
            removeBtn.style.display = 'none';
        } else if (removeBtn) {
            removeBtn.style.display = 'flex';
        }

        // Update field IDs and names
        const fields = card.querySelectorAll('input, select');
        fields.forEach(field => {
            const name = field.getAttribute('name');
            if (name) {
                field.setAttribute('name', name.replace('{id}', index));
            }
        });

        return card;
    }

    /**
     * Handle remove button click
     */
    function handleRemoveClick(e) {
        const removeBtn = e.target.closest('.btn-remove');
        if (removeBtn) {
            const card = removeBtn.closest('.contact-card');
            removeContact(card);
        }
    }

    /**
     * Remove a contact card
     */
    function removeContact(card) {
        const totalContacts = elements.contactsContainer.children.length;

        // Prevent removing below minimum
        if (totalContacts <= CONFIG.minimumContacts) {
            showValidation('error', `You must have at least ${CONFIG.minimumContacts} emergency contacts.`);
            return;
        }

        // Animate out
        card.style.transition = 'all 0.3s ease';
        card.style.opacity = '0';
        card.style.transform = 'translateX(20px)';

        setTimeout(() => {
            card.remove();
            renumberContacts();
            updateUI();
        }, 300);
    }

    /**
     * Renumber contacts after removal and update remove buttons visibility
     */
    function renumberContacts() {
        const cards = elements.contactsContainer.querySelectorAll('.contact-card');
        cards.forEach((card, index) => {
            const newIndex = index + 1;
            const numberEl = card.querySelector('.contact-number');
            if (numberEl) {
                numberEl.textContent = newIndex;
            }

            // Update remove button visibility
            const removeBtn = card.querySelector('.btn-remove');
            if (removeBtn) {
                if (newIndex <= 4) {
                    removeBtn.style.display = 'none';
                } else {
                    removeBtn.style.display = 'flex';
                }
            }

            // Update field names
            const fields = card.querySelectorAll('input, select');
            fields.forEach(field => {
                const name = field.getAttribute('name');
                if (name && name.includes('[')) {
                    field.setAttribute('name', name.replace(/\[\d+\]/, `[${newIndex}]`));
                }
            });
        });

        state.contactCounter = cards.length;
    }

    /**
     * Handle input changes
     */
    function handleInput(e) {
        // Handle phone input specifically
        if (e.target.type === 'tel') {
            formatPhoneNumber(e.target);
        }
        
        const card = e.target.closest('.contact-card');
        if (card) {
            validateContact(card);
        }

        setTimeout(() => updateUI(), 50);
    }

    /**
     * Format phone number to exactly 10 digits
     */
    function formatPhoneNumber(input) {
        let value = input.value.replace(/\D/g, '');
        
        // Limit to exactly 10 digits
        if (value.length > CONFIG.phoneDigits) {
            value = value.slice(0, CONFIG.phoneDigits);
        }
        
        input.value = value;
    }

    /**
     * Validate a single contact
     */
    function validateContact(card) {
        const required = card.querySelectorAll('[required]');
        let isValid = true;

        required.forEach(field => {
            field.classList.remove('error', 'valid');
            if (!field.value.trim()) {
                isValid = false;
            }
        });

        // Phone validation for India (exactly 10 digits, starts with 6-9)
        const phoneInput = card.querySelector('input[type="tel"]');
        if (phoneInput && phoneInput.value.trim()) {
            const digits = phoneInput.value.replace(/\D/g, '');
            
            // Check if exactly 10 digits and starts with 6-9
            if (digits.length !== CONFIG.phoneDigits || !CONFIG.phonePattern.test(digits)) {
                isValid = false;
            }
        }

        // Email validation (optional field)
        const emailInput = card.querySelector('input[type="email"]');
        if (emailInput && emailInput.value.trim()) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(emailInput.value)) {
                isValid = false;
            }
        }

        // Mark fields
        required.forEach(field => {
            if (field.value.trim()) {
                if (field.type === 'tel') {
                    const digits = field.value.replace(/\D/g, '');
                    if (digits.length === CONFIG.phoneDigits && CONFIG.phonePattern.test(digits)) {
                        field.classList.add('valid');
                    } else {
                        field.classList.add('error');
                        isValid = false;
                    }
                } else {
                    field.classList.add('valid');
                }
            }
        });

        // Update card state
        if (isValid) {
            card.classList.add('completed');
        } else {
            card.classList.remove('completed');
        }

        return isValid;
    }

    /**
     * Update UI elements
     */
    function updateUI() {
        const cards = elements.contactsContainer.querySelectorAll('.contact-card');
        const total = cards.length;
        let valid = 0;

        cards.forEach(card => {
            if (card.classList.contains('completed')) {
                valid++;
            }
        });

        // Update count
        if (elements.contactCount) {
            elements.contactCount.textContent = total;
        }

        // Update validation message
        if (total < CONFIG.minimumContacts) {
            showValidation('warning', `Add ${CONFIG.minimumContacts - total} more contact(s). Minimum ${CONFIG.minimumContacts} required.`);
        } else if (valid < total) {
            showValidation('warning', `${valid} of ${total} contacts complete. Fill all required fields.`);
        } else {
            showValidation('success', `All ${total} contacts are ready!`);
        }

        // Update submit button
        if (elements.submitBtn) {
            elements.submitBtn.disabled = valid < CONFIG.minimumContacts;
        }

        // Update progress steps
        updateProgressSteps(total, valid);
    }

    /**
     * Update progress step indicators
     */
    function updateProgressSteps(total, valid) {
        const steps = document.querySelectorAll('.step');
        if (steps.length >= 3) {
            steps[0].classList.add('active');
            
            if (total >= CONFIG.minimumContacts && valid >= CONFIG.minimumContacts) {
                steps[1].classList.remove('current');
                steps[1].classList.add('active');
                steps[2].classList.add('current');
            } else {
                steps[1].classList.add('current');
                steps[1].classList.remove('active');
                steps[2].classList.remove('current');
            }
        }
    }

    /**
     * Show validation message
     */
    function showValidation(type, message) {
        if (elements.validationBox && elements.validationText) {
            elements.validationBox.className = 'validation-box ' + type;
            elements.validationText.textContent = message;

            const icon = elements.validationBox.querySelector('i');
            if (icon) {
                const icons = {
                    warning: 'fa-circle-info',
                    success: 'fa-circle-check',
                    error: 'fa-circle-exclamation'
                };
                icon.className = icons[type] || 'fa-circle-info';
            }
        }
    }

    /**
     * Handle form submission
     */
    async function handleSubmit(e) {
        e.preventDefault();

        if (state.isSubmitting) return;

        const cards = elements.contactsContainer.querySelectorAll('.contact-card');
        const validContacts = Array.from(cards).filter(c => c.classList.contains('completed'));

        if (validContacts.length < CONFIG.minimumContacts) {
            showValidation('error', `Please complete at least ${CONFIG.minimumContacts} emergency contacts.`);
            return;
        }

        showLoading();

        try {
            const formData = collectFormData();

            const response = await fetch('/api/onboarding/complete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok && result.status === 'success') {
                showSuccess();
            } else {
                throw new Error(result.error || 'Failed to save contacts');
            }
        } catch (error) {
            console.error('Submission error:', error);
            hideLoading();
            showValidation('error', 'Failed to save contacts. Please try again.');
        }
    }

    /**
     * Collect form data
     */
    function collectFormData() {
        const cards = elements.contactsContainer.querySelectorAll('.contact-card');
        const contacts = [];

        cards.forEach((card, index) => {
            const name = card.querySelector(`input[name="contacts[${index + 1}][name]"]`);
            const phone = card.querySelector(`input[name="contacts[${index + 1}][phone]"]`);
            const relationship = card.querySelector(`select[name="contacts[${index + 1}][relationship]"]`);
            const email = card.querySelector(`input[name="contacts[${index + 1}][email]"]`);

            if (name && phone && relationship && name.value && phone.value && relationship.value) {
                contacts.push({
                    name: name.value.trim(),
                    phone: phone.value.trim(),
                    relationship: relationship.value,
                    email: email ? email.value.trim() || null : null,
                    order: index + 1
                });
            }
        });

        return {
            contacts: contacts,
            onboarding_completed: true,
            completed_at: new Date().toISOString()
        };
    }

    /**
     * Show loading state
     */
    function showLoading() {
        state.isSubmitting = true;
        if (elements.submitBtn) elements.submitBtn.disabled = true;
        if (elements.addContactBtn) elements.addContactBtn.disabled = true;
        if (elements.loadingOverlay) elements.loadingOverlay.classList.add('show');
    }

    /**
     * Hide loading state
     */
    function hideLoading() {
        state.isSubmitting = false;
        if (elements.submitBtn) updateUI();
        if (elements.addContactBtn) elements.addContactBtn.disabled = false;
        if (elements.loadingOverlay) elements.loadingOverlay.classList.remove('show');
    }

    /**
     * Show success and redirect
     */
    function showSuccess() {
        const content = elements.loadingOverlay.querySelector('.loading-content');
        if (content) {
            content.innerHTML = `
                <div style="width: 60px; height: 60px; margin: 0 auto 20px; background: var(--bg-success); border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                    <i class="fas fa-check" style="color: var(--accent); font-size: 28px;"></i>
                </div>
                <h3 style="color: var(--accent);">Setup Complete!</h3>
                <p>Your emergency contacts have been saved.</p>
                <p style="margin-top: 1rem; font-size: 0.9rem; color: var(--text-muted);">Redirecting to the main app...</p>
            `;
        }

        setTimeout(() => {
            window.location.href = '/';
        }, 2000);
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const btn = document.getElementById('submit-btn');
            if (btn && !btn.disabled) btn.click();
        }
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            const btn = document.getElementById('add-contact-btn');
            if (btn && !btn.disabled) btn.click();
        }
        // Toggle theme with Ctrl+D or Cmd+D
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            const btn = document.getElementById('theme-toggle');
            if (btn) btn.click();
        }
    });

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();


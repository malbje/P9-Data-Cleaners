/**
 * @fileoverview Main dashboard JavaScript functionality
 * Handles widget interactions, modal system, chatbot, and user authentication
 * @author Data Cleaners Team
 * @version 1.0.0
 */

// ============================================================================
// MAIN APPLICATION INITIALIZATION
// ============================================================================

/**
 * Main application entry point
 * Initializes all dashboard functionality when DOM is ready
 */
document.addEventListener("DOMContentLoaded", () => {
    // Initialize core application components
    loadUserInfo();           // Load and display user authentication status
    initializeModal();        // Set up modal system for widget content
    initializeModeToggle();   // Configure AI/Manual mode switcher

    // ========================================================================
    // WIDGET SYSTEM INITIALIZATION
    // ========================================================================
    
    /**
     * Set up click handlers for all dashboard widgets
     * Each widget card triggers specific functionality when clicked
     */
    const widgets = document.querySelectorAll('.widget-card');
    
    widgets.forEach(widget => {
        widget.addEventListener('click', () => {
            const widgetType = widget.dataset.widget;
            handleWidgetClick(widgetType);
        });
    });

    // ========================================================================
    // WIDGET CLICK HANDLING
    // ========================================================================

    /**
     * Central widget click handler
     * Routes clicks to appropriate widget-specific functions
     * @param {string} widgetType - The type of widget clicked (weather, appointments, etc.)
     */
    function handleWidgetClick(widgetType) {
        switch(widgetType) {
            case 'weather':
                handleWeatherClick();
                break;
            case 'appointments':
                handleAppointmentsClick();
                break;
            case 'addresses':
                handleAddressesClick();
                break;
            case 'profile':
                handleProfileClick();
                break;
            default:
                console.log('Unknown widget type:', widgetType);
        }
    }

    // ========================================================================
    // INDIVIDUAL WIDGET HANDLERS
    // Each widget has its own handler that opens specific content in the modal
    // ========================================================================

    /**
     * Weather widget click handler
     * Displays 7-day cleaning impact forecast
     */
    function handleWeatherClick() {
        console.log('Weather widget clicked');
        openWidget('weather', 'Weather Information', generateWeatherContent());
    }

    /**
     * Appointments widget click handler
     * Shows upcoming cleaning appointments and calendar overview
     */
    function handleAppointmentsClick() {
        loadAppointmentsContent();
    }

    /**
     * Addresses widget click handler
     * Displays saved customer addresses with property details
     */
    function handleAddressesClick() {
        console.log('My Addresses widget clicked');
        openWidget('addresses', 'My Addresses', generateAddressesContent());
    }

    /**
     * Profile widget click handler
     * Opens user profile management interface
     */
    function handleProfileClick() {
        console.log('Profile widget clicked');
        loadUserProfileContent();
    }

    // ========================================================================
    // CHATBOT SYSTEM
    // AI assistant for booking and customer service
    // ========================================================================

    /**
     * Get chatbot interface elements
     * These elements handle user input and message display
     */
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    /**
     * Initialize chatbot form submission handling
     * Processes user messages and generates AI responses
     */
    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const userMessage = chatInput.value.trim();
            
            if (userMessage) {
                // Add user message to chat
                addMessageToChat(userMessage, 'user');
                
                // Clear input
                chatInput.value = '';
                
                // Simulate bot response (you can replace this with actual chatbot logic)
                setTimeout(() => {
                    const botResponse = generateBotResponse(userMessage);
                    addMessageToChat(botResponse, 'bot');
                }, 1000);
            }
        });
    }

    /**
     * Add a message to the chat interface
     * @param {string} message - The message content to display
     * @param {string} sender - Either 'user' or 'bot' for styling
     */
    function addMessageToChat(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    /**
     * Generate automated bot responses based on user input
     * Simple keyword matching for common queries
     * @param {string} userMessage - The user's input message
     * @returns {string} Appropriate bot response
     */
    function generateBotResponse(userMessage) {
        // Simple bot responses - you can enhance this with actual AI/NLP
        const lowerMessage = userMessage.toLowerCase();
        
        if (lowerMessage.includes('booking') || lowerMessage.includes('book')) {
            return 'I can help you book a cleaning! Please provide the customer details and preferred date.';
        } else if (lowerMessage.includes('vejr') || lowerMessage.includes('weather')) {
            return 'For weather information, click on the Vejr widget in the dashboard.';
        } else if (lowerMessage.includes('schedule') || lowerMessage.includes('ugeplan')) {
            return 'To view the weekly schedule, click on the Ugeplan widget.';
        } else if (lowerMessage.includes('appointment')) {
            return 'To see upcoming appointments, click on the Upcoming Appointments widget.';
        } else {
            return 'I\'m here to help with booking and scheduling. What would you like to do?';
        }
    }

    // ========================================================================
    // USER AUTHENTICATION SYSTEM
    // ========================================================================

    /**
     * Load and display user authentication information
     * Fetches user data from the server and updates the UI
     * Redirects to login if user is not authenticated
     */
    async function loadUserInfo() {
        try {
            const response = await fetch('/api/auth/status');
            const data = await response.json();
            
            if (data.logged_in) {
                const userInfo = document.getElementById('user-info');
                if (userInfo) {
                    userInfo.textContent = `Welcome, ${data.user.name}`;
                }
            } else {
                // Redirect to login if not logged in
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('Error loading user info:', error);
            // Redirect to login on error
            window.location.href = '/login';
        }
    }

    // ========================================================================
    // MODAL SYSTEM
    // Handles widget content display in overlay modal
    // ========================================================================

    /**
     * Initialize modal functionality
     * Sets up close button and keyboard shortcuts
     */
    function initializeModal() {
        const closeBtn = document.getElementById('modal-close');
        
        // Close modal when clicking the close button
        closeBtn.addEventListener('click', closeModal);
        
        // Close modal when pressing Escape key
        document.addEventListener('keydown', (e) => {
            const modal = document.getElementById('widget-modal');
            if (e.key === 'Escape' && modal.classList.contains('active')) {
                closeModal();
            }
        });
    }

    /**
     * Open a widget's content in the modal overlay
     * @param {string} widgetType - Type of widget being opened
     * @param {string} title - Modal title to display
     * @param {string} content - HTML content to show in modal
     */
    function openWidget(widgetType, title, content) {
        const modal = document.getElementById('widget-modal');
        const modalTitle = document.getElementById('modal-title');
        const modalBody = document.getElementById('modal-body');
        const widgetGrid = document.getElementById('widget-grid');
        
        modalTitle.textContent = title;
        modalBody.innerHTML = content;
        
        // Hide widget grid and show modal
        widgetGrid.style.display = 'none';
        modal.classList.add('active');
    }

    /**
     * Close the modal and return to widget grid view
     */
    function closeModal() {
        const modal = document.getElementById('widget-modal');
        const widgetGrid = document.getElementById('widget-grid');
        
        modal.classList.remove('active');
        
        // Show widget grid again
        widgetGrid.style.display = 'grid';
    }

    // ========================================================================
    // WIDGET CONTENT GENERATORS
    // Functions that create HTML content for each widget type
    // ========================================================================

    /**
     * Generate weather widget content
     * Creates a 7-day forecast focused on cleaning impact
     * Shows how weather conditions affect dirt tracking and cleaning needs
     * @returns {string} HTML content for weather widget modal
     */
    function generateWeatherContent() {
        return `
            <div class="weather-info">
                <div class="weather-forecast">
                    <h4>7-Day Forecast - Cleaning Impact</h4>
                    <div class="forecast-day clean">
                        <div class="day-card">
                            <div class="date">Oct 19th</div>
                            <div class="day-name">Today</div>
                            <div class="weather-icon">☁️</div>
                            <div class="impact-level low">Low Mess</div>
                            <div class="impact-desc">Dry conditions - minimal dirt tracking</div>
                        </div>
                    </div>
                    <div class="forecast-day messy">
                        <div class="day-card">
                            <div class="date">Oct 20th</div>
                            <div class="day-name">Tomorrow</div>
                            <div class="weather-icon">🌧️</div>
                            <div class="impact-level high">High Mess</div>
                            <div class="impact-desc">Rain - muddy shoes, wet coats</div>
                        </div>
                    </div>
                    <div class="forecast-day clean">
                        <div class="day-card">
                            <div class="date">Oct 21st</div>
                            <div class="day-name">Friday</div>
                            <div class="weather-icon">🌞</div>
                            <div class="impact-level low">Low Mess</div>
                            <div class="impact-desc">Sunny & dry - clean conditions</div>
                        </div>
                    </div>
                    <div class="forecast-day clean">
                        <div class="day-card">
                            <div class="date">Oct 22nd</div>
                            <div class="day-name">Saturday</div>
                            <div class="weather-icon">⛅</div>
                            <div class="impact-level low">Low Mess</div>
                            <div class="impact-desc">Partly cloudy - good conditions</div>
                        </div>
                    </div>
                    <div class="forecast-day messy">
                        <div class="day-card">
                            <div class="date">Oct 23rd</div>
                            <div class="day-name">Sunday</div>
                            <div class="weather-icon">🌧️</div>
                            <div class="impact-level high">High Mess</div>
                            <div class="impact-desc">Heavy rain - very muddy conditions</div>
                        </div>
                    </div>
                    <div class="forecast-day messy">
                        <div class="day-card">
                            <div class="date">Oct 24th</div>
                            <div class="day-name">Monday</div>
                            <div class="weather-icon">❄️</div>
                            <div class="impact-level medium">Medium Mess</div>
                            <div class="impact-desc">Snow - wet boots, salt residue</div>
                        </div>
                    </div>
                    <div class="forecast-day clean">
                        <div class="day-card">
                            <div class="date">Oct 25th</div>
                            <div class="day-name">Tuesday</div>
                            <div class="weather-icon">🌞</div>
                            <div class="impact-level low">Low Mess</div>
                            <div class="impact-desc">Clear & cold - dry conditions</div>
                        </div>
                    </div>
                </div>
            </div>
            <style>
                .weather-forecast h4 { margin-bottom: 0.8em; color: #333; font-size: 1em; }
                .forecast-day { 
                    margin: 0.25em 0; 
                }
                .day-card {
                    display: flex; 
                    flex-direction: column;
                    align-items: center;
                    text-align: center;
                    padding: 0.6em; 
                    background-color: #f8f9fa; 
                    border-radius: 8px; 
                    border-left: 3px solid #28a745;
                    gap: 0.3em;
                }
                .forecast-day.messy .day-card { 
                    border-left-color: #dc3545;
                }
                .forecast-day.clean .day-card { 
                    border-left-color: #28a745;
                }
                .date { 
                    font-size: 0.75em; 
                    color: #666; 
                    font-weight: bold;
                }
                .day-name { 
                    font-size: 0.85em; 
                    color: #333; 
                    font-weight: bold;
                }
                .weather-icon { 
                    font-size: 1.5em; 
                    margin: 0.2em 0;
                }
                .impact-level { 
                    font-weight: bold; 
                    font-size: 0.65em;
                    padding: 0.1em 0.3em;
                    border-radius: 6px;
                    display: inline-block;
                    width: fit-content;
                }
                .impact-level.low { 
                    background-color: #d4edda; 
                    color: #155724; 
                }
                .impact-level.medium { 
                    background-color: #fff3cd; 
                    color: #856404; 
                }
                .impact-level.high { 
                    background-color: #f8d7da; 
                    color: #721c24; 
                }
                .impact-desc { 
                    font-size: 0.6em; 
                    color: #666; 
                    font-style: italic;
                }

            </style>
        `;
    }
    
    async function generateHomeContent() {
        // This function now fetches and displays user addresses and preferences.
        let content = '<h3>Your Registered Addresses</h3>';
        
        try {
            // Fetch from the new endpoint defined in app.py
            const response = await fetch('/api/user/addresses-with-preferences');
            const addresses = await response.json();
            
            if (addresses.length > 0) {
                content += '<div class="address-list">';
                content += addresses.map(addr => `
                    <div class="address-card">
                        <div class="address-header">
                            <h4>📍 ${addr.street_and_number}, ${addr.postal_code} ${addr.city_name}</h4>
                        </div>
                        <div class="address-preferences">
                            <h5>Preferences:</h5>
                            <ul>
                                <li><strong>Allergies:</strong> ${addr.allergies || 'None specified'}</li>
                                <li><strong>Pets:</strong> ${addr.pets || 'None specified'}</li>
                                <li><strong>Kids:</strong> ${addr.kids || 'None specified'}</li>
                                <li><strong>Size:</strong> ${addr.square_footage ? `${addr.square_footage} m²` : 'Not specified'}</li>
                                <li><strong>Notes:</strong> ${addr.preference_notes || 'None'}</li>
                            </ul>
                        </div>
                    </div>
                `).join('');
                content += '</div>';
            } else {
                content += '<p>You have no registered addresses.</p>';
            }
        } catch (error) {
            console.error("Could not load addresses:", error);
            content += '<p>Error loading addresses.</p>';
        }

        return `
            <div class="address-widget-content">
                ${content}
            </div>
            <style>
                .address-list { display: grid; gap: 1.5em; }
                .address-card { background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 12px; overflow: hidden; }
                .address-header { background-color: #007bff; color: white; padding: 0.75em 1.25em; }
                .address-header h4 { margin: 0; font-size: 1.1em; }
                .address-preferences { padding: 1.25em; }
                .address-preferences h5 { margin-top: 0; margin-bottom: 0.75em; color: #333; }
                .address-preferences ul { list-style: none; padding: 0; margin: 0; }
                .address-preferences li { padding: 0.4em 0; border-bottom: 1px solid #eee; }
                .address-preferences li:last-child { border-bottom: none; }
            </style>
        `;
    }
    
    async function loadAppointmentsContent() {
        try {
            const response = await fetch('/api/appointments');
            if (!response.ok) {
                openWidget('appointments', 'Upcoming Appointments', '<p>Could not load appointments.</p>');
                return;
            }
            const appointments = await response.json();
            
            let content = '<h3>Your Upcoming Appointments</h3>';
            if (appointments.length > 0) {
                content += '<div class="appointments-list">';
                content += appointments.map(appt => `
                    <div class="appointment-card">
                        <div class="appointment-date">
                            <span>${new Date(appt.date).toLocaleString('en-US', { month: 'short' })}</span>
                            <strong>${new Date(appt.date).getDate()}</strong>
                        </div>
                        <div class="appointment-details">
                            <p><strong>${appt.service_names || 'General Cleaning'}</strong> at ${appt.time.slice(0, 5)}</p>
                            <p class="address">📍 ${appt.address}</p>
                            ${appt.notes ? `<p class="notes">Notes: ${appt.notes}</p>` : ''}
                        </div>
                    </div>
                </div>
            </div>
            <style>
                .home-info { padding: 1em; }
                .addresses-list { margin-top: 1em; }
                .address-card { margin-bottom: 2em; padding: 1.5em; background-color: #f8f9fa; border-radius: 12px; border-left: 5px solid #28a745; }
                .address-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1em; }
                .address-header h4 { margin: 0; color: #333; font-size: 1.3em; }
                .address-type { background-color: #28a745; color: white; padding: 0.25em 0.75em; border-radius: 12px; font-size: 0.8em; font-weight: bold; }
                .address-text { font-size: 1.1em; margin-bottom: 1.5em; color: #555; }
                .specifications, .preferences { margin-bottom: 1.5em; }
                .specifications h5, .preferences h5 { margin: 0 0 1em 0; color: #333; font-size: 1.1em; border-bottom: 2px solid #28a745; padding-bottom: 0.5em; }
                .spec-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.75em; }
                .spec-item { display: flex; justify-content: space-between; padding: 0.5em; background-color: white; border-radius: 6px; }
                .spec-label { font-weight: bold; color: #666; }
                .spec-value { color: #333; }
                .pref-list { display: flex; flex-direction: column; gap: 0.5em; }
                .pref-item { padding: 0.75em; background-color: white; border-radius: 6px; color: #333; }
            </style>
        `;
    }

    /**
     * Load user profile content asynchronously
     * Fetches current user data and generates profile widget content
     * Handles authentication errors gracefully
     */
    async function loadUserProfileContent() {
        try {
            const response = await fetch('/api/auth/status');
            const data = await response.json();
            if (data.logged_in) {
                const user = data.user;
                const profileContent = generateProfileContent(user);
                openWidget('profile', 'My Profile', profileContent);

                // Add event listener AFTER the content is in the DOM
                const toggle = document.getElementById('notification-toggle');
                if (toggle) {
                    toggle.addEventListener('change', (event) => {
                        const statusSpan = document.querySelector('.setting-status');
                        if (event.target.checked) {
                            statusSpan.textContent = 'YES';
                        } else {
                            statusSpan.textContent = 'NO';
                        }
                    });
                }
            } else {
                openWidget('profile', 'My Profile', '<p>Please log in to view your profile.</p>');
            }
        } catch (error) {
            console.error('Error loading profile:', error);
            openWidget('profile', 'My Profile', '<p>Error loading profile information.</p>');
        }
    }

    /**
     * Generate user profile widget content
     * Creates a comprehensive profile interface with personal info and settings
     * @param {Object} user - User data object from authentication API
     * @returns {string} HTML content for profile widget modal
     */
    function generateProfileContent(user) {
        // Split the full name from the user object into first and last names
        const nameParts = user.name ? user.name.split(' ') : ['User'];
        const firstName = nameParts.shift() || '';
        const lastName = nameParts.join(' ') || '';

        // Generate user initials for the avatar from the first name
        const initials = firstName ? firstName.charAt(0).toUpperCase() : 'U';
        
        // Determine notification settings from user data
        const notificationPreference = user.notification_preference || 'none';
        const notificationsEnabled = notificationPreference !== 'none';
        const isChecked = notificationsEnabled ? 'checked' : '';
        const statusText = notificationsEnabled ? 'YES' : 'NO';

        return `
            <div class="profile-info">
                <div class="profile-avatar">
                    <div class="avatar-circle">${initials}</div>
                    <h3>${user.name || 'User'}</h3>
                </div>
                
                <div class="profile-section">
                    <h3>Personal Information</h3>
                    <div class="profile-field">
                        <span class="label">First Name:</span>
                        <span class="value">${firstName}</span>
                    </div>
                    <div class="profile-field">
                        <span class="label">Last Name:</span>
                        <span class="value">${lastName}</span>
                    </div>
                    <div class="profile-field">
                        <span class="label">Email:</span>
                        <span class="value">${user.email || 'No email provided'}</span>
                    </div>
                </div>
                
                <div class="profile-section">
                    <h3>Notification Settings</h3>
                    <div class="setting-row">
                        <span class="setting-label">Notifications Enabled:</span>
                        <div class="toggle-container">
                            <label class="toggle-switch">
                                <input type="checkbox" id="notification-toggle" ${isChecked}>
                                <span class="slider"></span>
                            </label>
                            <span class="setting-status">${statusText}</span>
                        </div>
                    </div>
                    <div class="setting-row">
                        <span class="setting-label">Reminder Time:</span>
                        <span class="setting-value">${notificationPreference}</span>
                    </div>
                </div>
                
                <div class="profile-section">
                    <h3>Quick Actions</h3>
                    <div class="action-buttons">
                        <button class="action-btn primary" onclick="alert('Edit profile functionality coming soon!')">Edit Profile</button>
                        <button class="action-btn secondary" onclick="alert('Change password functionality coming soon!')">Change Password</button>
                        <button class="action-btn success" onclick="alert('Save settings functionality coming soon!')">Save Settings</button>
                    </div>
                </div>
            </div>
            <style>
                .profile-info { padding: 1em; }
                .profile-avatar { text-align: center; margin-bottom: 2em; }
                .avatar-circle { width: 80px; height: 80px; border-radius: 50%; background-color: #007bff; color: white; display: flex; align-items: center; justify-content: center; font-size: 2em; font-weight: bold; margin: 0 auto 1em; }
                .profile-section { margin-bottom: 2em; padding: 1.5em; background-color: #f8f9fa; border-radius: 12px; }
                .profile-section h3 { margin: 0 0 1em 0; color: #333; border-bottom: 2px solid #007bff; padding-bottom: 0.5em; }
                .profile-field, .setting-row { display: flex; justify-content: space-between; align-items: center; padding: 0.75em 0; border-bottom: 1px solid #e9ecef; }
                .profile-field:last-child, .setting-row:last-child { border-bottom: none; }
                .profile-field .label, .setting-label { font-weight: bold; color: #666; }
                .profile-field .value, .setting-value { color: #333; text-transform: capitalize; }
                .toggle-container { display: flex; align-items: center; gap: 0.5em; }
                .toggle-switch { position: relative; display: inline-block; width: 50px; height: 24px; }
                .toggle-switch input { opacity: 0; width: 0; height: 0; }
                .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 24px; }
                .slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background-color: white; transition: .4s; border-radius: 50%; }
                input:checked + .slider { background-color: #007bff; }
                input:checked + .slider:before { transform: translateX(26px); }
                .setting-status { font-weight: bold; }
                .action-buttons { display: flex; gap: 1em; flex-wrap: wrap; }
                .action-btn { padding: 0.75em 1.5em; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; transition: background-color 0.3s; }
                .action-btn.primary { background-color: #007bff; color: white; }
                .action-btn.secondary { background-color: #6c757d; color: white; }
                .action-btn.success { background-color: #28a745; color: white; }
                .action-btn:hover { opacity: 0.9; }
            </style>
        `;
    }

    // ========================================================================
    // MODE TOGGLE SYSTEM
    // Switches between AI Assistant mode and Manual booking mode
    // ========================================================================

    /**
     * Initialize the mode toggle button
     * Sets the initial state to AI mode (dashboard)
     */
    function initializeModeToggle() {
        // Set initial state to AI Mode (dashboard)
        updateModeButton('ai');
    }

    /**
     * Update the mode toggle button appearance and text
     * @param {string} mode - Either 'ai' or 'manual' mode
     */
    function updateModeButton(mode) {
        const button = document.getElementById('mode-toggle-btn');
        const modeText = button.querySelector('.mode-text');
        
        if (mode === 'ai') {
            modeText.textContent = 'Manual Mode';
            button.classList.add('active');
        } else {
            modeText.textContent = 'AI Mode';
            button.classList.remove('active');
        }
    }
});

// ============================================================================
// GLOBAL FUNCTIONS
// Functions that need to be accessible from HTML onclick attributes
// ============================================================================

/**
 * Global function for mode toggle button
 * Switches between AI Assistant dashboard and Manual booking interface
 * Called directly from HTML onclick attribute
 */
function toggleMode() {
    const button = document.getElementById('mode-toggle-btn');
    const modeText = button.querySelector('.mode-text');
    
    if (modeText.textContent === 'Manual Mode') {
        // Switch to Manual Mode
        window.location.href = '/manual';
    } else {
        // Switch to AI Mode (Dashboard)
        window.location.href = '/';
    }
}
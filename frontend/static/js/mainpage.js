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
        console.log('Appointments widget clicked');
        openWidget('appointments', 'Upcoming Appointments', generateAppointmentsContent());
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

    /**
     * Generate appointments widget content
     * Shows upcoming cleaning appointments and calendar overview
     * Includes interactive calendar for the current month
     * @returns {string} HTML content for appointments widget modal
     */
    function generateAppointmentsContent() {
        return `
            <div class="appointments-info">
                <div class="upcoming-section">
                    <h3>Next Appointments</h3>
                    <div class="no-appointments">
                        <div class="no-appointments-icon">📅</div>
                        <h4>No Upcoming Appointments</h4>
                        <p>You don't have any cleaning appointments scheduled at the moment.</p>
                        <p class="suggestion">Book a new appointment using the chatbot or manual mode!</p>
                    </div>
                </div>
                
                <div class="calendar-section">
                    <h3>Calendar Overview</h3>
                    <div class="mini-calendar">
                        <div class="calendar-header">
                            <button class="nav-btn">&lt;</button>
                            <span class="month-year">October 2025</span>
                            <button class="nav-btn">&gt;</button>
                        </div>
                        <div class="calendar-grid">
                            <div class="day-header">Mon</div>
                            <div class="day-header">Tue</div>
                            <div class="day-header">Wed</div>
                            <div class="day-header">Thu</div>
                            <div class="day-header">Fri</div>
                            <div class="day-header">Sat</div>
                            <div class="day-header">Sun</div>
                            
                            <div class="calendar-day empty"></div>
                            <div class="calendar-day empty"></div>
                            <div class="calendar-day">1</div>
                            <div class="calendar-day">2</div>
                            <div class="calendar-day">3</div>
                            <div class="calendar-day">4</div>
                            <div class="calendar-day">5</div>
                            <div class="calendar-day">6</div>
                            <div class="calendar-day">7</div>
                            <div class="calendar-day">8</div>
                            <div class="calendar-day">9</div>
                            <div class="calendar-day">10</div>
                            <div class="calendar-day">11</div>
                            <div class="calendar-day">12</div>
                            <div class="calendar-day">13</div>
                            <div class="calendar-day">14</div>
                            <div class="calendar-day">15</div>
                            <div class="calendar-day">16</div>
                            <div class="calendar-day">17</div>
                            <div class="calendar-day">18</div>
                            <div class="calendar-day today">19</div>
                            <div class="calendar-day">20</div>
                            <div class="calendar-day">21</div>
                            <div class="calendar-day">22</div>
                            <div class="calendar-day">23</div>
                            <div class="calendar-day">24</div>
                            <div class="calendar-day">25</div>
                            <div class="calendar-day">26</div>
                            <div class="calendar-day">27</div>
                            <div class="calendar-day">28</div>
                            <div class="calendar-day">29</div>
                            <div class="calendar-day">30</div>
                            <div class="calendar-day">31</div>
                        </div>
                    </div>
                </div>
            </div>
            <style>
                .appointments-info { padding: 1em; }
                .upcoming-section { margin-bottom: 2em; }
                .appointment-item { padding: 1em; margin: 0.5em 0; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #007bff; }
                .appointment-time { font-weight: bold; color: #007bff; margin-bottom: 0.5em; }
                .appointment-title { font-size: 1.1em; margin-bottom: 0.25em; }
                .appointment-location { color: #666; font-size: 0.9em; }
                .no-appointments { text-align: center; padding: 2em; background-color: #f8f9fa; border-radius: 12px; border: 2px dashed #dee2e6; }
                .no-appointments-icon { font-size: 3em; margin-bottom: 0.5em; }
                .no-appointments h4 { margin: 0.5em 0; color: #333; font-size: 1.2em; }
                .no-appointments p { margin: 0.5em 0; color: #666; }
                .no-appointments .suggestion { color: #007bff; font-weight: 500; margin-top: 1em; }
                .calendar-section h3 { margin-bottom: 1em; }
                .mini-calendar { background-color: #fff; border-radius: 8px; padding: 1em; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .calendar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1em; }
                .nav-btn { background: none; border: none; font-size: 1.2em; cursor: pointer; padding: 0.25em 0.5em; }
                .month-year { font-weight: bold; }
                .calendar-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 0.25em; }
                .day-header { text-align: center; font-weight: bold; padding: 0.5em; color: #666; font-size: 0.8em; }
                .calendar-day { text-align: center; padding: 0.5em; cursor: pointer; border-radius: 4px; }
                .calendar-day:hover { background-color: #e9ecef; }
                .calendar-day.today { background-color: #007bff; color: white; font-weight: bold; }
                .calendar-day.has-appointment { background-color: #ffc107; color: #333; font-weight: bold; }
                .calendar-day.empty { cursor: default; }
                .calendar-day.empty:hover { background-color: transparent; }
            </style>
        `;
    }

    /**
     * Generate addresses widget content
     * Displays saved customer addresses with detailed property information
     * Includes specifications and preferences for each property
     * @returns {string} HTML content for addresses widget modal
     */
    function generateAddressesContent() {
        return `
            <div class="home-info">
                <h3>Saved Addresses</h3>
                <div class="addresses-list">
                    <div class="address-card">
                        <div class="address-header">
                            <h4>Primary Home</h4>
                            <span class="address-type">Main Residence</span>
                        </div>
                        <div class="address-details">
                            <p class="address-text">📍 Nørrebrogade 123, 2200 Copenhagen N, Denmark</p>
                            <div class="specifications">
                                <h5>Specifications</h5>
                                <div class="spec-grid">
                                    <div class="spec-item">
                                        <span class="spec-label">Bedrooms:</span>
                                        <span class="spec-value">3</span>
                                    </div>
                                    <div class="spec-item">
                                        <span class="spec-label">Bathrooms:</span>
                                        <span class="spec-value">2</span>
                                    </div>
                                    <div class="spec-item">
                                        <span class="spec-label">Size:</span>
                                        <span class="spec-value">120 m²</span>
                                    </div>
                                    <div class="spec-item">
                                        <span class="spec-label">Year Built:</span>
                                        <span class="spec-value">1985</span>
                                    </div>
                                </div>
                            </div>
                            <div class="preferences">
                                <h5>Preferences</h5>
                                <div class="pref-list">
                                    <div class="pref-item">Smart thermostat: 21°C</div>
                                    <div class="pref-item">Security system: Armed at night</div>
                                    <div class="pref-item">Lighting: Auto at sunset</div>
                                    <div class="pref-item">Smart outlets: Schedule enabled</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="address-card">
                        <div class="address-header">
                            <h4>Summer House</h4>
                            <span class="address-type">Vacation Home</span>
                        </div>
                        <div class="address-details">
                            <p class="address-text">📍 Strandvejen 45, 9990 Skagen, Denmark</p>
                            <div class="specifications">
                                <h5>Specifications</h5>
                                <div class="spec-grid">
                                    <div class="spec-item">
                                        <span class="spec-label">Bedrooms:</span>
                                        <span class="spec-value">2</span>
                                    </div>
                                    <div class="spec-item">
                                        <span class="spec-label">Bathrooms:</span>
                                        <span class="spec-value">1</span>
                                    </div>
                                    <div class="spec-item">
                                        <span class="spec-label">Size:</span>
                                        <span class="spec-value">80 m²</span>
                                    </div>
                                    <div class="spec-item">
                                        <span class="spec-label">Year Built:</span>
                                        <span class="spec-value">1962</span>
                                    </div>
                                </div>
                            </div>
                            <div class="preferences">
                                <h5>Preferences</h5>
                                <div class="pref-list">
                                    <div class="pref-item">Heating: 18°C minimum</div>
                                    <div class="pref-item">Garden sprinkler: Weekends only</div>
                                    <div class="pref-item">Security: Motion detection</div>
                                    <div class="pref-item">Beach access: Private path</div>
                                </div>
                            </div>
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
            } else {
                openWidget('profile', 'My Profile', '<p>Unable to load profile information.</p>');
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
        // Generate user initials for avatar
        const initials = user.name ? user.name.split(' ').map(n => n[0]).join('').toUpperCase() : 'U';
        
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
                        <span class="value">John</span>
                    </div>
                    <div class="profile-field">
                        <span class="label">Last Name:</span>
                        <span class="value">Doe</span>
                    </div>
                    <div class="profile-field">
                        <span class="label">Email:</span>
                        <span class="value">${user.email || 'john.doe@email.com'}</span>
                    </div>
                </div>
                
                <div class="profile-section">
                    <h3>Notification Settings</h3>
                    <div class="notification-setting">
                        <div class="setting-row">
                            <span class="setting-label">Notifications:</span>
                            <div class="toggle-container">
                                <label class="toggle-switch">
                                    <input type="checkbox" checked>
                                    <span class="slider"></span>
                                </label>
                                <span class="setting-status">On</span>
                            </div>
                        </div>
                        <div class="setting-row">
                            <span class="setting-label">Notification Type:</span>
                            <div class="select-container">
                                <select class="setting-select">
                                    <option value="email" selected>Email</option>
                                    <option value="sms">SMS</option>
                                    <option value="push">Push Notification</option>
                                </select>
                            </div>
                        </div>
                        <div class="setting-row">
                            <span class="setting-label">Notification Time:</span>
                            <div class="time-container">
                                <input type="time" class="setting-time" value="09:00">
                            </div>
                        </div>
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
                .profile-field { display: flex; justify-content: space-between; align-items: center; padding: 0.75em 0; border-bottom: 1px solid #e9ecef; }
                .profile-field:last-child { border-bottom: none; }
                .profile-field .label { font-weight: bold; color: #666; }
                .profile-field .value { color: #333; }
                .notification-setting { }
                .setting-row { display: flex; justify-content: space-between; align-items: center; padding: 1em 0; border-bottom: 1px solid #e9ecef; }
                .setting-row:last-child { border-bottom: none; }
                .setting-label { font-weight: bold; color: #666; }
                .toggle-container { display: flex; align-items: center; gap: 0.5em; }
                .toggle-switch { position: relative; display: inline-block; width: 50px; height: 24px; }
                .toggle-switch input { opacity: 0; width: 0; height: 0; }
                .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; transition: .4s; border-radius: 24px; }
                .slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background-color: white; transition: .4s; border-radius: 50%; }
                input:checked + .slider { background-color: #007bff; }
                input:checked + .slider:before { transform: translateX(26px); }
                .setting-status { color: #28a745; font-weight: bold; }
                .select-container, .time-container { }
                .setting-select, .setting-time { padding: 0.5em; border: 1px solid #ddd; border-radius: 4px; background-color: white; }
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
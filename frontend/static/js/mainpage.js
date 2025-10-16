// static/js/mainpage.js

document.addEventListener("DOMContentLoaded", () => {
    // Load user information
    loadUserInfo();
    
    // Initialize modal functionality
    initializeModal();
    
    // Initialize mode toggle
    initializeModeToggle();
    
    // Widget click handlers
    const widgets = document.querySelectorAll('.widget-card');
    
    widgets.forEach(widget => {
        widget.addEventListener('click', () => {
            const widgetType = widget.dataset.widget;
            handleWidgetClick(widgetType);
        });
    });
    
    // Function to handle widget clicks
    function handleWidgetClick(widgetType) {
        switch(widgetType) {
            case 'weather':
                handleWeatherClick();
                break;
            case 'appointments':
                handleAppointmentsClick();
                break;
            case 'home':
                handleHomeClick();
                break;
            case 'profile':
                handleProfileClick();
                break;
            default:
                console.log('Unknown widget type:', widgetType);
        }
    }
    
    // Individual widget handlers
    function handleWeatherClick() {
        console.log('Weather widget clicked');
        openWidget('weather', 'Weather Information', generateWeatherContent());
    }
    
    function handleAppointmentsClick() {
        loadAppointmentsContent();
    }
    
    async function handleHomeClick() {
        const homeContent = await generateHomeContent();
        openWidget('home', 'Home Dashboard', homeContent);
    }
    
    function handleProfileClick() {
        console.log('Profile widget clicked');
        loadUserProfileContent();
    }
    
    // Chatbot functionality
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    
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
    
    function addMessageToChat(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
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
    
    // Load user information
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
    
    // Modal functionality
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
    
    function closeModal() {
        const modal = document.getElementById('widget-modal');
        const widgetGrid = document.getElementById('widget-grid');
        
        modal.classList.remove('active');
        
        // Show widget grid again
        widgetGrid.style.display = 'grid';
    }
    
    // Widget content generators
    function generateWeatherContent() {
        return `
            <div class="weather-info">
                <div class="weather-current">
                    <div class="weather-temp">22°C</div>
                    <div class="weather-desc">Partly Cloudy</div>
                    <div>Copenhagen, Denmark</div>
                </div>
                <div class="weather-details">
                    <div class="detail-row">
                        <span>Humidity:</span>
                        <span>65%</span>
                    </div>
                    <div class="detail-row">
                        <span>Wind:</span>
                        <span>12 km/h</span>
                    </div>
                    <div class="detail-row">
                        <span>Pressure:</span>
                        <span>1013 hPa</span>
                    </div>
                </div>
                <div class="weather-forecast">
                    <h4>5-Day Forecast</h4>
                    <div class="forecast-day">
                        <div><strong>Today</strong></div>
                        <div>☁️</div>
                        <div>22°/16°</div>
                    </div>
                    <div class="forecast-day">
                        <div><strong>Tomorrow</strong></div>
                        <div>🌧️</div>
                        <div>18°/12°</div>
                    </div>
                    <div class="forecast-day">
                        <div><strong>Friday</strong></div>
                        <div>🌞</div>
                        <div>25°/18°</div>
                    </div>
                    <div class="forecast-day">
                        <div><strong>Saturday</strong></div>
                        <div>⛅</div>
                        <div>23°/16°</div>
                    </div>
                    <div class="forecast-day">
                        <div><strong>Sunday</strong></div>
                        <div>🌞</div>
                        <div>24°/17°</div>
                    </div>
                </div>
            </div>
            <style>
                .weather-current { text-align: center; margin-bottom: 2em; }
                .weather-temp { font-size: 3em; font-weight: bold; color: #007bff; }
                .weather-desc { font-size: 1.2em; margin: 0.5em 0; color: #666; }
                .weather-details { margin: 2em 0; }
                .detail-row { display: flex; justify-content: space-between; padding: 0.5em 0; border-bottom: 1px solid #eee; }
                .detail-row:last-child { border-bottom: none; }
                .weather-forecast h4 { margin-bottom: 1em; color: #333; }
                .forecast-day { display: flex; justify-content: space-between; align-items: center; padding: 0.75em; margin: 0.5em 0; background-color: #f8f9fa; border-radius: 8px; }
                .forecast-day div { flex: 1; text-align: center; }
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
                `).join('');
                content += '</div>';
            } else {
                content += '<p>You have no upcoming appointments.</p>';
            }
            openWidget('appointments', 'Upcoming Appointments', content);
        } catch (error) {
            console.error("Error loading appointments:", error);
            openWidget('appointments', 'Upcoming Appointments', '<p>Error loading appointments.</p>');
        }
    }
    
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
            console.error("Error loading user profile:", error);
            openWidget('profile', 'My Profile', '<p>Error loading profile.</p>');
        }
    }
    
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
    
    // Mode toggle functionality
    function initializeModeToggle() {
        // Set initial state to AI Mode (dashboard)
        updateModeButton('ai');
    }
    
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

// Global function for the toggle button onclick
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
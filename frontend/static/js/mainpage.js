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
        console.log('Appointments widget clicked');
        openWidget('appointments', 'Upcoming Appointments', generateAppointmentsContent());
    }
    
    function handleHomeClick() {
        console.log('Home widget clicked');
        openWidget('home', 'Home Management', generateHomeContent());
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
    
    function generateAppointmentsContent() {
        return `
            <div class="appointments-info">
                <div class="upcoming-section">
                    <h3>Next Appointments</h3>
                    <div class="appointment-item">
                        <div class="appointment-time">Today 14:30</div>
                        <div class="appointment-title">Doctor Appointment</div>
                        <div class="appointment-location">Health Center, Østerbro</div>
                    </div>
                    <div class="appointment-item">
                        <div class="appointment-time">Tomorrow 10:00</div>
                        <div class="appointment-title">Business Meeting</div>
                        <div class="appointment-location">Office Conference Room</div>
                    </div>
                    <div class="appointment-item">
                        <div class="appointment-time">Friday 16:00</div>
                        <div class="appointment-title">Dentist Checkup</div>
                        <div class="appointment-location">Dental Clinic, Nørrebro</div>
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
                            <div class="calendar-day today">16</div>
                            <div class="calendar-day has-appointment">17</div>
                            <div class="calendar-day has-appointment">18</div>
                            <div class="calendar-day">19</div>
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
    
    function generateHomeContent() {
        return `
            <div class="home-info">
                <h3>Saved Addresses</h3>
                <div class="addresses-list">
                    <div class="address-card">
                        <div class="address-header">
                            <h4>🏠 Primary Home</h4>
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
                                    <div class="pref-item">🌡️ Smart thermostat: 21°C</div>
                                    <div class="pref-item">🔒 Security system: Armed at night</div>
                                    <div class="pref-item">💡 Lighting: Auto at sunset</div>
                                    <div class="pref-item">🔌 Smart outlets: Schedule enabled</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="address-card">
                        <div class="address-header">
                            <h4>🏖️ Summer House</h4>
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
                                    <div class="pref-item">🌡️ Heating: 18°C minimum</div>
                                    <div class="pref-item">🌿 Garden sprinkler: Weekends only</div>
                                    <div class="pref-item">📹 Security: Motion detection</div>
                                    <div class="pref-item">🌊 Beach access: Private path</div>
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
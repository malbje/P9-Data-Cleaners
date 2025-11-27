/**
 * @fileoverview Main dashboard JavaScript functionality
 * Handles widget interactions, modal system, chatbot, and user authentication
 * © Data Cleaners Team + OpenAI Chat Integration Upgrade
 */

// ============================================================================
// MAIN APPLICATION INITIALIZATION
// ============================================================================
document.addEventListener("DOMContentLoaded", () => {
    loadUserInfo();
    initializeModal();
    initializeModeToggle();


        const loadUserData = async () => {
        try {
            // Check user authentication status and get user details
            const statusResponse = await fetch('/api/auth/status');
            if (!statusResponse.ok) {
                throw new Error(`Authentication status check failed: ${statusResponse.statusText}`);
            }
            const statusData = await statusResponse.json();
            
                if (statusData.logged_in) {
                // Pre-populate form fields with user data if those elements exist
                const createNameEl = document.getElementById('create_name');
                const createEmailEl = document.getElementById('create_email');
                if (createNameEl) createNameEl.value = statusData.user.name;
                if (createEmailEl) createEmailEl.value = statusData.user.email;

                // Set user's default notification preference in dropdown if present
                const userPreference = statusData.user.notification_preference;
                const notificationSelect = document.getElementById('create_notification');
                if (userPreference && notificationSelect) {
                    notificationSelect.value = userPreference;
                }

                // Load appointment data after confirming authentication
                fetchAllAppointments(); 

            } else {
                // Handle unauthenticated state
                document.getElementById('select_address').innerHTML = '<option value="">Please log in to see addresses</option>';
                document.getElementById("customer-table-container").innerHTML = "<p>Please log in to see your appointments.</p>";
                return; // Exit early for unauthenticated users
            }

            // Fetch user's saved addresses from API
            const addressResponse = await fetch('/api/user/addresses');
            if (!addressResponse.ok) throw new Error('Failed to fetch addresses');
            const addresses = await addressResponse.json();
            
            // Populate address dropdowns for page elements if present. Templates may no longer
            // include dedicated create/reschedule selects because creation is handled from the
            // calendar details pane.
            const createAddressSelect = document.getElementById('select_address');
            const rescheduleAddressSelect = document.getElementById('reschedule_address_select');
            const addressOptions = addresses.map(addr => 
                `<option value="${addr.id}">${addr.street_and_number}, ${addr.postal_code} ${addr.city_name}</option>`
            ).join('');
            if (createAddressSelect) createAddressSelect.innerHTML = addressOptions;
            if (rescheduleAddressSelect) rescheduleAddressSelect.innerHTML = '<option value="">-- Select an address --</option>' + addressOptions;

        } catch (error) {
            console.error("Error loading user data:", error);
            // Display error message in address dropdown
            document.getElementById('select_address').innerHTML = '<option value="">Error loading addresses</option>';
        }
    };

    // ========================================================================
    // WIDGETS - CLICK INITIALIZATION
    // ========================================================================
    const widgets = document.querySelectorAll('.widget-card');
    widgets.forEach(widget => {
        widget.addEventListener('click', () => {
            handleWidgetClick(widget.dataset.widget);
        });
    });

    function handleWidgetClick(widgetType) {
        switch(widgetType) {
            case 'weather': handleWeatherClick(); break;
            case 'appointments': handleAppointmentsClick(); break;
            case 'addresses': handleAddressesClick(); break;
            case 'profile': handleProfileClick(); break;
            default: console.log('Unknown widget type:', widgetType);
        }
    }


    // ========================================================================
    // APPOINTMENTS WIDGET
    // ============================================================================
    async function handleAppointmentsClick() {
        await loadAppointmentsContent();
    }

    // ========================================================================
    // ADDRESSES WIDGET
    // ============================================================================
    async function handleAddressesClick() {
        const content = await generateHomeContent();
        openWidget('addresses', 'My Addresses', content);
    }

    // ========================================================================
    // PROFILE WIDGET
    // ============================================================================
    async function handleProfileClick() {
        await loadUserProfileContent();
    }

    // ========================================================================
    // CHATBOT SYSTEM ✅ OpenAI-Integration ✅
    // ============================================================================
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const userMessage = chatInput.value.trim();
            if (!userMessage) return;

            addMessageToChat(userMessage, 'user');
            chatInput.value = '';

            const typingId = addTypingIndicator();

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: userMessage})
                });

                if (res.status === 401) {
                    removeTypingIndicator(typingId);
                    window.location.href = '/login';
                    return;
                }

                const data = await res.json();
                removeTypingIndicator(typingId);
                addMessageToChat(data.reply || "Jeg kunne ikke finde noget at svare.", "bot");

            } catch (err) {
                console.error('Chat API Error:', err);
                removeTypingIndicator(typingId);
                addMessageToChat("Fejl: kunne ikke kontakte serveren ❌", "bot");
            }
        });
    }

    function addMessageToChat(message, sender) {
        const msgEl = document.createElement("div");
        msgEl.className = `message ${sender}`;
        msgEl.textContent = message;
        chatMessages.appendChild(msgEl);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addTypingIndicator() {
        const id = `typing-${Date.now()}`;
        const el = document.createElement("div");
        el.className = "message bot";
        el.id = id;
        el.textContent = "AI skriver…";
        chatMessages.appendChild(el);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return id;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    // ========================================================================
    // AUTH + DASHBOARD DATA LOADING
    // ============================================================================
    async function loadUserInfo() {
        try {
            const res = await fetch('/api/auth/status');
            const data = await res.json();
            if (!data.logged_in) window.location.href = '/login';
            document.getElementById('user-info').textContent = `Welcome, ${data.user.name}`;
        } catch {
            window.location.href = '/login';
        }
    }

    // ========================================================================
    // MODAL + SHOW HELPERS
    // ============================================================================
    function initializeModal() {
        const closeBtn = document.getElementById('modal-close');
        closeBtn.addEventListener('click', closeModal);

        document.addEventListener('keydown', (e) => {
            if (e.key !== 'Escape') return;
            if (document.getElementById('widget-modal').classList.contains('active'))
                closeModal();
        });
    }

    function openWidget(widgetType, title, content) {
        document.getElementById('modal-title').textContent = title;
        document.getElementById('modal-body').innerHTML = content;
        document.getElementById('widget-grid').style.display = 'none';
        document.getElementById('widget-modal').classList.add('active');
    }

    function closeModal() {
        document.getElementById('widget-modal').classList.remove('active');
        document.getElementById('widget-grid').style.display = 'grid';
    }

    // ========================================================================
    // WEATHER CONTENT
    // ============================================================================
    function generateWeatherContent() {
        return `<p>Weather data coming soon 🌤</p>`;
    }

    // ========================================================================
    // ADDRESSES CONTENT
    // ============================================================================
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

    // ========================================================================
    // APPOINTMENTS CONTENT
    // ============================================================================

    async function loadAppointmentsContent() {
        // Fetch appointments and render an interactive month calendar highlighting
        // days that have appointments. Clicking a highlighted day shows that
        // day's appointments below the calendar.
            try {
            // Fetch merged events (Google + DB). The backend returns an array of
            // objects: { google: <event|null>, appointment: <dbRow|null>, matched: bool }
            // We normalize each item into the same shape the calendar UI expects
            // so the existing rendering code can be reused.
            const now = new Date();
            const startIso = new Date(now.getFullYear(), now.getMonth(), 1).toISOString();
            const endIso = new Date(now.getFullYear(), now.getMonth() + 2, 0).toISOString();
            const response = await fetch(`/api/calendar/combined?start=${encodeURIComponent(startIso)}&end=${encodeURIComponent(endIso)}`);
            if (!response.ok) {
                throw new Error('Failed to fetch combined calendar data');
            }
            const merged = await response.json();

            // Organize appointments by ISO date string (YYYY-MM-DD)
            const apptsByDate = {};

            function pushAppt(dateStr, item) {
                if (!apptsByDate[dateStr]) apptsByDate[dateStr] = [];
                apptsByDate[dateStr].push(item);
            }

            merged.forEach(pair => {
                // If there is a DB appointment, prefer its date/time for grouping
                const dbAppt = pair.appointment;
                const gAppt = pair.google;
                if (dbAppt) {
                    const d = dbAppt.date; // YYYY-MM-DD
                    const time = dbAppt.time ? dbAppt.time.slice(0,5) : '00:00';
                    pushAppt(d, Object.assign({}, dbAppt, {
                        _source: gAppt && dbAppt ? (pair.matched ? 'Both' : 'DB') : 'DB'
                    }));
                }
                if (gAppt) {
                    // Google event: extract date and time from start (could be date-only or dateTime)
                    const startStr = gAppt.start || '';
                    let dateOnly = startStr.slice(0,10);
                    let timeOnly = '';
                    if (startStr.includes('T')) {
                        // format like 2025-11-15T10:00:00+00:00
                        const t = startStr.split('T')[1] || '';
                        timeOnly = t.slice(0,5);
                    }
                    // Create a DB-like representation so UI can reuse rendering
                    const syntheticDataFormat = {
                        id: gAppt.id || `g-${Math.random().toString(36).slice(2,8)}`,
                        date: dateOnly,
                        time: timeOnly || '00:00',
                        notes: gAppt.description || '',
                        address: gAppt.location || '',
                        service_names: gAppt.summary || 'Google Event',
                        _source: dbAppt && pair.matched ? 'Both' : 'Google'
                    };
                    pushAppt(dateOnly, syntheticDataFormat);
                }
            });

            // Fetch user's addresses with preferences so we can show preference info
            // alongside each appointment in the day-details pane.
            let prefsByAddressString = {};
            try {
                const addrResp = await fetch('/api/user/addresses-with-preferences');
                if (addrResp.ok) {
                    const addrs = await addrResp.json();
                    // Build lookup key matching how appointments format addresses
                    // DB uses CONCAT(street_and_number, ', ', postal_code, ' ', city_name)
                    addrs.forEach(a => {
                        const key = `${a.street_and_number}, ${a.postal_code} ${a.city_name}`;
                        prefsByAddressString[key] = a;
                    });
                }
            } catch (err) {
                console.warn('Could not load address preferences:', err);
            }

            // Calendar rendering is delegated to the reusable calendar widget.
            const content = (window.getCalendarSkeleton && typeof window.getCalendarSkeleton === 'function')
                ? window.getCalendarSkeleton()
                : `
                    <div class="calendar-widget">
                        <div class="cal-header">
                            <button id="cal-prev" class="cal-nav" aria-label="Previous month">‹</button>
                            <div id="cal-month-year" class="cal-title"></div>
                            <button id="cal-next" class="cal-nav" aria-label="Next month">›</button>
                        </div>
                        <div id="cal-grid" class="cal-grid"></div>
                        <div id="cal-day-appointments" class="cal-day-appointments"><em>Select a day to see appointments</em></div>
                    </div>
                `;

            openWidget('appointments', 'Upcoming Appointments', content);

            // Attach behavior provided by calendar_widget; pass prepared data structures
            if (window.attachAppointmentsCalendar && typeof window.attachAppointmentsCalendar === 'function') {
                try {
                    window.attachAppointmentsCalendar(apptsByDate, prefsByAddressString || {});
                } catch (err) {
                    console.error('Failed to attach calendar widget:', err);
                }
            } else {
                // Fallback: if widget isn't loaded, just render a plain list of dates
                const container = document.getElementById('cal-day-appointments');
                if (container) {
                    container.innerHTML = '<p>Calendar not available.</p>';
                }
            }

        } catch (error) {
            console.error('Error loading appointments:', error);
            openWidget('appointments', 'Upcoming Appointments', '<p>Error loading appointments.</p>');
        }
    }


    // ========================================================================
    // PROFILE CONTENT
    // ============================================================================
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
    // MODE TOGGLE
    // ============================================================================
    function initializeModeToggle() {
        updateModeButton('ai');
    }

    function updateModeButton(mode) {
        const btn = document.getElementById('mode-toggle-btn');
        const txt = btn.querySelector('.mode-text');
        if (mode === 'ai') {
            txt.textContent = 'Manual Mode';
            btn.classList.add('active');
        } else {
            txt.textContent = 'AI Mode';
            btn.classList.remove('active');
        }
    }
});

// ============================================================================
// GLOBAL
// ============================================================================
function toggleMode() {
    const txt = document.querySelector('#mode-toggle-btn .mode-text').textContent;
    window.location.href = txt === 'Manual Mode' ? '/manual' : '/';
}
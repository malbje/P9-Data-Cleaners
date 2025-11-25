/**
 * @fileoverview
 * Main dashboard JavaScript functionality.
 * Handles widget interactions, modal system, chatbot, and authentication.
 * Includes live weather (temperature, rain, humidity, wind, pollen).
 * © Data Cleaners Team + OpenAI Chat Integration Upgrade
 */

// ============================================================================
// MAIN APPLICATION INITIALIZATION
// ============================================================================
document.addEventListener("DOMContentLoaded", () => {
    console.log("✅ mainpage.js loaded successfully");

    // Initialize user info and modal system
    loadUserInfo();
    initializeModal();

    // ========================================================================
    // WIDGET CLICK HANDLERS
    // ========================================================================
    const widgets = document.querySelectorAll(".widget-card");
    console.log("✅ Widgets found:", widgets.length);

    widgets.forEach(widget => {
        widget.addEventListener("click", () => {
            handleWidgetClick(widget.dataset.widget);
        });
    });

    function handleWidgetClick(widgetType) {
        switch (widgetType) {
            case "weather":
                handleWeatherClick();
                break;
            case "appointments":
                handleAppointmentsClick();
                break;
            case "addresses":
                handleAddressesClick();
                break;
            case "profile":
                handleProfileClick();
                break;
            default:
                console.log("⚠️ Unknown widget type:", widgetType);
        }
    }

    // ========================================================================
    // WEATHER WIDGET
    // ========================================================================
    function handleWeatherClick() {
        openWidget("weather", "Weather Information", generateWeatherContent());
    }

    /**
     * Generates weather widget HTML and fetches live data from Flask backend.
     */
    function generateWeatherContent() {
        const content = `
            <div id="weather-content">
                <p>Loading live weather data... 🌦</p>
            </div>
        `;

        fetch("/api/weather")
            .then(res => res.json())
            .then(data => {
                const el = document.getElementById("weather-content");
                if (!el) return;

                // Handle backend error
                if (data.error) {
                    el.innerHTML = `
                        <div class="weather-error">
                            <p>⚠️ Could not fetch weather data:</p>
                            <pre>${data.error}</pre>
                        </div>
                    `;
                    return;
                }

                // Extract key data fields
                const temp = data.temperature ?? "?";
                const wind = data.wind_speed ?? "?";
                const humidity = data.humidity ?? "?";
                const rain = data.rain ?? "?";
                const provider = data.provider || "Unknown";
                const pollenData = data.pollen || {};

                // Build pollen list
                let pollenList = "";
                if (typeof pollenData === "object" && Object.keys(pollenData).length > 0) {
                    pollenList = Object.entries(pollenData)
                        .map(([type, value]) => `<li>${type}: ${value}</li>`)
                        .join("");
                } else {
                    pollenList = "<li>No pollen data available</li>";
                }

                // Render formatted content
                el.innerHTML = `
                    <div class="weather-info">
                        <h3>🌤 Current Weather (${provider})</h3>
                        <ul>
                            <li><strong>Temperature:</strong> ${temp}°C</li>
                            <li><strong>Wind speed:</strong> ${wind} m/s</li>
                            <li><strong>Humidity:</strong> ${humidity}%</li>
                            <li><strong>Rain:</strong> ${rain} mm</li>
                        </ul>
                        <h4>Pollen</h4>
                        <ul>${pollenList}</ul>
                        <p class="small">Data from ${provider} API</p>
                    </div>
                    <style>
                        .weather-info {
                            padding: 1em;
                            background: #f8f9fa;
                            border-radius: 12px;
                            box-shadow: 0 0 6px rgba(0,0,0,0.1);
                        }
                        .weather-info ul {
                            list-style: none;
                            padding: 0;
                            margin: 0.5em 0;
                        }
                        .weather-info li {
                            margin: 0.3em 0;
                            font-size: 0.95em;
                        }
                        .weather-error {
                            background-color: #fff3cd;
                            color: #856404;
                            border-radius: 8px;
                            padding: 1em;
                            font-size: 0.9em;
                            word-break: break-word;
                        }
                        .small {
                            color: #777;
                            font-size: 0.9em;
                            margin-top: 1em;
                        }
                    </style>
                `;
            })
            .catch(err => {
                console.error("Weather fetch error:", err);
                const el = document.getElementById("weather-content");
                if (el) el.innerHTML = `<p>Could not load weather data.</p>`;
            });

        return content;
    }

    // ========================================================================
    // CHATBOT SYSTEM
    // ========================================================================
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatMessages = document.getElementById("chat-messages");

    if (chatForm) {
        chatForm.addEventListener("submit", async e => {
            e.preventDefault();

            const userMessage = chatInput.value.trim();
            if (!userMessage) return;

            addMessageToChat(userMessage, "user");
            chatInput.value = "";

            const typingId = addTypingIndicator();

            try {
                const res = await fetch("/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: userMessage })
                });

                if (res.status === 401) {
                    removeTypingIndicator(typingId);
                    window.location.href = "/login";
                    return;
                }

                const data = await res.json();
                removeTypingIndicator(typingId);
                addMessageToChat(data.reply || "I couldn’t find a suitable answer.", "bot");
            } catch (err) {
                console.error("Chat API Error:", err);
                removeTypingIndicator(typingId);
                addMessageToChat("Error: could not reach the server ", "bot");
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
        el.textContent = "AI is typing…";
        chatMessages.appendChild(el);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return id;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    // ========================================================================
    // AUTH + DASHBOARD DATA
    // ========================================================================
    async function loadUserInfo() {
        try {
            const res = await fetch("/api/auth/status");
            const data = await res.json();
            if (!data.logged_in) window.location.href = "/login";
            document.getElementById("user-info").textContent = `Welcome, ${data.user.name}`;
        } catch {
            window.location.href = "/login";
        }
    }

    // ========================================================================
    // MODAL SYSTEM
    // ========================================================================
    function initializeModal() {
        const closeBtn = document.getElementById("modal-close");
        closeBtn.addEventListener("click", closeModal);

        document.addEventListener("keydown", e => {
            if (e.key === "Escape" && document.getElementById("widget-modal").classList.contains("active")) {
                closeModal();
            }
        });
    }

    function openWidget(widgetType, title, content) {
        document.getElementById("modal-title").textContent = title;
        document.getElementById("modal-body").innerHTML = content;
        document.getElementById("widget-grid").style.display = "none";
        document.getElementById("widget-modal").classList.add("active");
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
                const g = pair.google;
                if (dbAppt) {
                    const d = dbAppt.date; // YYYY-MM-DD
                    const time = dbAppt.time ? dbAppt.time.slice(0,5) : '00:00';
                    pushAppt(d, Object.assign({}, dbAppt, {
                        _source: g && dbAppt ? (pair.matched ? 'Both' : 'DB') : 'DB'
                    }));
                }
                if (g) {
                    // Google event: extract date and time from start (could be date-only or dateTime)
                    const startStr = g.start || '';
                    let dateOnly = startStr.slice(0,10);
                    let timeOnly = '';
                    if (startStr.includes('T')) {
                        // format like 2025-11-15T10:00:00+00:00
                        const t = startStr.split('T')[1] || '';
                        timeOnly = t.slice(0,5);
                    }
                    // Create a DB-like representation so UI can reuse rendering
                    const synthetic = {
                        id: g.id || `g-${Math.random().toString(36).slice(2,8)}`,
                        date: dateOnly,
                        time: timeOnly || '00:00',
                        notes: g.description || '',
                        address: g.location || '',
                        service_names: g.summary || 'Google Event',
                        _source: dbAppt && pair.matched ? 'Both' : 'Google'
                    };
                    pushAppt(dateOnly, synthetic);
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

            // Calendar view state
            const today = new Date();
            let viewYear = today.getFullYear();
            let viewMonth = today.getMonth(); // 0-11

            // Calendar HTML structure (month navigation, grid, and details)
            const content = `
                <div class="calendar-widget">
                    <div class="cal-header">
                        <button id="cal-prev" class="cal-nav" aria-label="Previous month">‹</button>
                        <div id="cal-month-year" class="cal-title"></div>
                        <button id="cal-next" class="cal-nav" aria-label="Next month">›</button>
                    </div>
                    <div id="cal-grid" class="cal-grid"></div>
                    <div id="cal-day-appointments" class="cal-day-appointments"><em>Select a day to see appointments</em></div>
                </div>
                <!-- Calendar styles moved to frontend/static/css/style.css for maintainability -->
            `;

            // Open modal with calendar skeleton
            openWidget('appointments', 'Upcoming Appointments', content);

            // Helper utilities
            const pad = (n) => n.toString().padStart(2, '0');

            // Render calendar month into DOM
            function renderCalendar(year, month) {
                const monthStart = new Date(year, month, 1);
                const monthName = monthStart.toLocaleString(undefined, { month: 'long' });
                const daysInMonth = new Date(year, month + 1, 0).getDate();
                const startWeekday = monthStart.getDay(); // 0 = Sunday

                const grid = document.getElementById('cal-grid');
                const title = document.getElementById('cal-month-year');
                title.textContent = `${monthName} ${year}`;

                // Weekday headers
                const weekdays = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
                let html = '';
                weekdays.forEach(w => { html += `<div class="cal-weekday">${w}</div>`; });

                // Empty cells for previous month
                for (let i = 0; i < startWeekday; i++) {
                    html += `<div class="cal-day disabled"></div>`;
                }

                // Days
                for (let day = 1; day <= daysInMonth; day++) {
                    const dateStr = `${year}-${pad(month + 1)}-${pad(day)}`;
                    const has = Array.isArray(apptsByDate[dateStr]) && apptsByDate[dateStr].length > 0;
                    const isToday = (new Date().toISOString().slice(0,10) === dateStr);
                    html += `
                        <div class="cal-day ${has? 'has-appt':''} ${isToday? 'today':''}" data-date="${dateStr}">
                            <div class="date-num">${day}</div>
                            ${has? '<div class="dot" aria-hidden="true"></div>' : ''}
                        </div>
                    `;
                }

                grid.innerHTML = html;

                // Attach click listeners to days; only days with appointments are selectable
                grid.querySelectorAll('.cal-day').forEach(el => {
                    if (el.classList.contains('disabled')) return;
                    if (!el.classList.contains('has-appt')) {
                        // mark visually as not having appointments (lighter interaction)
                        el.classList.add('no-appt');
                        return;
                    }
                    el.addEventListener('click', () => {
                        // clear previous selection
                        grid.querySelectorAll('.cal-day.selected').forEach(s => s.classList.remove('selected'));
                        // mark this day selected and show details
                        el.classList.add('selected');
                        const ds = el.getAttribute('data-date');
                        showAppointmentsForDate(ds);

                        // Auto-scroll the details pane into view so the user sees
                        // the appointment information without manual scrolling.
                        // Use smooth behavior for a nicer UX.
                        const details = document.getElementById('cal-day-appointments');
                        if (details && typeof details.scrollIntoView === 'function') {
                            // If the modal body provides its own scrolling, this will
                            // bring the details into view within the modal.
                            try {
                                details.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            } catch (e) {
                                // Fallback for older browsers/environments
                                details.scrollIntoView();
                            }
                        }
                    });
                });
            }

            // Show appointments for a specific date in the details pane
            function showAppointmentsForDate(dateStr) {
                const container = document.getElementById('cal-day-appointments');
                const list = apptsByDate[dateStr] || [];
                if (list.length === 0) {
                    container.innerHTML = `<em>No appointments on ${dateStr}.</em>`;
                    return;
                }
                let html = `<h4>Appointments on ${dateStr}</h4>`;
                html += '<div class="appt-list">';
                list.forEach(a => {
                    const prefs = prefsByAddressString[a.address] || null;
                    html += `
                        <div class="appt-item">
                            <div><strong>${a.service_names || 'General Cleaning'}</strong> — ${a.time.slice(0,5)}</div>
                            <div class="small"> ${a.address}</div>
                            <div class="small"> Source: ${a._source || 'DB'}</div>
                            ${a.notes? `<div class="small">Notes: ${a.notes}</div>` : ''}
                            ${prefs ? `
                                <div class="small" style="margin-top:0.5rem"><strong>Preferences:</strong></div>
                                <ul class="small" style="margin:0.25rem 0 0 1rem; padding:0; list-style:disc;">
                                    <li>Allergies: ${prefs.allergies || 'None specified'}</li>
                                    <li>Pets: ${prefs.pets || 'None specified'}</li>
                                    <li>Kids: ${prefs.kids || 'None specified'}</li>
                                    <li>Size: ${prefs.square_footage ? prefs.square_footage + ' m²' : 'Not specified'}</li>
                                    <li>Notes: ${prefs.preference_notes || 'None'}</li>
                                </ul>
                            ` : ''}
                        </div>
                    `;
                });
                html += '</div>';
                container.innerHTML = html;
            }
            

            // Month navigation handlers
            document.getElementById('cal-prev').addEventListener('click', () => {
                viewMonth -= 1;
                if (viewMonth < 0) { viewMonth = 11; viewYear -= 1; }
                renderCalendar(viewYear, viewMonth);
                document.getElementById('cal-day-appointments').innerHTML = '<em>Select a day to see appointments</em>';

                // Ensure the calendar header is visible after changing months.
                // The modal body is the scrollable container, so scroll it to top.
                const modalBody = document.getElementById('modal-body');
                if (modalBody) {
                    try {
                        modalBody.scrollTo({ top: 0, behavior: 'smooth' });
                    } catch (e) {
                        modalBody.scrollTop = 0;
                    }
                }
            });
            document.getElementById('cal-next').addEventListener('click', () => {
                viewMonth += 1;
                if (viewMonth > 11) { viewMonth = 0; viewYear += 1; }
                renderCalendar(viewYear, viewMonth);
                document.getElementById('cal-day-appointments').innerHTML = '<em>Select a day to see appointments</em>';

                // Scroll modal body to top so the month navigation remains reachable
                const modalBody = document.getElementById('modal-body');
                if (modalBody) {
                    try {
                        modalBody.scrollTo({ top: 0, behavior: 'smooth' });
                    } catch (e) {
                        modalBody.scrollTop = 0;
                    }
                }
            });

            // Initial render
            renderCalendar(viewYear, viewMonth);

            // Auto-select today's date if it has appointments
            const todayStr = new Date().toISOString().slice(0,10);
            if (apptsByDate[todayStr]) {
                const todayEl = document.querySelector(`.cal-day[data-date="${todayStr}"]`);
                if (todayEl) {
                    // ensure selected class and show details
                    todayEl.classList.add('selected');
                    showAppointmentsForDate(todayStr);

                    // Scroll the details into view when auto-selecting today
                    const details = document.getElementById('cal-day-appointments');
                    if (details && typeof details.scrollIntoView === 'function') {
                        try {
                            details.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        } catch (e) {
                            details.scrollIntoView();
                        }
                    }
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
    // ========================================================================
    function initializeModeToggle() {
        updateModeButton("ai");
    }

    function updateModeButton(mode) {
        const btn = document.getElementById("mode-toggle-btn");
        const txt = btn.querySelector(".mode-text");
        if (mode === "ai") {
            txt.textContent = "Manual Mode";
            btn.classList.add("active");
        } else {
            txt.textContent = "AI Mode";
            btn.classList.remove("active");
        }
    }

    initializeModeToggle();
});

// ============================================================================
// GLOBAL FUNCTION
// ============================================================================
function toggleMode() {
    const txt = document.querySelector("#mode-toggle-btn .mode-text").textContent;
    window.location.href = txt === "Manual Mode" ? "/manual" : "/";
}

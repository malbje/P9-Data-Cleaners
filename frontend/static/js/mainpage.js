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
    // WEATHER WIDGET
    // ============================================================================
    function handleWeatherClick() {
        openWidget('weather', 'Weather Information', generateWeatherContent());
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
        let content = '<h3>Your Registered Addresses</h3>';
        try {
            const res = await fetch('/api/user/addresses-with-preferences');
            const addresses = await res.json();

            if (!addresses.length) {
                return content + '<p>No registered addresses.</p>';
            }

            content += '<ul>' + addresses.map(a =>
                `<li>📍 ${a.street_and_number}, ${a.postal_code} ${a.city_name}</li>`
            ).join('') + '</ul>';

        } catch {
            content += '<p>Error loading addresses.</p>';
        }

        return content;
    }

    // ========================================================================
    // APPOINTMENTS CONTENT
    // ============================================================================

    async function loadAppointmentsContent() {
        // Fetch appointments and render an interactive month calendar highlighting
        // days that have appointments. Clicking a highlighted day shows that
        // day's appointments below the calendar.
        try {
            const response = await fetch('/api/appointments');
            if (!response.ok) {
                return;
            }
            const appointments = await response.json();
            
            // Organize appointments by ISO date string (YYYY-MM-DD)
            const apptsByDate = {};
            appointments.forEach(appt => {
                const d = appt.date; // expected format YYYY-MM-DD
                if (!apptsByDate[d]) apptsByDate[d] = [];
                apptsByDate[d].push(appt);
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
                            <div class="small">📍 ${a.address}</div>
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
    async function loadUserProfileContent() {
        try {
            const res = await fetch('/api/auth/status');
            const data = await res.json();
            if (!data.logged_in) return openWidget('profile', 'Profile', '<p>Login required.</p>');

            const user = data.user;
            openWidget('profile', 'My Profile', `
                <p>Navn: ${user.name}</p>
                <p>Email: ${user.email}</p>
            `);
        } catch {
            openWidget('profile', 'My Profile', '<p>Error.</p>');
        }
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

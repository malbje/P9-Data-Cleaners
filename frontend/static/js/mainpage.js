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
        try {
            const res = await fetch('/api/appointments');
            const appointments = await res.json();

            let html = '<h3>Your Upcoming Appointments</h3>';
            html += '<ul>' + appointments.map(a =>
                `<li>${a.date} | ${a.service_names || 'Cleaning'} @ ${a.address}</li>`
            ).join('') + '</ul>';

            openWidget('appointments', 'Upcoming Appointments', html);

        } catch {
            openWidget('appointments', 'Upcoming Appointments', '<p>Error loading.</p>');
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

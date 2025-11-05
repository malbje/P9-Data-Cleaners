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
        document.getElementById("widget-modal").classList.remove("active");
        document.getElementById("widget-grid").style.display = "grid";
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

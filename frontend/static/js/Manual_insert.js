/**
 * @fileoverview Manual appointment booking and management interface
 * Handles form interactions, data loading, and API communication for staff booking system
 * @author Data Cleaners Team
 * @version 1.0.0
 */

// ============================================================================
// MAIN APPLICATION INITIALIZATION
// ============================================================================

/**
 * Initialize manual booking interface when DOM is ready
 * Sets up forms, loads user data, and configures default values
 */
document.addEventListener("DOMContentLoaded", () => {
    // ========================================================================
    // FORM DEFAULT VALUES SETUP
    // ========================================================================
    
    /**
     * Set default date and time values for appointment booking form
     * Uses current date and time as sensible defaults
     */
    const now = new Date();
    const today = now.toISOString().split("T")[0];  // Format: YYYY-MM-DD
    const currentTime = now.toTimeString().slice(0, 5);  // Format: HH:MM
    
    // Pre-populate booking form fields if they exist (forms were removed from template)
    const createDateEl = document.getElementById("create_date");
    const createTimeEl = document.getElementById("create_time");
    if (createDateEl) createDateEl.value = today;
    if (createTimeEl) createTimeEl.value = currentTime;
    // Hidden update fields default (may not exist anymore)
    const updateDateEl = document.getElementById("update_date");
    const updateTimeEl = document.getElementById("update_time");
    if (updateDateEl) updateDateEl.value = today;
    if (updateTimeEl) updateTimeEl.value = currentTime;

    // ========================================================================
    // USER DATA LOADING AND AUTHENTICATION
    // ========================================================================
    
    /**
     * Load user-specific data and populate form defaults
     * Fetches user authentication status, addresses, and appointment data
     * @async
     */
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
    // APPOINTMENT DATA LOADING AND DISPLAY
    // ========================================================================
    
    /**
     * Fetch and display all user appointments in a table format
     * Updates the customer-table-container with current appointment data
     * @async
     */
    const fetchAllAppointments = async () => {
        const container = document.getElementById("customer-table-container");
        try {
            // Fetch appointments for the authenticated user
            const response = await fetch("/api/appointments");
            const appointments = await response.json();
            
            // Sort appointments by date and time (earliest first)
            appointments.sort((a, b) => new Date(`${a.date}T${a.time}`) - new Date(`${b.date}T${b.time}`));

            // Handle empty appointments state
            if (appointments.length === 0) {
                container.innerHTML = "<p>You have no upcoming appointments.</p>";
                return;
            }

            // Generate card-based appointment display with delete functionality
            let content = '<div class="appointments-list">';
            // Map each appointment to a card HTML structure
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
                    <div class="appointment-actions">
                        <button class="danger delete-btn" data-id="${appt.id}" title="Delete this appointment">Delete</button>
                    </div>
                </div>
            `).join('');
            content += '</div>';

            // Clear previous content and inject new appointment cards
            // Note: Presentation/CSS for the classes below should live in your stylesheet
            // (e.g. frontend/static/css/style.css). Add the selectors shown in the comment
            // at the end of this file if not already present.
            container.innerHTML = "";
            container.innerHTML = content;

        } catch (error) {
            container.innerHTML = "<p>Error loading appointments.</p>";
            console.error("Fetch error:", error);
        }
    };

    // ========================================================================
    // USER FEEDBACK AND MESSAGING
    // ========================================================================
    
    /**
     * Display temporary success or error messages to the user
     * @param {string} text - Message text to display
     * @param {string} type - Message type ('success', 'error', etc.)
     */
    const showMessage = (text, type = "success") => {
        const container = document.getElementById("message-container");
        const messageDiv = document.createElement("div");
        messageDiv.className = `alert ${type}`;
        messageDiv.textContent = text;
        container.innerHTML = "";
        container.appendChild(messageDiv);
        // Auto-remove message after 4 seconds
        setTimeout(() => messageDiv.remove(), 4000);
    };

    // ========================================================================
    // APPOINTMENT DELETION HANDLING
    // ========================================================================
    
    /**
     * Handle appointment deletion via delete buttons in appointment cards
     * Uses event delegation to handle dynamically created buttons
     */
    document.getElementById("customer-table-container").addEventListener("click", async (e) => {
        if (e.target && e.target.classList.contains("delete-btn")) {
            const appointmentId = e.target.getAttribute("data-id");
            
            // Confirm deletion with user
            if (!confirm(`Are you sure you want to permanently delete appointment #${appointmentId}?`)) return;

            // Send DELETE request to API
            const response = await fetch(`/api/appointments/${appointmentId}`, { method: "DELETE" });

            if (response.ok) {
                showMessage("Appointment deleted successfully.");
                fetchAllAppointments(); // Refresh appointment list
            } else {
                const errorData = await response.json();
                showMessage(`Error: ${errorData.error}`, "error");
            }
        }
    });


    // ========================================================================
    // APPLICATION STARTUP
    // ========================================================================
    
    /**
     * Initialize application data loading
     * loadUserData() handles authentication, addresses, and appointments in sequence
     */
    loadUserData();
    // Initialize the calendar for manual booking view
    initializeManualCalendar();
});

/**
 * Initialize calendar on manual insert page by fetching appointments and
 * addresses, building apptsByDate map, inserting the calendar skeleton and
 * wiring callbacks for day click (create) and appointment click (reschedule).
 */
async function initializeManualCalendar() {
    try {
        // Fetch appointments (DB) for mapping
        const resp = await fetch('/api/appointments');
        const appointments = resp.ok ? await resp.json() : [];

        // Build apptsByDate: { 'YYYY-MM-DD': [appts...] }
        const apptsByDate = {};
        appointments.forEach(a => {
            const date = a.date;
            if (!apptsByDate[date]) apptsByDate[date] = [];
            apptsByDate[date].push({
                id: a.id,
                date: a.date,
                time: a.time || '00:00',
                notes: a.notes || '',
                address: a.address || '',
                address_id: a.address_id || a.address_id,
                service_names: a.service_names || '',
                _source: 'DB'
            });
        });

        // Fetch address preferences to show in calendar details and provide address list
        let prefsByAddressString = {};
        let addressesList = [];
        try {
            const addrResp = await fetch('/api/user/addresses-with-preferences');
            if (addrResp.ok) {
                const addrs = await addrResp.json();
                addressesList = addrs || [];
                addrs.forEach(a => {
                    const key = `${a.street_and_number}, ${a.postal_code} ${a.city_name}`;
                    prefsByAddressString[key] = Object.assign({}, a, { id: a.id });
                });
            }
        } catch (e) { console.warn('Could not fetch address prefs:', e); }

        // Render calendar skeleton into page container
        const container = document.getElementById('manual-calendar-container');
        if (!container) return;
        const skeleton = (window.getCalendarSkeleton && typeof window.getCalendarSkeleton === 'function')
            ? window.getCalendarSkeleton()
            : '<div class="calendar-widget"><p>Calendar not available.</p></div>';
        container.innerHTML = skeleton;

        // Attach calendar behavior with callbacks
        if (window.attachAppointmentsCalendar && typeof window.attachAppointmentsCalendar === 'function') {
            window.attachAppointmentsCalendar(apptsByDate, prefsByAddressString, {
                onDayClick: (dateStr, list) => {
                    // Page now uses calendar details for creation. Notify user instead
                    showMessage(`Selected ${dateStr}. Use the calendar details to create an appointment.`, 'success');
                },
                editable: true,
                addresses: addressesList,
                onAppointmentUpdate: async (appt, updated) => {
                    // PUT updated appointment to backend and refresh calendar on success
                    if (!appt || !appt.id) {
                        showMessage('Cannot update this appointment.', 'error');
                        return;
                    }
                    try {
                        const res = await fetch(`/api/appointments/${appt.id}`, {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(updated)
                        });
                        if (!res.ok) {
                            const err = await res.json();
                            showMessage(`Error updating appointment: ${err.error || res.statusText}`, 'error');
                            return;
                        }
                        showMessage('Appointment updated successfully.', 'success');
                        // Re-initialize calendar to pick up changes
                        initializeManualCalendar();
                    } catch (err) {
                        console.error('Update failed:', err);
                        showMessage('Failed to update appointment.', 'error');
                    }
                },
                onAppointmentClick: (appt) => {
                    // Instead of filling removed reschedule form, instruct user to use the
                    // calendar details pane which now contains edit/reschedule controls.
                    if (!appt || !appt.id) { showMessage('This event cannot be rescheduled from manual UI.', 'error'); return; }
                    showMessage(`Selected appointment #${appt.id}. Use the calendar details to edit or reschedule.`, 'success');
                }
                ,
                onCreateAppointment: async (payload) => {
                    // Expect payload: { date, time, address_id, service_names, notes }
                    try {
                        // Map to backend manual insert payload
                        const createPayload = {
                            address_id: payload.address_id,
                            date: payload.date,
                            time: payload.time,
                            notes: payload.notes,
                            service_ids: payload.service_names ? [1] : []
                        };
                        const res = await fetch('/api/manual_insert', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(createPayload)
                        });
                        if (!res.ok) {
                            const err = await res.json();
                            showMessage(`Error creating appointment: ${err.error || res.statusText}`, 'error');
                            return;
                        }
                        showMessage('Appointment created successfully.', 'success');
                        // Refresh both calendar and appointment list
                        initializeManualCalendar();
                        fetchAllAppointments();
                    } catch (err) {
                        console.error('Create appointment failed:', err);
                        showMessage('Failed to create appointment.', 'error');
                    }
                }
            });
        }
    } catch (err) {
        console.error('Calendar init error:', err);
    }
}



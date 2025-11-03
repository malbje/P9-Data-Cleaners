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
    
    // Pre-populate booking form with current date/time
    document.getElementById("create_date").value = today;
    document.getElementById("create_time").value = currentTime;

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
                // Pre-populate form fields with user data
                document.getElementById('create_name').value = statusData.user.name;
                document.getElementById('create_email').value = statusData.user.email;
                
                // Set user's default notification preference in dropdown
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
            
            // Populate address dropdowns for both booking forms
            const createAddressSelect = document.getElementById('select_address');
            const rescheduleAddressSelect = document.getElementById('reschedule_address_select');
            
            // Generate HTML options for address dropdowns
            const addressOptions = addresses.map(addr => 
                `<option value="${addr.id}">${addr.street_and_number}, ${addr.postal_code} ${addr.city_name}</option>`
            ).join('');

            // Populate create appointment address dropdown
            createAddressSelect.innerHTML = addressOptions;
            
            // Populate reschedule appointment dropdown with placeholder
            rescheduleAddressSelect.innerHTML = '<option value="">-- Select an address --</option>' + addressOptions;

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
    // APPOINTMENT BOOKING FORM HANDLING
    // ========================================================================
    
    /**
     * Handle new appointment creation form submission
     * Collects form data and sends POST request to create appointment
     */
    document.getElementById("form_create").addEventListener("submit", async (e) => {
        e.preventDefault();

        // Prepare appointment data from form inputs
        const appointmentData = {
            address_id: document.getElementById("select_address").value,
            date: document.getElementById("create_date").value,
            time: document.getElementById("create_time").value,
            notes: document.getElementById("create_service").value,
            // Placeholder service selection (TODO: implement proper service UI)
            service_ids: document.getElementById("create_service").value ? [1] : [],
        };

        // Submit appointment to backend API
        const response = await fetch("/api/manual_insert", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(appointmentData),
        });

        if (response.ok) {
            showMessage("Appointment created successfully.");
            // Reset form while preserving date/time defaults and user info
            document.getElementById("form_create").reset();
            document.getElementById("create_date").value = today;
            document.getElementById("create_time").value = currentTime;
            loadUserData(); // Re-populate user information after reset
            fetchAllAppointments(); // Refresh appointment display
        } else {
            const errorData = await response.json();
            showMessage(`Error: ${errorData.error}`, "error");
        }
    });

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
    // APPOINTMENT RESCHEDULING FUNCTIONALITY
    // ========================================================================
    
    /**
     * Handle address selection in reschedule form
     * Populates appointment dropdown with appointments for selected address
     */
    document.getElementById('reschedule_address_select').addEventListener('change', async (e) => {
        const addressId = e.target.value;
        const appointmentSelect = document.getElementById('update_appointment_select');

        // Reset appointment dropdown if no address selected
        if (!addressId) {
            appointmentSelect.innerHTML = '<option value="">-- Select address first --</option>';
            appointmentSelect.disabled = true;
            return;
        }

        try {
            // Fetch all user appointments
            const response = await fetch('/api/appointments');
            if (!response.ok) throw new Error('Failed to fetch appointments');
            const allAppointments = await response.json();
            
            // Filter appointments by selected address
            const filteredAppointments = allAppointments.filter(appt => appt.address_id == addressId);

            if (filteredAppointments.length > 0) {
                // Populate dropdown with matching appointments
                appointmentSelect.innerHTML = '<option value="">-- Select an appointment --</option>';
                appointmentSelect.innerHTML += filteredAppointments.map(appt => 
                    `<option value="${appt.id}">${appt.date} at ${appt.time.slice(0, 5)}</option>`
                ).join('');
                appointmentSelect.disabled = false;
            } else {
                // No appointments found for this address
                appointmentSelect.innerHTML = '<option value="">-- No appointments at this address --</option>';
                appointmentSelect.disabled = true;
            }
        } catch (error) {
            console.error('Error fetching appointments for address:', error);
            appointmentSelect.innerHTML = '<option value="">-- Error loading appointments --</option>';
            appointmentSelect.disabled = true;
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
});



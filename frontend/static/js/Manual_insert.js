document.addEventListener("DOMContentLoaded", () => {
    // --- Set default date and time for the create form ---
    const now = new Date();
    const today = now.toISOString().split("T")[0];
    const currentTime = now.toTimeString().slice(0, 5);
    
    document.getElementById("create_date").value = today;
    document.getElementById("create_time").value = currentTime;

    // --- New function to load user-specific data ---
    const loadUserData = async () => {
        try {
            // Fetch user status to get name/email
            const statusResponse = await fetch('/api/auth/status');
            if (!statusResponse.ok) {
                throw new Error(`Authentication status check failed: ${statusResponse.statusText}`);
            }
            const statusData = await statusResponse.json();
            if (statusData.logged_in) {
                document.getElementById('create_name').value = statusData.user.name;
                document.getElementById('create_email').value = statusData.user.email;
                
                // --- NEW: Set the default notification preference ---
                const userPreference = statusData.user.notification_preference;
                const notificationSelect = document.getElementById('create_notification');
                // Check if the user has a preference and the dropdown exists
                if (userPreference && notificationSelect) {
                    // Set the dropdown's value to match the user's preference
                    notificationSelect.value = userPreference;
                }
                // --- END NEW ---

                // Fetch appointments only AFTER confirming login
                fetchAllAppointments(); 

            } else {
                // If not logged in, we can't load addresses.
                document.getElementById('select_address').innerHTML = '<option value="">Please log in to see addresses</option>';
                // Also clear the appointments table
                document.getElementById("customer-table-container").innerHTML = "<p>Please log in to see your appointments.</p>";
                return; // Stop execution here
            }

            // Fetch user addresses
            const addressResponse = await fetch('/api/user/addresses');
            if (!addressResponse.ok) throw new Error('Failed to fetch addresses');
            const addresses = await addressResponse.json();
            
            // Populate both the 'create' and 'reschedule' address dropdowns
            const createAddressSelect = document.getElementById('select_address');
            const rescheduleAddressSelect = document.getElementById('reschedule_address_select');
            
            const addressOptions = addresses.map(addr => 
                `<option value="${addr.id}">${addr.street_and_number}, ${addr.postal_code} ${addr.city_name}</option>`
            ).join('');

            createAddressSelect.innerHTML = addressOptions;
            // Add a placeholder to the reschedule dropdown
            rescheduleAddressSelect.innerHTML = '<option value="">-- Select an address --</option>' + addressOptions;

        } catch (error) {
            console.error("Error loading user data:", error);
            // This will now correctly display an error message in the dropdown
            document.getElementById('select_address').innerHTML = '<option value="">Error loading addresses</option>';
        }
    };

    // --- Main function to fetch and display all appointments ---
    const fetchAllAppointments = async () => {
        const container = document.getElementById("customer-table-container");
        try {
            // This API endpoint correctly fetches appointments for the logged-in user.
            const response = await fetch("/api/appointments");
            const appointments = await response.json();
            
            // Sort by date and time
            appointments.sort((a, b) => new Date(`${a.date}T${a.time}`) - new Date(`${b.date}T${b.time}`));

            if (appointments.length === 0) {
                container.innerHTML = "<p>You have no upcoming appointments.</p>";
                return;
            }

            // Use the card-based layout from mainpage.js, with an added delete button.
            let content = '<div class="appointments-list">';
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

            // Add the necessary styles for the card layout
            const style = document.createElement('style');
            style.innerHTML = `
                .appointments-list { display: grid; gap: 1em; }
                .appointment-card { display: flex; align-items: center; background-color: #f8f9fa; padding: 1em; border-radius: 12px; border: 1px solid #e9ecef; }
                .appointment-date { text-align: center; margin-right: 1.5em; padding-right: 1.5em; border-right: 1px solid #e9ecef; }
                .appointment-date span { font-size: 1em; color: #666; }
                .appointment-date strong { font-size: 2em; color: #007bff; display: block; }
                .appointment-details { flex-grow: 1; }
                .appointment-details p { margin: 0.25em 0; }
                .appointment-details .address { font-size: 0.9em; color: #555; }
                .appointment-details .notes { font-size: 0.9em; color: #777; font-style: italic; }
                .appointment-actions .delete-btn { padding: 0.5em 1em; }
            `;
            
            container.innerHTML = ""; // Clear previous content
            container.appendChild(style);
            container.innerHTML += content;

        } catch (error) {
            container.innerHTML = "<p>Error loading appointments.</p>";
            console.error("Fetch error:", error);
        }
    };

    // --- Message display helper ---
    const showMessage = (text, type = "success") => {
        const container = document.getElementById("message-container");
        const messageDiv = document.createElement("div");
        messageDiv.className = `alert ${type}`; // Using alert classes for consistency
        messageDiv.textContent = text;
        container.innerHTML = "";
        container.appendChild(messageDiv);
        setTimeout(() => messageDiv.remove(), 4000);
    };

    // --- Form submission handler for creating appointments ---
    document.getElementById("form_create").addEventListener("submit", async (e) => {
        e.preventDefault();

        // The backend now only needs the address_id, not the full address details
        const appointmentData = {
            // name, surname, and email are now handled by the backend based on the logged-in user
            address_id: document.getElementById("select_address").value,
            date: document.getElementById("create_date").value,
            time: document.getElementById("create_time").value,
            notes: document.getElementById("create_service").value,
            // This is still a placeholder for a real service selection UI
            service_ids: document.getElementById("create_service").value ? [1] : [],
        };

        const response = await fetch("/api/manual_insert", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(appointmentData),
        });

        if (response.ok) {
            showMessage("Appointment created successfully.");
            // Don't reset name/email as they are pre-filled
            document.getElementById("form_create").reset();
            document.getElementById("create_date").value = today;
            document.getElementById("create_time").value = currentTime;
            loadUserData(); // Re-fill user info after reset
            fetchAllAppointments();
        } else {
            const errorData = await response.json();
            showMessage(`Error: ${errorData.error}`, "error");
        }
    });

    // --- Event Listener for Delete Buttons in the table ---
    document.getElementById("customer-table-container").addEventListener("click", async (e) => {
        if (e.target && e.target.classList.contains("delete-btn")) {
            const appointmentId = e.target.getAttribute("data-id");
            if (!confirm(`Are you sure you want to permanently delete appointment #${appointmentId}?`)) return;

            // 5. Use a new API endpoint for deletion (you'll need to create this in app.py)
            const response = await fetch(`/api/appointments/${appointmentId}`, { method: "DELETE" });

            if (response.ok) {
                showMessage("Appointment deleted successfully.");
                fetchAllAppointments();
            } else {
                const errorData = await response.json();
                showMessage(`Error: ${errorData.error}`, "error");
            }
        }
    });

    // --- NEW: Event listener for the reschedule address dropdown ---
    document.getElementById('reschedule_address_select').addEventListener('change', async (e) => {
        const addressId = e.target.value;
        const appointmentSelect = document.getElementById('update_appointment_select');

        // If no address is selected, disable and reset the appointment dropdown
        if (!addressId) {
            appointmentSelect.innerHTML = '<option value="">-- Select address first --</option>';
            appointmentSelect.disabled = true;
            return;
        }

        try {
            // Fetch all appointments for the logged-in user
            const response = await fetch('/api/appointments');
            if (!response.ok) throw new Error('Failed to fetch appointments');
            const allAppointments = await response.json();
            
            // Filter the appointments to find ones matching the selected address ID
            const filteredAppointments = allAppointments.filter(appt => appt.address_id == addressId);

            if (filteredAppointments.length > 0) {
                appointmentSelect.innerHTML = '<option value="">-- Select an appointment --</option>';
                appointmentSelect.innerHTML += filteredAppointments.map(appt => 
                    `<option value="${appt.id}">${appt.date} at ${appt.time.slice(0, 5)}</option>`
                ).join('');
                appointmentSelect.disabled = false; // Enable the dropdown
            } else {
                appointmentSelect.innerHTML = '<option value="">-- No appointments at this address --</option>';
                appointmentSelect.disabled = true;
            }
        } catch (error) {
            console.error('Error fetching appointments for address:', error);
            appointmentSelect.innerHTML = '<option value="">-- Error loading appointments --</option>';
            appointmentSelect.disabled = true;
        }
    });

    // --- Initial Load ---
    loadUserData(); // This now handles loading everything in the correct order.
    // fetchAllAppointments(); // DELETED from here to prevent the race condition.
});


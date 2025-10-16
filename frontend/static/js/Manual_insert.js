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
            // Add a check to ensure the response is valid before parsing JSON
            if (!statusResponse.ok) {
                throw new Error(`Authentication status check failed: ${statusResponse.statusText}`);
            }
            const statusData = await statusResponse.json();
            if (statusData.logged_in) {
                document.getElementById('create_name').value = statusData.user.name;
                document.getElementById('create_email').value = statusData.user.email;
            } else {
                // If not logged in, we can't load addresses.
                document.getElementById('select_address').innerHTML = '<option value="">Please log in to see addresses</option>';
                return; // Stop execution here
            }

            // Fetch user addresses
            const addressResponse = await fetch('/api/user/addresses');
            // Add a check here as well
            if (!addressResponse.ok) {
                throw new Error(`Failed to fetch addresses: ${addressResponse.statusText}`);
            }
            const addresses = await addressResponse.json();
            const addressSelect = document.getElementById('select_address');
            
            addressSelect.innerHTML = ''; // Clear loading message
            if (addresses.length > 0) {
                addresses.forEach(addr => {
                    const option = document.createElement('option');
                    option.value = addr.id;
                    option.textContent = `${addr.street_and_number}, ${addr.postal_code} ${addr.city_name}`;
                    addressSelect.appendChild(option);
                });
            } else {
                addressSelect.innerHTML = '<option value="">No addresses found for this user</option>';
            }
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

            // The table is now simplified to remove the redundant "Customer" column.
            const table = document.createElement("table");
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>Date & Time</th>
                        <th>Address</th>
                        <th>Services</th>
                        <th>Notes</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${appointments.map(appt => `
                        <tr>
                            <td>${appt.date} at ${appt.time.slice(0, 5)}</td>
                            <td>${appt.address}</td>
                            <td>${appt.service_names || 'N/A'}</td>
                            <td>${appt.notes || ''}</td>
                            <td>
                                <button class="danger delete-btn" data-id="${appt.id}" title="Delete this appointment">Delete</button>
                            </td>
                        </tr>`).join("")}
                </tbody>`;
            container.innerHTML = "";
            container.appendChild(table);
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

    // --- Initial Load ---
    loadUserData(); // Load user-specific data first
    fetchAllAppointments();
});


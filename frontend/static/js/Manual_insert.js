document.addEventListener("DOMContentLoaded", () => {
    // A shared cache to store appointment data fetched by address
    let appointmentCache = {};

    // --- Set default date and time for inputs ---
    const now = new Date();
    const today = now.toISOString().split("T")[0];
    const currentTime = now.toTimeString().slice(0, 5);
    
    document.getElementById("create_date").value = today;
    document.getElementById("create_time").value = currentTime;
    document.getElementById("update_date").value = today;
    document.getElementById("update_time").value = currentTime;

    // --- Main function to fetch and display all appointments ---
    const fetchAllAppointments = async () => {
        const container = document.getElementById("customer-table-container");
        try {
            const response = await fetch("/api/customers");
            const customers = await response.json();
            customers.sort((a, b) => new Date(a.cleaning_date) - new Date(b.cleaning_date));

            if (customers.length === 0) {
                container.innerHTML = "<p>No appointments yet.</p>";
                return;
            }

            const table = document.createElement("table");
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>Date & Time</th>
                        <th>Customer</th>
                        <th>Address</th>
                        <th>Service / Notes</th>
                        <th>Notification</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${customers.map(c => `
                        <tr>
                            <td>${c.cleaning_date} at ${c.cleaning_time}</td>
                            <td>
                                <strong>${c.name}</strong><br>
                                <small>${c.email || 'No email provided'}</small>
                            </td>
                            <td>${c.address}</td>
                            <td>${c.service || 'N/A'}</td>
                            <td>${c.notification_preference}</td>
                            <td>
                                <button class="danger delete-btn" data-id="${c.id}" title="Delete this appointment">Delete</button>
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
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = text;
        container.innerHTML = "";
        container.appendChild(messageDiv);
        setTimeout(() => messageDiv.remove(), 4000);
    };

    // --- Form submission handlers ---
    document.getElementById("form_create").addEventListener("submit", async (e) => {
        e.preventDefault();
        const appointmentData = {
            name: document.getElementById("create_name").value,
            email: document.getElementById("create_email").value,
            address: document.getElementById("create_address").value,
            cleaning_date: document.getElementById("create_date").value,
            cleaning_time: document.getElementById("create_time").value,
            service: document.getElementById("create_service").value,
            notification_preference: document.getElementById("create_notification").value,
        };

        const response = await fetch("/api/customers", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify(appointmentData),
        });

        if (response.ok) {
            showMessage("Appointment created successfully.");
            e.target.reset();
            document.getElementById("create_date").value = today;
            document.getElementById("create_time").value = currentTime;
            fetchAllAppointments();
        } else {
            const errorData = await response.json();
            showMessage(`Error: ${errorData.error}`, "error");
        }
    });

    document.getElementById("form_update").addEventListener("submit", async (e) => {
        e.preventDefault();
        const appointmentId = document.getElementById("update_appointment_select").value;
        const rescheduleData = {
            new_date: document.getElementById("update_date").value,
            new_time: document.getElementById("update_time").value,
            service: document.getElementById("update_service").value,
            notification_preference: document.getElementById("update_notification").value,
        };

        const response = await fetch(`/api/customers/${appointmentId}`, {
            method: "PUT", headers: { "Content-Type": "application/json" },
            body: JSON.stringify(rescheduleData),
        });

        if (response.ok) {
            showMessage("Appointment rescheduled successfully.");
            e.target.reset();
            document.getElementById("update_date").value = today;
            document.getElementById("update_time").value = currentTime;
            document.getElementById("update_appointment_select").innerHTML = '<option value="">-- Enter address first --</option>';
            document.getElementById("update_appointment_select").disabled = true;
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
            if (!confirm(`Are you sure you want to permanently delete this appointment?`)) return;

            const response = await fetch(`/api/customers/${appointmentId}`, { method: "DELETE" });

            if (response.ok) {
                showMessage("Appointment deleted successfully.");
                fetchAllAppointments();
            } else {
                const errorData = await response.json();
                showMessage(`Error: ${errorData.error}`, "error");
            }
        }
    });

    // --- Dynamic Dropdown & Form Pre-filling Logic ---
    const setupAddressInput = (addressInputId, selectId, isRescheduleForm = false) => {
        const addressInput = document.getElementById(addressInputId);
        const selectElement = document.getElementById(selectId);

        addressInput.addEventListener("input", async (e) => {
            const address = e.target.value.trim();
            selectElement.innerHTML = '<option value="">-- Loading... --</option>';
            if (address.length < 3) {
                selectElement.innerHTML = '<option value="">-- Enter address first --</option>';
                selectElement.disabled = true;
                return;
            }

            try {
                const response = await fetch(`/api/customers/by-address/${encodeURIComponent(address)}`);
                const appointments = await response.json();
                appointmentCache[address] = appointments;

                selectElement.innerHTML = "";
                if (appointments.length > 0) {
                    selectElement.disabled = false;
                    selectElement.innerHTML = '<option value="">-- Select an appointment --</option>';
                    appointments.forEach(app => {
                        const option = document.createElement("option");
                        option.value = app.id;
                        option.textContent = `${app.name} - ${app.cleaning_date} at ${app.cleaning_time}`;
                        selectElement.appendChild(option);
                    });
                } else {
                    selectElement.innerHTML = '<option value="">-- No appointments found --</option>';
                    selectElement.disabled = true;
                }
            } catch (error) {
                console.error("Failed to fetch appointments by address:", error);
            }
        });

        if (isRescheduleForm) {
            selectElement.addEventListener("change", (e) => {
                const selectedId = e.target.value;
                const address = addressInput.value.trim();
                const selectedAppointment = (appointmentCache[address] || []).find(app => app.id === selectedId);

                if (selectedAppointment) {
                    document.getElementById("update_date").value = selectedAppointment.cleaning_date;
                    document.getElementById("update_time").value = selectedAppointment.cleaning_time;
                    document.getElementById("update_service").value = selectedAppointment.service;
                    document.getElementById("update_notification").value = selectedAppointment.notification_preference;
                }
            });
        }
    };

    setupAddressInput("update_address", "update_appointment_select", true);

    // --- Initial Load ---
    fetchAllAppointments();
});


// static/js/manual_insert.js
// this file handles the manual insertion, update, and deletion of customers before database is implemented

document.addEventListener("DOMContentLoaded", () => {
    // Set default date for inputs to today
    const today = new Date().toISOString().split("T")[0];
    document.getElementById("create_date").value = today;
    document.getElementById("update_date").value = today;

    // --- Main function to fetch and display customers ---
    const fetchCustomers = async () => {
        const container = document.getElementById("customer-table-container");
        try {
            const response = await fetch("/api/customers");
            const customers = await response.json();

            if (customers.length === 0) {
                container.innerHTML = "<p>No customers yet.</p>";
                return;
            }

            const table = document.createElement("table");
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Address</th>
                        <th>Cleaning Date</th>
                    </tr>
                </thead>
                <tbody>
                    ${customers
                        .map(
                            (c) => `
                        <tr>
                            <td>${c.name}</td>
                            <td>${c.email}</td>
                            <td>${c.address}</td>
                            <td>${c.cleaning_date}</td>
                        </tr>
                    `
                        )
                        .join("")}
                </tbody>
            `;
            container.innerHTML = ""; // Clear previous content
            container.appendChild(table);
        } catch (error) {
            container.innerHTML = "<p>Error loading customers.</p>";
            console.error("Fetch error:", error);
        }
    };

    // --- Message display helper ---
    const showMessage = (text, type = "success") => {
        const container = document.getElementById("message-container");
        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = text;
        container.innerHTML = ""; // Clear old messages
        container.appendChild(messageDiv);

        setTimeout(() => {
            messageDiv.remove();
        }, 4000); // Message disappears after 4 seconds
    };

    // --- Event Listener for Create Form ---
    document.getElementById("form_create").addEventListener("submit", async (e) => {
        e.preventDefault();
        const customerData = {
            name: document.getElementById("create_name").value,
            email: document.getElementById("create_email").value,
            address: document.getElementById("create_address").value,
            cleaning_date: document.getElementById("create_date").value,
        };

        const response = await fetch("/api/customers", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(customerData),
        });

        if (response.ok) {
            showMessage("Customer created successfully.");
            e.target.reset(); // Clear the form
            document.getElementById("create_date").value = today;
            fetchCustomers(); // Refresh the list
        } else {
            const errorData = await response.json();
            showMessage(`Error: ${errorData.error}`, "error");
        }
    });
    
    // --- Event Listener for Update Form ---
    document.getElementById("form_update").addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("update_email").value;
        const new_date = document.getElementById("update_date").value;

        const response = await fetch(`/api/customers/${email}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ new_date: new_date }),
        });

        if (response.ok) {
            showMessage("Date updated successfully.");
            e.target.reset();
            document.getElementById("update_date").value = today;
            fetchCustomers();
        } else {
            const errorData = await response.json();
            showMessage(`Error: ${errorData.error}`, "error");
        }
    });

    // --- Event Listener for Delete Form ---
    document.getElementById("form_delete").addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("delete_email").value;
        
        // Simple browser confirmation
        if (!confirm(`Are you sure you want to delete the customer with email: ${email}?`)) {
            return;
        }

        const response = await fetch(`/api/customers/${email}`, {
            method: "DELETE",
        });

        if (response.ok) {
            showMessage("Customer deleted successfully.");
            e.target.reset();
            fetchCustomers();
        } else {
            const errorData = await response.json();
            showMessage(`Error: ${errorData.error}`, "error");
        }
    });


    // Initial load of customers when the page starts
    fetchCustomers();
});
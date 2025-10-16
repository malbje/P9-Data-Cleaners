// login.js - Authentication page functionality

document.addEventListener("DOMContentLoaded", () => {
    // Get DOM elements
    const loginForm = document.getElementById('login-form');
    const messageContainer = document.getElementById('message-container');

    // Handle login form submission
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearMessages();
        
        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value; // This is sent but ignored by the backend

        // Basic validation to ensure the user enters an email
        if (!email) {
            showMessage('Please enter an email address.', 'error');
            return;
        }

        if (!isValidEmail(email)) {
            showMessage('Please enter a valid email address.', 'error');
            return;
        }

        try {
            // Call the login API endpoint
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password // The backend will ignore this field
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                showMessage('Login successful! Redirecting...', 'success');
                
                // Redirect to the main dashboard after a short delay
                setTimeout(() => {
                    window.location.href = '/';
                }, 1500);
            } else {
                showMessage(data.error || 'Login failed. Please try again.', 'error');
            }
        } catch (error) {
            console.error('Login error:', error);
            showMessage('An error occurred during login. Please try again.', 'error');
        }
    });

    // --- Utility functions ---

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function showMessage(text, type = 'success') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = text;
        messageContainer.innerHTML = ''; // Clear previous messages
        messageContainer.appendChild(messageDiv);

        // Auto-remove message after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }

    function clearMessages() {
        messageContainer.innerHTML = '';
    }
});
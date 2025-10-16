// login.js - Authentication page functionality

document.addEventListener("DOMContentLoaded", () => {
    // Get DOM elements
    const loginToggle = document.getElementById('login-toggle');
    const signupToggle = document.getElementById('signup-toggle');
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const messageContainer = document.getElementById('message-container');

    // Toggle between login and signup forms
    loginToggle.addEventListener('click', () => {
        switchToLogin();
    });

    signupToggle.addEventListener('click', () => {
        switchToSignup();
    });

    function switchToLogin() {
        loginToggle.classList.add('active');
        signupToggle.classList.remove('active');
        loginForm.classList.add('active');
        signupForm.classList.remove('active');
        clearMessages();
    }

    function switchToSignup() {
        signupToggle.classList.add('active');
        loginToggle.classList.remove('active');
        signupForm.classList.add('active');
        loginForm.classList.remove('active');
        clearMessages();
    }

    // Handle login form submission
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value;
        const rememberMe = document.getElementById('remember-me').checked;

        // Basic validation
        if (!email || !password) {
            showMessage('Please fill in all fields.', 'error');
            return;
        }

        if (!isValidEmail(email)) {
            showMessage('Please enter a valid email address.', 'error');
            return;
        }

        try {
            // Here you would typically make an API call to your backend
            const response = await loginUser({ email, password, rememberMe });
            
            if (response.success) {
                showMessage('Login successful! Redirecting...', 'success');
                
                // Redirect to dashboard after a short delay
                setTimeout(() => {
                    window.location.href = '/';
                }, 1500);
            } else {
                showMessage(response.message || 'Login failed. Please try again.', 'error');
            }
        } catch (error) {
            console.error('Login error:', error);
            showMessage('An error occurred during login. Please try again.', 'error');
        }
    });

    // Handle signup form submission
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const firstname = document.getElementById('signup-firstname').value.trim();
        const lastname = document.getElementById('signup-lastname').value.trim();
        const email = document.getElementById('signup-email').value.trim();
        const phone = document.getElementById('signup-phone').value.trim();
        const password = document.getElementById('signup-password').value;
        const confirmPassword = document.getElementById('signup-confirm-password').value;
        const termsAgreed = document.getElementById('terms-agreement').checked;

        // Validation
        if (!firstname || !lastname || !email || !phone || !password || !confirmPassword) {
            showMessage('Please fill in all fields.', 'error');
            return;
        }

        if (!isValidEmail(email)) {
            showMessage('Please enter a valid email address.', 'error');
            return;
        }

        if (!isValidPhone(phone)) {
            showMessage('Please enter a valid phone number.', 'error');
            return;
        }

        if (password.length < 8) {
            showMessage('Password must be at least 8 characters long.', 'error');
            return;
        }

        if (password !== confirmPassword) {
            showMessage('Passwords do not match.', 'error');
            return;
        }

        if (!termsAgreed) {
            showMessage('Please agree to the Terms of Service and Privacy Policy.', 'error');
            return;
        }

        try {
            // Here you would typically make an API call to your backend
            const response = await createUser({ 
                firstname, 
                lastname, 
                email, 
                phone, 
                password 
            });
            
            if (response.success) {
                showMessage('Account created successfully! Please log in.', 'success');
                
                // Clear form and switch to login
                signupForm.reset();
                setTimeout(() => {
                    switchToLogin();
                }, 2000);
            } else {
                showMessage(response.message || 'Account creation failed. Please try again.', 'error');
            }
        } catch (error) {
            console.error('Signup error:', error);
            showMessage('An error occurred during account creation. Please try again.', 'error');
        }
    });

    // Utility functions
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function isValidPhone(phone) {
        // Basic phone validation - adjust regex based on your requirements
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
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

    // Mock API functions - replace these with actual API calls
    async function loginUser(credentials) {
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: credentials.email,
                    password: credentials.password
                })
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, message: 'Network error occurred' };
        }
    }

    async function createUser(userData) {
        try {
            const response = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Signup error:', error);
            return { success: false, message: 'Network error occurred' };
        }
    }

    // Password visibility toggle (optional enhancement)
    function addPasswordToggle() {
        const passwordFields = document.querySelectorAll('input[type="password"]');
        
        passwordFields.forEach(field => {
            const wrapper = document.createElement('div');
            wrapper.style.position = 'relative';
            field.parentNode.insertBefore(wrapper, field);
            wrapper.appendChild(field);
            
            const toggle = document.createElement('button');
            toggle.type = 'button';
            toggle.innerHTML = '👁️';
            toggle.style.position = 'absolute';
            toggle.style.right = '10px';
            toggle.style.top = '50%';
            toggle.style.transform = 'translateY(-50%)';
            toggle.style.border = 'none';
            toggle.style.background = 'transparent';
            toggle.style.cursor = 'pointer';
            toggle.style.fontSize = '16px';
            
            toggle.addEventListener('click', () => {
                if (field.type === 'password') {
                    field.type = 'text';
                    toggle.innerHTML = '🙈';
                } else {
                    field.type = 'password';
                    toggle.innerHTML = '👁️';
                }
            });
            
            wrapper.appendChild(toggle);
        });
    }

    // Uncomment the line below if you want password visibility toggles
    // addPasswordToggle();
});
// static/js/dashboard.js

document.addEventListener("DOMContentLoaded", () => {
    // Load user information
    loadUserInfo();
    
    // Widget click handlers
    const widgets = document.querySelectorAll('.widget-card');
    
    widgets.forEach(widget => {
        widget.addEventListener('click', () => {
            const widgetType = widget.dataset.widget;
            handleWidgetClick(widgetType);
        });
    });
    
    // Function to handle widget clicks
    function handleWidgetClick(widgetType) {
        switch(widgetType) {
            case 'vejr':
                handleVejrClick();
                break;
            case 'ugeplan':
                handleUgeplanClick();
                break;
            case 'appointments':
                handleAppointmentsClick();
                break;
            case 'profile':
                handleProfileClick();
                break;
            default:
                console.log('Unknown widget type:', widgetType);
        }
    }
    
    // Individual widget handlers
    function handleVejrClick() {
        console.log('Vejr widget clicked');
        // You can add weather functionality here
        // For example: fetch weather data and display it
        alert('Vejr widget clicked! Weather functionality will be implemented here.');
    }
    
    function handleUgeplanClick() {
        console.log('Ugeplan widget clicked');
        // You can add weekly plan functionality here
        // For example: navigate to weekly schedule view
        alert('Ugeplan widget clicked! Weekly schedule functionality will be implemented here.');
    }
    
    function handleAppointmentsClick() {
        console.log('Appointments widget clicked');
        // You can add appointments functionality here
        // For example: show upcoming appointments
        alert('Upcoming Appointments widget clicked! Appointments functionality will be implemented here.');
    }
    
    function handleProfileClick() {
        console.log('Profile widget clicked');
        // You can add profile functionality here
        // For example: navigate to user profile page
        alert('My Profile widget clicked! Profile functionality will be implemented here.');
    }
    
    // Chatbot functionality
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    
    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const userMessage = chatInput.value.trim();
            
            if (userMessage) {
                // Add user message to chat
                addMessageToChat(userMessage, 'user');
                
                // Clear input
                chatInput.value = '';
                
                // Simulate bot response (you can replace this with actual chatbot logic)
                setTimeout(() => {
                    const botResponse = generateBotResponse(userMessage);
                    addMessageToChat(botResponse, 'bot');
                }, 1000);
            }
        });
    }
    
    function addMessageToChat(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function generateBotResponse(userMessage) {
        // Simple bot responses - you can enhance this with actual AI/NLP
        const lowerMessage = userMessage.toLowerCase();
        
        if (lowerMessage.includes('booking') || lowerMessage.includes('book')) {
            return 'I can help you book a cleaning! Please provide the customer details and preferred date.';
        } else if (lowerMessage.includes('vejr') || lowerMessage.includes('weather')) {
            return 'For weather information, click on the Vejr widget in the dashboard.';
        } else if (lowerMessage.includes('schedule') || lowerMessage.includes('ugeplan')) {
            return 'To view the weekly schedule, click on the Ugeplan widget.';
        } else if (lowerMessage.includes('appointment')) {
            return 'To see upcoming appointments, click on the Upcoming Appointments widget.';
        } else {
            return 'I\'m here to help with booking and scheduling. What would you like to do?';
        }
    }
    
    // Load user information
    async function loadUserInfo() {
        try {
            const response = await fetch('/api/auth/status');
            const data = await response.json();
            
            if (data.logged_in) {
                const userInfo = document.getElementById('user-info');
                if (userInfo) {
                    userInfo.textContent = `Welcome, ${data.user.name}`;
                }
            } else {
                // Redirect to login if not logged in
                window.location.href = '/login';
            }
        } catch (error) {
            console.error('Error loading user info:', error);
            // Redirect to login on error
            window.location.href = '/login';
        }
    }
});
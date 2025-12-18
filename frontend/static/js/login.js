/**
 * @fileoverview Authentication system for Unit Cleaning application
 * Handles both login and signup functionality with form validation and API integration
 * Supports both single-form and dual-form layouts with defensive programming
 * @author Unit Cleaning Team
 * @version 1.0.0
 */

// ============================================================================
// AUTHENTICATION SYSTEM INITIALIZATION
// ============================================================================

/**
 * Main authentication system entry point
 * Initializes login and signup forms when DOM is ready
 * Uses defensive programming to handle missing elements gracefully
 */
function initAuth() {
  // ========================================================================
  // DOM ELEMENT REFERENCES
  // Safe element lookups with null-checking for defensive programming
  // ========================================================================
  
  /** @type {HTMLElement|null} Toggle button for login form */
  const loginToggle = document.getElementById("login-toggle");
  
  /** @type {HTMLElement|null} Toggle button for signup form */
  const signupToggle = document.getElementById("signup-toggle");
  
  /** @type {HTMLFormElement|null} Login form element */
  const loginForm = document.getElementById("login-form");
  
  /** @type {HTMLFormElement|null} Signup form element */
  const signupForm = document.getElementById("signup-form");
  
  /** @type {HTMLElement|null} Container for displaying messages to user */
  const messageContainer = document.getElementById("message-container");

  // ========================================================================
  // VALIDATION UTILITIES
  // Shared validation functions for form inputs
  // ========================================================================
  
  /**
   * Validates email address format using regex
   * @param {string} email - Email address to validate
   * @returns {boolean} True if email format is valid
   */
  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // NOTE: phone validation and phone usage removed as requested

  // ========================================================================
  // USER FEEDBACK SYSTEM
  // Functions for displaying messages and notifications to users
  // ========================================================================

  /**
   * Display a message to the user with automatic dismissal
   * Falls back to alert() if message container is not available
   * @param {string} text - Message text to display
   * @param {string} [type="success"] - Message type: "success", "error", "info"
   */
  function showMessage(text, type = "success") {
    const div = document.createElement("div");
    div.className = `message ${type}`;
    div.textContent = text;
    if (messageContainer) {
      messageContainer.innerHTML = "";
      messageContainer.appendChild(div);
      setTimeout(() => div.parentNode && div.remove(), 5000);
    } else {
      // fallback if no container
      alert(`${type.toUpperCase()}: ${text}`);
    }
  }

  /**
   * Clear all existing messages from the message container
   * Safe to call even if message container doesn't exist
   */
  function clearMessages() {
    if (messageContainer) messageContainer.innerHTML = "";
  }

  // ========================================================================
  // FORM TOGGLE SYSTEM
  // Functions for switching between login and signup forms
  // ========================================================================

  /**
   * Switch interface to show login form
   * Updates toggle button states and form visibility
   * Only works when both login and signup forms are present
   */
  function switchToLogin() {
    // If signup form is absent (we are on separate pages), fetch login fragment
    if (!loginForm) {
      fetchAndSwap('/login', 'login-form');
      return;
    }
    if (!loginForm || !signupForm) return;
    loginToggle && loginToggle.classList.add("active");
    signupToggle && signupToggle.classList.remove("active");
    loginForm.classList.add("active");
    signupForm.classList.remove("active");
    clearMessages();
  }

  /**
   * Switch interface to show signup form
   * Updates toggle button states and form visibility
   * Only works when both login and signup forms are present
   */
  function switchToSignup() {
    // If signup form is absent (we are on separate pages), fetch signup fragment
    if (!signupForm) {
      fetchAndSwap('/signup', 'signup-form');
      return;
    }
    if (!loginForm || !signupForm) return;
    signupToggle && signupToggle.classList.add("active");
    loginToggle && loginToggle.classList.remove("active");
    signupForm.classList.add("active");
    loginForm.classList.remove("active");
    clearMessages();
  }

  /**
   * Initialize toggle button event listeners
   * Uses safe chaining to avoid errors if elements don't exist
   */
  // Use SPA-like handlers: prevent default, fetch fragment if needed and update history
  loginToggle && loginToggle.addEventListener("click", (e) => {
    e.preventDefault();
    switchToLogin();
    try { history.replaceState(null, '', '/login'); } catch (err) {}
  });
  signupToggle && signupToggle.addEventListener("click", (e) => {
    e.preventDefault();
    switchToSignup();
    try { history.replaceState(null, '', '/signup'); } catch (err) {}
  });

  /**
   * Fetch another auth page and swap its form into the current `.auth-card`.
   * If the fetched page has an element with id=formId we replace/add it.
   */
  async function fetchAndSwap(url, formId) {
    try {
      const res = await fetch(url, { credentials: 'same-origin' });
      if (!res.ok) return;
      const text = await res.text();
      const parser = new DOMParser();
      const doc = parser.parseFromString(text, 'text/html');
      const newForm = doc.getElementById(formId);
      const currentCard = document.querySelector('.auth-card');
      if (!currentCard) return;
      if (newForm) {
        const existing = currentCard.querySelector(`#${formId}`);
        if (existing) existing.replaceWith(newForm);
        else currentCard.appendChild(newForm);
      }
      // Re-run message bindings / event setup by reloading script behaviors
      // The current script remains; re-query elements and bind handlers for new nodes.
      // Simple approach: reload the page script by calling its init (re-run DOMContentLoaded handlers)
      // but here we'll manually re-run the submit listeners for forms present.
      // Bind login handler if new login form present
  const refreshedLoginForm = document.getElementById('login-form');
  const refreshedSignupForm = document.getElementById('signup-form');
  // Re-run init to bind handlers for any newly injected forms
  try { initAuth(); } catch (err) { console.error('re-init error', err); }
    } catch (err) {
      console.error('fetchAndSwap error', err);
    }
  }

  // ========================================================================
  // API COMMUNICATION
  // Wrapper functions for backend API calls with error handling
  // ========================================================================

  /**
   * Send JSON POST request to API endpoint
   * Handles various response formats and provides normalized return values
   * @param {string} url - API endpoint URL
   * @param {Object} body - Request body data to send as JSON
   * @returns {Promise<{success: boolean, data: any, message: string, status: number}>} Normalized response
   */
  async function postJSON(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    let data = null;
    try {
      data = await res.json();
    } catch (_) {
      // ignore parse errors; treat as generic failure
    }
    // Normalize: success if res.ok or data?.success === true
    const success = res.ok || (data && data.success === true);
    const message =
      (data && (data.message || data.error)) ||
      (res.ok ? "OK" : "Request failed");
    return { success, data, message, status: res.status };
  }

  // ========================================================================
  // LOGIN FORM HANDLING
  // Processes login form submission with validation and API integration
  // ========================================================================

  /**
   * Initialize login form submission handler
   * Handles form validation, API communication, and user feedback
   * Works even if backend ignores password field
   */
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      clearMessages();

      const email = (document.getElementById("login-email")?.value || "").trim();
      const password = document.getElementById("login-password")?.value || "";
      const rememberMe = !!document.getElementById("remember-me")?.checked;

      // Perform client-side validation before API call (what api call exactly???)
      if (!email) {
        showMessage("Please enter an email address.", "error");
        return;
      }
      if (!isValidEmail(email)) {
        showMessage("Please enter a valid email address.", "error");
        return;
      }

      try {
        const { success, data, message } = await postJSON("/api/auth/login", {
          email,
          password,     
          rememberMe,
        });

        if (success) {
          showMessage("Login successful! Redirecting...", "success");
          setTimeout(() => (window.location.href = "/"), 1500);
        } else {
          showMessage(
            message || data?.error || "Login failed. Please try again.",
            "error"
          );
        }
      } catch (err) {
        console.error("Login error:", err);
        showMessage("An error occurred during login. Please try again.", "error");
      }
    });
  }

  // ========================================================================
  // SIGNUP FORM HANDLING
  // Removed from this file — signup is now handled in frontend/static/js/signup.js
  // ========================================================================

  // ========================================================================
  // PASSWORD VISIBILITY TOGGLE (OPTIONAL FEATURE)
  // Adds show/hide functionality to password fields
  // ========================================================================

  /**
   * Add password visibility toggle buttons to all password fields
   * Creates eye icons that allow users to show/hide password text
   * Call this function to enable password visibility toggles
   * Currently commented out - uncomment the call above to enable
   */
  function addPasswordToggle() {
    const passwordFields = document.querySelectorAll('input[type="password"]');
    passwordFields.forEach((field) => {
      const wrapper = document.createElement("div");
      wrapper.style.position = "relative";
      field.parentNode.insertBefore(wrapper, field);
      wrapper.appendChild(field);

      const toggle = document.createElement("button");
      toggle.type = "button";
      toggle.innerHTML = "👁️";
      toggle.style.position = "absolute";
      toggle.style.right = "10px";
      toggle.style.top = "50%";
      toggle.style.transform = "translateY(-50%)";
      toggle.style.border = "none";
      toggle.style.background = "transparent";
      toggle.style.cursor = "pointer";
      toggle.style.fontSize = "16px";

      toggle.addEventListener("click", () => {
        if (field.type === "password") {
          field.type = "text";
          toggle.innerHTML = "🙈";
        } else {
          field.type = "password";
          toggle.innerHTML = "👁️";
        }
      });

      wrapper.appendChild(toggle);
    });
  }
}

// Auto-init on first DOM ready
document.addEventListener('DOMContentLoaded', () => {
  try {
    initAuth();
  } catch (err) {
    console.error('Failed to initialize auth handlers:', err);
  }
});

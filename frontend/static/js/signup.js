/*
  signup.js

  Purpose of sections:
  - Helpers: validation and UI helpers (isValidEmail, showMessage, postJSON).
  - initSignup: main form hookup, input collection, basic validation,
                sending payload to backend and handling response.
  - DOMContentLoaded: initializes the signup handler when the page is ready.
*/

(function () {
  // --- Helpers -------------------------------------------------------------
  // Validate a basic email shape
  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  // Show a brief message to the user; falls back to alert if no container
  function showMessage(container, text, type = "success") {
    const div = document.createElement("div");
    div.className = `message ${type}`;
    div.textContent = text;
    if (container) {
      container.innerHTML = "";
      container.appendChild(div);
      setTimeout(() => div.parentNode && div.remove(), 5000);
    } else {
      alert(`${type.toUpperCase()}: ${text}`);
    }
  }

  function clearMessages(container) {
    if (container) container.innerHTML = "";
  }

  // Minimal fetch wrapper for JSON POST
  async function postJSON(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      credentials: "same-origin",
    });
    let data = null;
    try { data = await res.json(); } catch (_) {}
    const success = res.ok || (data && data.success === true);
    const message = (data && (data.message || data.error)) || (res.ok ? "OK" : "Request failed");
    return { success, data, message, status: res.status };
  }

  // --- Main initialization -------------------------------------------------
  function initSignup() {
    const signupForm = document.getElementById("signup-form");
    if (!signupForm) return; // nothing to do on pages without the form

    // Toggle buttons: redirect to login when clicking "Log In"
    const loginToggle = document.getElementById("login-toggle");
    if (loginToggle) {
      loginToggle.addEventListener("click", (e) => {
        e.preventDefault();
        window.location.href = "/login";
      });
    }
    // Keep signup-toggle from doing anything unexpected
    const signupToggle = document.getElementById("signup-toggle");
    if (signupToggle) {
      signupToggle.addEventListener("click", (e) => e.preventDefault());
    }

    const messageContainer = document.getElementById("message-container");
    const submitBtn = signupForm.querySelector('button[type="submit"]') || null;

    signupForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      clearMessages(messageContainer);

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.dataset.origText = submitBtn.textContent || "";
        submitBtn.textContent = "Registering...";
      }

      const name = (document.getElementById("signup-firstname")?.value || "").trim();
      const surname = (document.getElementById("signup-lastname")?.value || "").trim();
      const email = (document.getElementById("signup-email")?.value || "").trim();
      const street = (document.getElementById("signup-street")?.value || "").trim();
      const postal = (document.getElementById("signup-postal")?.value || "").trim();
      const city = (document.getElementById("signup-city")?.value || "").trim();
      const notifications = (document.getElementById("signup-notifications")?.value || "none");

      if (!name || !surname || !email) {
        showMessage(messageContainer, "Please provide first name, last name and email.", "error");
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = submitBtn.dataset.origText || "Create account"; }
        return;
      }
      if (!isValidEmail(email)) {
        showMessage(messageContainer, "Please enter a valid email address.", "error");
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = submitBtn.dataset.origText || "Create account"; }
        return;
      }
      if (!street || !postal || !city) {
        showMessage(messageContainer, "Please provide a full address (street, postal code and city).", "error");
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = submitBtn.dataset.origText || "Create account"; }
        return;
      }

      const payload = {
        name,
        surname,
        email,
        address: {
          street_and_number: street,
          postal_code: postal,
          city_name: city
        },
        notifications
      };

      try {
        const { success, data, message } = await postJSON("/api/customers", payload);
        if (success) {
          const cid = data?.customer_id ? `Customer ID: ${data.customer_id}` : "";
          const aid = data?.address_id ? ` Address ID: ${data.address_id}` : "";
          showMessage(messageContainer, (data?.message || "Registered successfully.") + " " + cid + aid, "success");
          signupForm.reset();
          if (submitBtn) submitBtn.textContent = "Registered ✓";
          // Redirect to login (signup confirmation page removed)
          setTimeout(() => { window.location.href = "/login"; }, 1100);
        } else {
          showMessage(messageContainer, message || data?.error || "Registration failed.", "error");
          if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = submitBtn.dataset.origText || "Create account"; }
        }
      } catch (err) {
        // Network or unexpected error
        showMessage(messageContainer, "Network or server error.", "error");
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = submitBtn.dataset.origText || "Create account"; }
      }
    });
  }

  // Initialize when DOM is ready
  document.addEventListener("DOMContentLoaded", initSignup);
})();
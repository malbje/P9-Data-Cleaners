// auth.js — Login + optional Signup (safe-merge, defensive)

document.addEventListener("DOMContentLoaded", () => {
  // ---- DOM lookups (some may be absent; we guard below) ----
  const loginToggle = document.getElementById("login-toggle");
  const signupToggle = document.getElementById("signup-toggle");
  const loginForm = document.getElementById("login-form");
  const signupForm = document.getElementById("signup-form");
  const messageContainer = document.getElementById("message-container");

  // ---- Utilities (shared) ----
  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  function isValidPhone(phone) {
    // basic international-ish check, allows leading +
    if (!phone) return false;
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ""));
  }

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

  function clearMessages() {
    if (messageContainer) messageContainer.innerHTML = "";
  }

  // ---- Toggle helpers (only if both forms exist) ----
  function switchToLogin() {
    if (!loginForm || !signupForm) return;
    loginToggle && loginToggle.classList.add("active");
    signupToggle && signupToggle.classList.remove("active");
    loginForm.classList.add("active");
    signupForm.classList.remove("active");
    clearMessages();
  }

  function switchToSignup() {
    if (!loginForm || !signupForm) return;
    signupToggle && signupToggle.classList.add("active");
    loginToggle && loginToggle.classList.remove("active");
    signupForm.classList.add("active");
    loginForm.classList.remove("active");
    clearMessages();
  }

  // Wire up toggles (if they exist)
  loginToggle && loginToggle.addEventListener("click", switchToLogin);
  signupToggle && signupToggle.addEventListener("click", switchToSignup);

  // ---- API wrappers (handle both response styles) ----
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

  // ---- LOGIN (works even if password is ignored by backend) ----
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      clearMessages();

      const email = (document.getElementById("login-email")?.value || "").trim();
      const password = document.getElementById("login-password")?.value || "";
      const rememberMe = !!document.getElementById("remember-me")?.checked;

      // Basic validation — original file only required email, but we’ll allow
      // empty password if your backend ignores it.
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
          password, // backend may ignore this; safe to send
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

  // ---- SIGNUP (only wired if the form exists) ----
  if (signupForm) {
    signupForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      clearMessages();

      const firstname = (document.getElementById("signup-firstname")?.value || "").trim();
      const lastname = (document.getElementById("signup-lastname")?.value || "").trim();
      const email = (document.getElementById("signup-email")?.value || "").trim();
      const phone = (document.getElementById("signup-phone")?.value || "").trim();
      const password = document.getElementById("signup-password")?.value || "";
      const confirmPassword =
        document.getElementById("signup-confirm-password")?.value || "";
      const termsAgreed = !!document.getElementById("terms-agreement")?.checked;

      // Validations (from your signup file)
      if (!firstname || !lastname || !email || !phone || !password || !confirmPassword) {
        showMessage("Please fill in all fields.", "error");
        return;
      }
      if (!isValidEmail(email)) {
        showMessage("Please enter a valid email address.", "error");
        return;
      }
      if (!isValidPhone(phone)) {
        showMessage("Please enter a valid phone number.", "error");
        return;
      }
      if (password.length < 8) {
        showMessage("Password must be at least 8 characters long.", "error");
        return;
      }
      if (password !== confirmPassword) {
        showMessage("Passwords do not match.", "error");
        return;
      }
      if (!termsAgreed) {
        showMessage(
          "Please agree to the Terms of Service and Privacy Policy.",
          "error"
        );
        return;
      }

      try {
        const { success, data, message } = await postJSON("/api/auth/signup", {
          firstname,
          lastname,
          email,
          phone,
          password,
        });

        if (success) {
          showMessage("Account created successfully! Please log in.", "success");
          signupForm.reset();
          // If you have toggles/forms for both, switch back to login
          setTimeout(() => switchToLogin(), 1200);
        } else {
          showMessage(
            message || data?.error || "Account creation failed. Please try again.",
            "error"
          );
        }
      } catch (err) {
        console.error("Signup error:", err);
        showMessage(
          "An error occurred during account creation. Please try again.",
          "error"
        );
      }
    });
  }

  // ---- Optional: password visibility toggles (call if you want) ----
  // addPasswordToggle();

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
});

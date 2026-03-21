document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;
    const authPanel = document.querySelector(".auth-panel");
    const authCloseButton = document.querySelector(".auth-panel-close");
    const openButtons = Array.from(document.querySelectorAll("[data-auth-modal-open]"));
    const closeButtons = Array.from(document.querySelectorAll("[data-auth-modal-close]"));
    const mobileQuery = window.matchMedia("(max-width: 860px)");

    function syncCloseButtonVisibility() {
        if (!(authCloseButton instanceof HTMLElement)) {
            return;
        }
        const shouldShow = mobileQuery.matches && body.classList.contains("auth-modal-open");
        authCloseButton.hidden = !shouldShow;
    }

    function syncAuthModalMode() {
        const isMobile = mobileQuery.matches;
        body.classList.toggle("auth-mobile-ready", isMobile);
        if (!isMobile) {
            body.classList.remove("auth-modal-open");
        }
        syncCloseButtonVisibility();
    }

    function openAuthModal() {
        if (!mobileQuery.matches || !(authPanel instanceof HTMLElement)) {
            return;
        }
        body.classList.add("auth-modal-open");
        syncCloseButtonVisibility();
        const firstField = authPanel.querySelector("input, button, textarea, select");
        if (firstField instanceof HTMLElement) {
            window.setTimeout(() => firstField.focus(), 40);
        }
    }

    function closeAuthModal() {
        if (!mobileQuery.matches) {
            return;
        }
        body.classList.remove("auth-modal-open");
        syncCloseButtonVisibility();
    }

    syncAuthModalMode();
    if (typeof mobileQuery.addEventListener === "function") {
        mobileQuery.addEventListener("change", syncAuthModalMode);
    } else if (typeof mobileQuery.addListener === "function") {
        mobileQuery.addListener(syncAuthModalMode);
    }

    openButtons.forEach((button) => {
        button.addEventListener("click", openAuthModal);
    });

    closeButtons.forEach((button) => {
        button.addEventListener("click", closeAuthModal);
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeAuthModal();
        }
    });

    if (mobileQuery.matches && document.querySelector(".field-error, .form-alert-error")) {
        openAuthModal();
    }

    const guidance = document.querySelector("[data-password-guidance]");
    if (!(guidance instanceof HTMLElement)) {
        return;
    }

    const passwordInput = document.getElementById(guidance.dataset.passwordInputId || "");
    if (!(passwordInput instanceof HTMLInputElement)) {
        return;
    }

    const usernameInput = document.getElementById(guidance.dataset.usernameInputId || "");
    const emailInput = document.getElementById(guidance.dataset.emailInputId || "");
    const firstNameInput = document.getElementById(guidance.dataset.firstNameInputId || "");

    const commonPasswords = new Set([
        "12345678",
        "password",
        "password123",
        "azerty123",
        "qwerty123",
        "admin123",
        "trading123",
        "welcome123",
        "123456789",
        "motdepasse",
    ]);

    const rules = {
        length: guidance.querySelector('[data-password-rule="length"]'),
        numeric: guidance.querySelector('[data-password-rule="numeric"]'),
        personal: guidance.querySelector('[data-password-rule="personal"]'),
        common: guidance.querySelector('[data-password-rule="common"]'),
    };

    function normalize(value) {
        return String(value || "").trim().toLowerCase();
    }

    function splitTokens(value) {
        return normalize(value)
            .split(/[^a-z0-9]+/i)
            .map((token) => token.trim())
            .filter((token) => token.length >= 3);
    }

    function setRuleState(ruleNode, state) {
        if (!(ruleNode instanceof HTMLElement)) {
            return;
        }
        ruleNode.classList.remove("is-met", "is-failed");
        if (state === "met") {
            ruleNode.classList.add("is-met");
        } else if (state === "failed") {
            ruleNode.classList.add("is-failed");
        }
    }

    function evaluatePassword() {
        const password = passwordInput.value || "";
        const normalizedPassword = normalize(password);
        const hasValue = password.length > 0;

        guidance.hidden = !hasValue;

        if (!hasValue) {
            Object.values(rules).forEach((ruleNode) => setRuleState(ruleNode, "idle"));
            return;
        }

        const identityTokens = [
            ...(usernameInput instanceof HTMLInputElement ? splitTokens(usernameInput.value) : []),
            ...(emailInput instanceof HTMLInputElement ? splitTokens(emailInput.value) : []),
            ...(firstNameInput instanceof HTMLInputElement ? splitTokens(firstNameInput.value) : []),
        ];

        const hasPersonalInfo = identityTokens.some((token) => normalizedPassword.includes(token));

        setRuleState(rules.length, password.length >= 8 ? "met" : "failed");
        setRuleState(rules.numeric, /^\d+$/.test(password) ? "failed" : "met");
        setRuleState(rules.personal, hasPersonalInfo ? "failed" : "met");
        setRuleState(rules.common, commonPasswords.has(normalizedPassword) ? "failed" : "met");
    }

    passwordInput.addEventListener("input", evaluatePassword);

    [usernameInput, emailInput, firstNameInput].forEach((input) => {
        if (input instanceof HTMLInputElement) {
            input.addEventListener("input", evaluatePassword);
        }
    });

    evaluatePassword();
    syncCloseButtonVisibility();
});

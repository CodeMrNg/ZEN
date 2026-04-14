(function () {
    const langCode = (document.documentElement.lang || "fr").toLowerCase();
    const strings = langCode.startsWith("fr") ? {
        loading: "Chargement...",
        activating: "Activation...",
        accountSwitchFailed: "Le changement de compte a echoue.",
    } : {
        loading: "Loading...",
        activating: "Activating...",
        accountSwitchFailed: "Account switch failed.",
    };

    function getCsrfToken() {
        const match = document.cookie.match(/csrftoken=([^;]+)/);
        return match ? decodeURIComponent(match[1]) : "";
    }

    function escapeHtml(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function setButtonLoading(button, isLoading, loadingText) {
        if (!(button instanceof HTMLButtonElement)) {
            return;
        }

        if (isLoading) {
            if (!button.dataset.restoreHtml) {
                button.dataset.restoreHtml = button.innerHTML;
            }

            const label = loadingText || button.dataset.loadingText || button.textContent.trim() || strings.loading;
            button.classList.add("is-loading");
            button.disabled = true;
            button.setAttribute("aria-busy", "true");
            button.innerHTML = `
                <span class="button-spinner" aria-hidden="true"></span>
                <span class="button-label">${escapeHtml(label)}</span>
            `;
            return;
        }

        if (button.dataset.restoreHtml) {
            button.innerHTML = button.dataset.restoreHtml;
            delete button.dataset.restoreHtml;
        }

        button.classList.remove("is-loading");
        button.removeAttribute("aria-busy");
        button.disabled = false;
    }

    function togglePageLoader(loader, isLoading, message) {
        if (!(loader instanceof HTMLElement)) {
            return;
        }

        const copyNode = loader.querySelector("[data-loader-copy]");
        if (message && copyNode) {
            copyNode.textContent = message;
        }

        loader.hidden = !isLoading;
        loader.setAttribute("aria-hidden", String(!isLoading));
    }

    function getUiModals() {
        return Array.from(document.querySelectorAll(".trade-modal, .dashboard-modal"));
    }

    function syncModalOpenState() {
        const hasOpenModal = getUiModals().some((modal) => !modal.hidden);
        document.body.classList.toggle("modal-open", hasOpenModal);
    }

    function openModalById(id) {
        const modal = document.getElementById(id);
        if (!(modal instanceof HTMLElement)) {
            return;
        }

        const parentModal = modal.closest(".trade-modal, .dashboard-modal");
        if (parentModal && parentModal !== modal && !parentModal.hidden) {
            closeModal(parentModal);
        }

        modal.hidden = false;
        modal.setAttribute("aria-hidden", "false");
        syncModalOpenState();
    }

    function closeModal(modal) {
        if (!(modal instanceof HTMLElement)) {
            return;
        }

        modal.hidden = true;
        modal.setAttribute("aria-hidden", "true");
        syncModalOpenState();
    }

    function showUiToast(message, tone = "error") {
        const toast = document.createElement("div");
        toast.className = `ui-toast is-${tone}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        window.setTimeout(() => {
            toast.classList.add("is-visible");
        }, 10);
        window.setTimeout(() => {
            toast.classList.remove("is-visible");
            window.setTimeout(() => toast.remove(), 200);
        }, 3200);
    }

    function bindUiModals() {
        document.addEventListener("click", (event) => {
            const openButton = event.target.closest("[data-ui-modal-open]");
            if (openButton instanceof HTMLElement) {
                event.preventDefault();
                const targetId = openButton.dataset.uiModalOpen;
                const currentModal = openButton.closest(".trade-modal, .dashboard-modal");
                if (currentModal && currentModal.id && currentModal.id !== targetId) {
                    closeModal(currentModal);
                }
                openModalById(targetId);
                return;
            }

            const closeButton = event.target.closest("[data-ui-modal-close]");
            if (closeButton instanceof HTMLElement) {
                event.preventDefault();
                const targetId = closeButton.dataset.uiModalClose;
                const targetModal = targetId
                    ? document.getElementById(targetId)
                    : closeButton.closest(".trade-modal, .dashboard-modal");
                closeModal(targetModal);
            }
        });

        document.addEventListener("keydown", (event) => {
            if (event.key !== "Escape") {
                return;
            }

            const openModals = getUiModals().filter((modal) => !modal.hidden);
            const topModal = openModals[openModals.length - 1];
            if (topModal) {
                closeModal(topModal);
            }
        });

        syncModalOpenState();
    }

    function bindConfirmButtons() {
        document.addEventListener("click", (event) => {
            const button = event.target.closest("[data-confirm-message]");
            if (!(button instanceof HTMLButtonElement)) {
                return;
            }

            const message = button.dataset.confirmMessage;
            if (message && !window.confirm(message)) {
                event.preventDefault();
            }
        });
    }

    function bindAccountSwitcher() {
        document.addEventListener("click", async (event) => {
            const button = event.target.closest("[data-account-switch-button]");
            if (!(button instanceof HTMLButtonElement)) {
                return;
            }

            const modal = button.closest("[data-switch-account-modal]")
                || document.querySelector("[data-switch-account-modal]");
            if (!(modal instanceof HTMLElement)) {
                return;
            }

            const endpoint = modal.dataset.switchAccountUrl;
            const accountId = button.dataset.accountId;
            if (!endpoint || !accountId) {
                return;
            }

            setButtonLoading(button, true, button.dataset.loadingText || strings.activating);

            try {
                const formData = new FormData();
                formData.append("account_id", accountId);

                const response = await fetch(endpoint, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCsrfToken(),
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    body: formData,
                });
                const payload = await response.json();

                if (!response.ok || !payload.ok) {
                    throw new Error(payload.message || strings.accountSwitchFailed);
                }

                window.location.reload();
            } catch (error) {
                setButtonLoading(button, false);
                showUiToast(error.message || strings.accountSwitchFailed);
            }
        });
    }

    function bindAccountEditButtons() {
        const accountIdInput = document.getElementById("edit-account-id");
        const nameInput = document.getElementById("id_edit-account-name");
        const brokerInput = document.getElementById("id_edit-account-broker");
        const identifierInput = document.getElementById("id_edit-account-account_identifier");
        const capitalInput = document.getElementById("id_edit-account-capital_base");
        const currencyInput = document.getElementById("id_edit-account-currency");
        const activeInput = document.getElementById("id_edit-account-set_active");

        document.addEventListener("click", (event) => {
            const button = event.target.closest("[data-account-edit-button]");
            if (!(button instanceof HTMLButtonElement)) {
                return;
            }

            if (accountIdInput) {
                accountIdInput.value = button.dataset.accountId || "";
            }
            if (nameInput) {
                nameInput.value = button.dataset.accountName || "";
            }
            if (brokerInput) {
                brokerInput.value = button.dataset.accountBroker || "";
            }
            if (identifierInput) {
                identifierInput.value = button.dataset.accountIdentifier || "";
            }
            if (capitalInput) {
                capitalInput.value = button.dataset.accountCapital || "";
            }
            if (currencyInput) {
                currencyInput.value = button.dataset.accountCurrency || "";
            }
            if (activeInput) {
                activeInput.checked = button.dataset.accountActive === "true";
            }
        });
    }

    function bindLanguageSwitcher() {
        const switcher = document.querySelector("[data-language-switcher]");
        const trigger = switcher?.querySelector("[data-language-switcher-trigger]");
        const menu = switcher?.querySelector(".language-switcher-menu");
        if (!(switcher instanceof HTMLElement) || !(trigger instanceof HTMLButtonElement) || !(menu instanceof HTMLElement)) {
            return;
        }

        function closeMenu() {
            menu.hidden = true;
            switcher.classList.remove("is-open");
            trigger.setAttribute("aria-expanded", "false");
        }

        function openMenu() {
            menu.hidden = false;
            switcher.classList.add("is-open");
            trigger.setAttribute("aria-expanded", "true");
        }

        trigger.addEventListener("click", (event) => {
            event.preventDefault();
            if (menu.hidden) {
                openMenu();
                return;
            }
            closeMenu();
        });

        document.addEventListener("click", (event) => {
            if (!switcher.contains(event.target)) {
                closeMenu();
            }
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                closeMenu();
            }
        });

        closeMenu();
    }

    function bindSidebarMenu() {
        const sidebars = Array.from(document.querySelectorAll("[data-sidebar]"));
        if (!sidebars.length) {
            return;
        }

        const mobileViewport = window.matchMedia("(max-width: 1180px)");

        function setSidebarState(sidebar, isOpen) {
            if (!(sidebar instanceof HTMLElement)) {
                return;
            }

            const toggle = sidebar.querySelector("[data-sidebar-menu-toggle]");
            if (!(toggle instanceof HTMLButtonElement)) {
                return;
            }

            sidebar.classList.toggle("is-mobile-open", isOpen && mobileViewport.matches);
            toggle.setAttribute("aria-expanded", String(isOpen && mobileViewport.matches));
            const label = isOpen && mobileViewport.matches
                ? toggle.dataset.closeLabel
                : toggle.dataset.openLabel;
            if (label) {
                toggle.setAttribute("aria-label", label);
            }
        }

        function closeAllSidebars() {
            sidebars.forEach((sidebar) => setSidebarState(sidebar, false));
        }

        sidebars.forEach((sidebar) => {
            const toggle = sidebar.querySelector("[data-sidebar-menu-toggle]");
            if (!(toggle instanceof HTMLButtonElement)) {
                return;
            }

            toggle.addEventListener("click", () => {
                if (!mobileViewport.matches) {
                    return;
                }

                const nextState = !sidebar.classList.contains("is-mobile-open");
                closeAllSidebars();
                setSidebarState(sidebar, nextState);
            });

            sidebar.querySelectorAll("[data-sidebar-nav-link]").forEach((link) => {
                link.addEventListener("click", () => {
                    if (mobileViewport.matches) {
                        setSidebarState(sidebar, false);
                    }
                });
            });

            setSidebarState(sidebar, false);
        });

        const syncSidebarViewport = () => {
            if (!mobileViewport.matches) {
                closeAllSidebars();
            }
        };

        if (typeof mobileViewport.addEventListener === "function") {
            mobileViewport.addEventListener("change", syncSidebarViewport);
        } else if (typeof mobileViewport.addListener === "function") {
            mobileViewport.addListener(syncSidebarViewport);
        }

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && mobileViewport.matches) {
                closeAllSidebars();
            }
        });
    }

    function bindDeclarativeFormSpinners() {
        document.addEventListener("submit", (event) => {
            const form = event.target;
            if (!(form instanceof HTMLFormElement) || form.dataset.disableSubmitSpinner === "true") {
                return;
            }

            const submitter = event.submitter instanceof HTMLButtonElement
                ? event.submitter
                : form.querySelector('button[type="submit"]');

            if (!(submitter instanceof HTMLButtonElement) || submitter.dataset.loadingSpinner === "false") {
                return;
            }

            setButtonLoading(submitter, true, submitter.dataset.loadingText);
        });
    }

    function bindExportPeriodSelectors() {
        const forms = Array.from(document.querySelectorAll("[data-export-form]"));
        if (!forms.length) {
            return;
        }

        forms.forEach((form) => {
            const periodSelect = form.querySelector("[data-export-period-select]");
            const panels = Array.from(form.querySelectorAll("[data-export-period-panel]"));
            if (!(periodSelect instanceof HTMLSelectElement) || !panels.length) {
                return;
            }

            const syncPanels = () => {
                const selectedPeriod = periodSelect.value || "all_time";
                panels.forEach((panel) => {
                    const isActive = panel.dataset.exportPeriodPanel === selectedPeriod;
                    panel.hidden = !isActive;
                    panel.setAttribute("aria-hidden", String(!isActive));

                    panel.querySelectorAll("input, select, textarea").forEach((input) => {
                        if (input === periodSelect) {
                            return;
                        }
                        input.disabled = !isActive;
                    });
                });
            };

            periodSelect.addEventListener("change", syncPanels);
            syncPanels();
        });
    }

    window.AkiliUI = {
        setButtonLoading,
        togglePageLoader,
        openModalById,
        closeModal,
    };

    document.addEventListener("DOMContentLoaded", () => {
        bindDeclarativeFormSpinners();
        bindLanguageSwitcher();
        bindSidebarMenu();
        bindUiModals();
        bindConfirmButtons();
        bindAccountSwitcher();
        bindAccountEditButtons();
        bindExportPeriodSelectors();
    }, { once: true });
})();

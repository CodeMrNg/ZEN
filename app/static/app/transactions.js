const transactionsAppNode = document.getElementById("transactions-app");

if (transactionsAppNode) {
    const uiLocale = document.body?.dataset.uiLocale || "fr-FR";
    const langCode = (document.documentElement.lang || "fr").toLowerCase();
    const strings = langCode.startsWith("fr") ? {
        loading: "Chargement...",
        loadingTransactions: "Chargement des transactions...",
        loadingTransactionsDetails: "Chargement du capital, des flux et de l historique mensuel.",
        save: "Enregistrement...",
        savingMovement: "Enregistrement du mouvement en cours...",
        transactionsFailed: "Les transactions n ont pas pu etre chargees.",
        capitalVariation: "Capital initial {base} | Variation nette {net} sur {month}.",
        noMovements: "Aucun depot ni retrait enregistre pour le moment.",
        noOperations: "Aucune operation de capital disponible.",
        noMonthlyData: "Aucune donnee mensuelle disponible.",
        noNote: "Sans note",
        lastUpdatePrefix: "Derniere mise a jour a",
        recordWithdrawal: "Enregistrer un retrait",
        recordDeposit: "Enregistrer un depot",
        withdrawalCopy: "Enregistrez une sortie de capital. Le capital actuel et l historique mensuel sont recalcules automatiquement.",
        depositCopy: "Enregistrez un apport de capital. Le capital actuel et l historique mensuel sont recalcules automatiquement.",
        withdrawalAmount: "Montant du retrait",
        depositAmount: "Montant du depot",
        withdrawalPlaceholder: "Ex: retrait mensuel, securisation de performance",
        depositPlaceholder: "Ex: apport de capital, alimentation du compte",
        withdrawalCaption: "Le retrait diminue le capital actuel et s integre a l historique mensuel.",
        depositCaption: "Le depot augmente le capital actuel et s integre a l historique mensuel.",
        movementsPreviewLatest: "2 derniers / {count}",
        movementsPreviewCount: "{count} transaction(s)",
        bestMonth: "Meilleur mois",
        worstMonth: "Mauvais mois",
        chartMissing: "Chart.js n est pas charge. Verifiez le chargement des assets.",
        monthlyGp: "G/P mensuel",
    } : {
        loading: "Loading...",
        loadingTransactions: "Loading transactions...",
        loadingTransactionsDetails: "Loading capital, flows, and monthly history.",
        save: "Saving...",
        savingMovement: "Saving movement...",
        transactionsFailed: "Transactions could not be loaded.",
        capitalVariation: "Initial capital {base} | Net change {net} over {month}.",
        noMovements: "No deposit or withdrawal has been recorded yet.",
        noOperations: "No capital operation available.",
        noMonthlyData: "No monthly data available.",
        noNote: "No note",
        lastUpdatePrefix: "Last update at",
        recordWithdrawal: "Record a withdrawal",
        recordDeposit: "Record a deposit",
        withdrawalCopy: "Record a capital outflow. Current capital and monthly history are recalculated automatically.",
        depositCopy: "Record a capital deposit. Current capital and monthly history are recalculated automatically.",
        withdrawalAmount: "Withdrawal amount",
        depositAmount: "Deposit amount",
        withdrawalPlaceholder: "Example: monthly withdrawal, profit lock-in",
        depositPlaceholder: "Example: capital injection, account funding",
        withdrawalCaption: "The withdrawal reduces current capital and is added to monthly history.",
        depositCaption: "The deposit increases current capital and is added to monthly history.",
        movementsPreviewLatest: "Latest 2 / {count}",
        movementsPreviewCount: "{count} transaction(s)",
        bestMonth: "Best month",
        worstMonth: "Worst month",
        chartMissing: "Chart.js is not loaded. Check asset loading.",
        monthlyGp: "Monthly P/L",
    };
    const currencyUtils = window.AkiliCurrency || {};
    const setButtonLoading = window.AkiliUI?.setButtonLoading || ((button, isLoading, label) => {
        if (!button) {
            return;
        }

        if (isLoading) {
            if (!button.dataset.restoreLabel) {
                button.dataset.restoreLabel = button.textContent;
            }
            button.disabled = true;
            button.textContent = label || strings.loading;
            return;
        }

        button.disabled = false;
        if (button.dataset.restoreLabel) {
            button.textContent = button.dataset.restoreLabel;
            delete button.dataset.restoreLabel;
        }
    });
    const togglePageLoader = window.AkiliUI?.togglePageLoader || ((loader, isLoading) => {
        if (!loader) {
            return;
        }
        loader.hidden = !isLoading;
        loader.setAttribute("aria-hidden", String(!isLoading));
    });

    const state = {
        controller: null,
        flashTimeout: null,
        chart: null,
        allMovements: [],
    };

    const endpoints = {
        transactions: transactionsAppNode.dataset.transactionsUrl,
        movement: transactionsAppNode.dataset.movementUrl,
    };

    const metricsGrid = document.getElementById("transactions-metrics");
    const flashMessage = document.getElementById("transactions-flash");
    const pageLoader = document.getElementById("transactions-loader");
    const refreshButton = document.getElementById("transactions-refresh");
    const depositButton = document.getElementById("open-deposit-modal");
    const withdrawalButton = document.getElementById("open-withdrawal-modal");
    const lastUpdate = document.getElementById("transactions-last-update");
    const currentMonthLabel = document.getElementById("transactions-current-month");
    const currentCapital = document.getElementById("transactions-current-capital");
    const capitalCopy = document.getElementById("transactions-capital-copy");
    const monthTrades = document.getElementById("transactions-month-trades");
    const monthWinners = document.getElementById("transactions-month-winners");
    const monthLosers = document.getElementById("transactions-month-losers");
    const netHighlight = document.getElementById("transactions-highlight-net");
    const depositsHighlight = document.getElementById("transactions-highlight-deposits");
    const withdrawalsHighlight = document.getElementById("transactions-highlight-withdrawals");
    const bestMonthHighlight = document.getElementById("transactions-highlight-best-month");
    const worstMonthHighlight = document.getElementById("transactions-highlight-worst-month");
    const movementsList = document.getElementById("movements-list");
    const movementsPreviewBadge = document.getElementById("movements-preview-badge");
    const openMovementsModalButton = document.getElementById("open-movements-modal");
    const historyTableBody = document.getElementById("history-table-body");
    const movementModal = document.getElementById("movement-modal");
    const movementModalTitle = document.getElementById("movement-modal-title");
    const movementModalCopy = document.getElementById("movement-modal-copy");
    const closeMovementModalButton = document.getElementById("close-movement-modal");
    const movementForm = document.getElementById("movement-form");
    const movementKind = document.getElementById("movement-kind");
    const movementOccurredAt = document.getElementById("movement-occurred-at");
    const movementAmountLabel = document.getElementById("movement-amount-label");
    const movementNote = document.getElementById("movement-note");
    const movementFormCaption = document.getElementById("movement-form-caption");
    const movementSubmitButton = document.getElementById("movement-submit");
    const movementsModal = document.getElementById("movements-modal");
    const movementsModalList = document.getElementById("movements-modal-list");
    const closeMovementsModalButton = document.getElementById("close-movements-modal");

    document.addEventListener("DOMContentLoaded", () => {
        renderMetricSkeletons();
        bindEvents();
        loadTransactions();
    });

    function bindEvents() {
        refreshButton.addEventListener("click", () => {
            loadTransactions();
        });

        depositButton.addEventListener("click", () => {
            openMovementModal("DEPOSIT");
        });

        withdrawalButton.addEventListener("click", () => {
            openMovementModal("WITHDRAWAL");
        });

        openMovementsModalButton.addEventListener("click", openMovementsModal);
        closeMovementModalButton.addEventListener("click", closeMovementModal);
        closeMovementsModalButton.addEventListener("click", closeMovementsModal);
        movementForm.addEventListener("submit", handleMovementSubmit);

        movementModal.addEventListener("click", (event) => {
            if (event.target.matches("[data-close-movement-modal]")) {
                closeMovementModal();
            }
        });

        movementsModal.addEventListener("click", (event) => {
            if (event.target.matches("[data-close-movements-modal]")) {
                closeMovementsModal();
            }
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape" && !movementModal.hidden) {
                closeMovementModal();
            }
            if (event.key === "Escape" && !movementsModal.hidden) {
                closeMovementsModal();
            }
        });
    }

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

    function formatCurrency(value) {
        if (typeof currencyUtils.formatCurrency === "function") {
            return currencyUtils.formatCurrency(value, {
                currency: transactionsAppNode.dataset.currencyCode || "USD",
                locale: uiLocale,
            });
        }
        const amount = Number.parseFloat(value || 0);
        if (Number.isNaN(amount)) {
            return "--";
        }
        return new Intl.NumberFormat(uiLocale, {
            style: "currency",
            currency: transactionsAppNode.dataset.currencyCode || "USD",
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }).format(amount).replace(/([.,])00(?=(?:\s*[^\d\s]+)?\s*$)/, "");
    }

    function updateModalOpenState() {
        document.body.classList.toggle("modal-open", !movementModal.hidden || !movementsModal.hidden);
    }

    function openModal(modal) {
        modal.hidden = false;
        modal.setAttribute("aria-hidden", "false");
        updateModalOpenState();
    }

    function closeModal(modal) {
        modal.hidden = true;
        modal.setAttribute("aria-hidden", "true");
        updateModalOpenState();
    }

    function showFlash(message, tone = "success") {
        flashMessage.hidden = false;
        flashMessage.textContent = message;
        flashMessage.className = `flash-message is-${tone}`;
        window.clearTimeout(state.flashTimeout);
        state.flashTimeout = window.setTimeout(() => {
            flashMessage.hidden = true;
        }, 5000);
    }

    function renderMetricSkeletons() {
        metricsGrid.innerHTML = Array.from({ length: 5 }, () => {
            return '<article class="metric-card is-skeleton"></article>';
        }).join("");
    }

    function setBusy(isBusy, loaderMessage = strings.loadingTransactions) {
        setButtonLoading(refreshButton, isBusy, strings.loading);
        depositButton.disabled = isBusy;
        withdrawalButton.disabled = isBusy;
        togglePageLoader(pageLoader, isBusy, loaderMessage);
    }

    async function loadTransactions() {
        if (state.controller) {
            state.controller.abort();
        }

        const controller = new AbortController();
        state.controller = controller;
        setBusy(true, strings.loadingTransactionsDetails);

        try {
            const response = await fetch(endpoints.transactions, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
                signal: controller.signal,
            });

            if (!response.ok) {
                throw new Error(strings.transactionsFailed);
            }

            const payload = await response.json();
            renderPayload(payload);
            lastUpdate.textContent = `${strings.lastUpdatePrefix} ${new Date().toLocaleTimeString(uiLocale, { hour: "2-digit", minute: "2-digit" })}`;
        } catch (error) {
            if (error.name !== "AbortError") {
                showFlash(error.message || strings.transactionsFailed, "error");
            }
        } finally {
            if (state.controller === controller) {
                state.controller = null;
                setBusy(false);
            }
        }
    }

    function renderPayload(payload) {
        state.allMovements = payload.all_movements || payload.recent_movements || [];
        renderSummary(payload.summary, payload.highlights);
        renderMetrics(payload.metrics || []);
        renderMovements(state.allMovements);
        renderHistory(payload.monthly_history || []);
        renderChart(payload.chart || { labels: [], values: [] });
    }

    function renderSummary(summary, highlights) {
        currentMonthLabel.textContent = summary.current_month_label;
        currentCapital.textContent = summary.current_capital_label;
        capitalCopy.textContent = strings.capitalVariation
            .replace("{base}", summary.base_capital_label)
            .replace("{net}", highlights.net_month_label)
            .replace("{month}", summary.current_month_label);
        monthTrades.textContent = summary.trade_count_month;
        monthWinners.textContent = summary.winners_month;
        monthLosers.textContent = summary.losers_month;
        netHighlight.textContent = highlights.net_month_label;
        depositsHighlight.textContent = highlights.deposits_label;
        withdrawalsHighlight.textContent = highlights.withdrawals_label;
        bestMonthHighlight.textContent = highlights.best_month_label;
        worstMonthHighlight.textContent = highlights.worst_month_label;
    }

    function renderMetrics(metrics) {
        metricsGrid.innerHTML = metrics.map((metric) => {
            return `
                <article class="metric-card ${escapeHtml(metric.tone)}">
                    <div class="metric-card-header">
                        <div>
                            <span class="metric-card-title">${escapeHtml(metric.label)}</span>
                            <strong class="metric-card-value">${escapeHtml(metric.value)}</strong>
                            <p class="metric-card-detail">${escapeHtml(metric.detail)}</p>
                        </div>
                        <div class="metric-ring" style="--progress:${Number(metric.progress) || 0};"></div>
                    </div>
                    <div class="metric-progress" style="--progress:${Number(metric.progress) || 0}%;"><span></span></div>
                </article>
            `;
        }).join("");
    }

    function buildMovementsMarkup(movements, emptyMessage) {
        if (!movements.length) {
            return `<div class="empty-state">${emptyMessage}</div>`;
        }

        return movements.map((movement) => {
            const note = movement.note ? escapeHtml(movement.note) : strings.noNote;
            return `
                <article class="movement-item ${escapeHtml(movement.tone)}">
                    <div class="movement-copy">
                        <div class="movement-top">
                            <span class="movement-kind ${escapeHtml(movement.tone)}">${escapeHtml(movement.kind_label)}</span>
                            <strong>${escapeHtml(movement.amount_label)}</strong>
                        </div>
                        <p>${note}</p>
                    </div>
                    <span class="movement-date">${escapeHtml(movement.occurred_at_label)}</span>
                </article>
            `;
        }).join("");
    }

    function renderMovements(movements) {
        const previewMovements = movements.slice(0, 2);
        const totalCount = movements.length;
        movementsPreviewBadge.textContent = totalCount > 2
            ? strings.movementsPreviewLatest.replace("{count}", totalCount)
            : strings.movementsPreviewCount.replace("{count}", totalCount);
        movementsList.innerHTML = buildMovementsMarkup(
            previewMovements,
            strings.noMovements,
        );
        movementsModalList.innerHTML = buildMovementsMarkup(
            movements,
            strings.noOperations,
        );
    }

    function renderHistory(rows) {
        if (!rows.length) {
            historyTableBody.innerHTML = `
                <tr>
                    <td colspan="9">
                        <div class="empty-state">${strings.noMonthlyData}</div>
                    </td>
                </tr>
            `;
            return;
        }

        historyTableBody.innerHTML = rows.map((row) => {
            const badges = [
                row.is_best_month ? `<span class="history-badge best">${strings.bestMonth}</span>` : "",
                row.is_worst_month ? `<span class="history-badge worst">${strings.worstMonth}</span>` : "",
            ].filter(Boolean).join("");
            return `
                <tr>
                    <td>
                        <strong>${escapeHtml(row.month_label)}</strong>
                        ${badges}
                    </td>
                    <td>${escapeHtml(row.capital_start_label)}</td>
                    <td>${escapeHtml(row.gp_total_label)}</td>
                    <td>${escapeHtml(row.deposits_label)}</td>
                    <td>${escapeHtml(row.withdrawals_label)}</td>
                    <td>
                        <span class="history-tone ${escapeHtml(row.tone)}">${escapeHtml(row.net_label)}</span>
                    </td>
                    <td>${escapeHtml(row.trade_count)}</td>
                    <td>${escapeHtml(row.winners)}</td>
                    <td>${escapeHtml(row.losers)}</td>
                </tr>
            `;
        }).join("");
    }

    function renderChart(chart) {
        if (!window.Chart) {
            showFlash(strings.chartMissing, "error");
            return;
        }

        const canvas = document.getElementById("transactions-chart");
        if (!canvas) {
            return;
        }

        if (state.chart) {
            state.chart.destroy();
        }

        const values = Array.isArray(chart.values) ? chart.values : [];
        state.chart = new window.Chart(canvas, {
            type: "bar",
            data: {
                labels: Array.isArray(chart.labels) ? chart.labels : [],
                datasets: [{
                    label: strings.monthlyGp,
                    data: values,
                    borderRadius: 14,
                    borderSkipped: false,
                    backgroundColor: values.map((value) => {
                        return Number(value) >= 0 ? "rgba(53, 212, 154, 0.8)" : "rgba(239, 100, 100, 0.8)";
                    }),
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label(context) {
                                const label = context.dataset?.label ? `${context.dataset.label}: ` : "";
                                const numericValue = context.parsed?.y ?? context.parsed ?? 0;
                                return `${label}${formatCurrency(numericValue)}`;
                            },
                        },
                    },
                },
                scales: {
                    x: {
                        ticks: {
                            color: "#c6cee1",
                            font: { family: "Manrope", size: 11 },
                        },
                        grid: {
                            display: false,
                        },
                    },
                    y: {
                        ticks: {
                            color: "#c6cee1",
                            font: { family: "Manrope", size: 11 },
                            callback: (value) => formatCurrency(value),
                        },
                        grid: {
                            color: "rgba(255,255,255,0.06)",
                        },
                    },
                },
            },
        });
    }

    function seedOccurredAt() {
        const now = new Date();
        const local = new Date(now.getTime() - (now.getTimezoneOffset() * 60000));
        movementOccurredAt.value = local.toISOString().slice(0, 16);
    }

    function openMovementModal(kind = "WITHDRAWAL") {
        const isDeposit = kind === "DEPOSIT";
        movementForm.reset();
        movementKind.value = kind;
        seedOccurredAt();
        movementModalTitle.textContent = isDeposit ? strings.recordDeposit : strings.recordWithdrawal;
        movementModalCopy.textContent = isDeposit
            ? strings.depositCopy
            : strings.withdrawalCopy;
        movementAmountLabel.textContent = isDeposit ? strings.depositAmount : strings.withdrawalAmount;
        movementNote.placeholder = isDeposit
            ? strings.depositPlaceholder
            : strings.withdrawalPlaceholder;
        movementFormCaption.textContent = isDeposit
            ? strings.depositCaption
            : strings.withdrawalCaption;
        movementSubmitButton.textContent = isDeposit ? strings.recordDeposit : strings.recordWithdrawal;
        movementSubmitButton.className = isDeposit ? "warning-button" : "success-button";
        openModal(movementModal);
        window.setTimeout(() => {
            movementOccurredAt.focus();
        }, 40);
    }

    function closeMovementModal() {
        closeModal(movementModal);
    }

    function openMovementsModal() {
        openModal(movementsModal);
    }

    function closeMovementsModal() {
        closeModal(movementsModal);
    }

    function formatErrorMessages(errors) {
        const messages = [];
        Object.values(errors || {}).forEach((fieldErrors) => {
            fieldErrors.forEach((fieldError) => {
                if (fieldError.message) {
                    messages.push(fieldError.message);
                }
            });
        });
        return messages.join(" ");
    }

    async function handleMovementSubmit(event) {
        event.preventDefault();

        setButtonLoading(movementSubmitButton, true, strings.save);
        togglePageLoader(pageLoader, true, strings.savingMovement);

        try {
            const response = await fetch(endpoints.movement, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCsrfToken(),
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: new FormData(movementForm),
            });

            const payload = await response.json();

            if (!response.ok || !payload.ok) {
                throw new Error(formatErrorMessages(payload.errors) || payload.message || "Le mouvement n a pas pu etre enregistre.");
            }

            closeMovementModal();
            showFlash(payload.message || "Mouvement enregistre.");
            await loadTransactions();
        } catch (error) {
            showFlash(error.message || "Le mouvement n a pas pu etre enregistre.", "error");
        } finally {
            setButtonLoading(movementSubmitButton, false);
            if (!state.controller) {
                togglePageLoader(pageLoader, false);
            }
        }
    }
}

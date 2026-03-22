const appNode = document.getElementById("dashboard-app");

if (appNode) {
    const uiLocale = document.body?.dataset.uiLocale || "fr-FR";
    const langCode = (document.documentElement.lang || "fr").toLowerCase();
    const strings = langCode.startsWith("fr") ? {
        loading: "Chargement...",
        gainCapital: "Gain sur capital (%)",
        lossCapital: "Perte sur capital (%)",
        impactCapital: "Impact sur capital (%)",
        currentCapitalPrefix: "Calcul base sur le capital actuel de",
        referenceCapitalPrefix: "Calcul base sur un capital de",
        newTrade: "Nouveau trade",
        editTrade: "Modifier le trade",
        saveTrade: "Enregistrer le trade",
        saveChanges: "Enregistrer les modifications",
        loadingDashboard: "Chargement du tableau de bord...",
        loadingDashboardDetails: "Chargement des indicateurs, graphiques, calendrier et executions recentes.",
        loadingDemo: "Chargement du jeu de donnees de demonstration...",
        loadingTradeSave: "Enregistrement du trade en cours...",
        loadingTradeUpdate: "Mise a jour du trade en cours...",
        dashboardFailed: "Le tableau de bord n a pas pu etre charge.",
        lastUpdatePrefix: "Derniere mise a jour a",
        tradeUpdated: "Trade mis a jour. Le tableau de bord est en cours de synchronisation.",
        tradeSaved: "Trade enregistre. Le tableau de bord est en cours de synchronisation.",
        noData: "Aucune donnee disponible",
        noExecution: "Aucune execution",
        noExecutionYet: "Aucune execution enregistree pour le moment. Utilisez le formulaire de saisie ou chargez un jeu de donnees de demonstration.",
        monthTradesTitle: "Trades du mois",
        monthTradesSubtitle: "trade(s) pour",
        monthTradesEmpty: "Aucun trade enregistre pour le mois selectionne.",
        monthTradesCountSuffix: "trade(s) ce mois",
        radarTitle: "Radar de performance",
        cumulativeTitle: "Courbe de P&L cumulatif",
        dailyTitle: "P&L net quotidien",
        comboTitle: "Vue combinee",
        calendarTitle: "Calendrier de performance",
        panelDetailTitle: "Vue detaillee",
        positiveDay: "Jour positif",
        negativeDay: "Jour negatif",
        neutralDay: "Neutre",
        dayTradeCountSuffix: "trade(s)",
        dayPerformance: "Performance du jour",
        executions: "Executions",
        dayExecutionsTitle: "Executions de la journee",
        tradeImages: "Images du trade",
        screenshotAltPrefix: "Capture",
        noImageSelected: "Aucune image selectionnee",
        imageCurrentBadge: "Actuelle",
        imageNewBadge: "Nouvelle",
        imageKeepHint: "Conservees si aucune nouvelle image n est ajoutee",
        viewImage: "Agrandir l image",
        imagePreviewTitle: "Apercu de l image",
        downloadImage: "Telecharger l image",
        removeImage: "Supprimer l image",
        closeImageViewer: "Fermer l apercu image",
        imageTypeError: "Chaque fichier doit etre une image.",
        imageCompressionFailed: "La compression des images a echoue.",
        dateTime: "Date et heure",
        setup: "Setup",
        result: "Resultat",
        netPnl: "P&L net",
        gpValue: "G/P",
        ratio: "Ratio",
        lots: "Lots",
        capitalPercent: "% capital",
        confidence: "Confiance",
        capitalReference: "Capital de reference",
        riskAmount: "Montant de risque",
        notes: "Notes",
        noNotes: "Aucune note n a ete renseignee pour ce trade.",
        editTradeButton: "Modifier le trade",
        chartMissing: "Chart.js n est pas charge. Verifiez le chargement des assets.",
        tradeSaveFailed: "Le trade n a pas pu etre enregistre.",
        demoLoadFailed: "Le jeu de donnees de demonstration n a pas pu etre charge.",
        countdownOverdue: "Depasse de",
        countdownDisabled: "Desactive",
        countdownDay: "j",
        countdownHour: "h",
        countdownMinute: "min",
        countdownSecond: "s",
    } : {
        loading: "Loading...",
        gainCapital: "Capital gain (%)",
        lossCapital: "Capital loss (%)",
        impactCapital: "Capital impact (%)",
        currentCapitalPrefix: "Calculated from the current capital of",
        referenceCapitalPrefix: "Calculated from a capital of",
        newTrade: "New trade",
        editTrade: "Edit trade",
        saveTrade: "Save trade",
        saveChanges: "Save changes",
        loadingDashboard: "Loading dashboard...",
        loadingDashboardDetails: "Loading metrics, charts, calendar, and recent executions.",
        loadingDemo: "Loading demo dataset...",
        loadingTradeSave: "Saving trade...",
        loadingTradeUpdate: "Updating trade...",
        dashboardFailed: "The dashboard could not be loaded.",
        lastUpdatePrefix: "Last update at",
        tradeUpdated: "Trade updated. The dashboard is synchronizing.",
        tradeSaved: "Trade saved. The dashboard is synchronizing.",
        noData: "No data available",
        noExecution: "No execution",
        noExecutionYet: "No execution has been recorded yet. Use the entry form or load a demo dataset.",
        monthTradesTitle: "Monthly trades",
        monthTradesSubtitle: "trade(s) for",
        monthTradesEmpty: "No trade has been recorded for the selected month.",
        monthTradesCountSuffix: "trade(s) this month",
        radarTitle: "Performance radar",
        cumulativeTitle: "Cumulative P&L curve",
        dailyTitle: "Daily net P&L",
        comboTitle: "Combined view",
        calendarTitle: "Performance calendar",
        panelDetailTitle: "Detailed view",
        positiveDay: "Positive day",
        negativeDay: "Negative day",
        neutralDay: "Neutral",
        dayTradeCountSuffix: "trade(s)",
        dayPerformance: "Day performance",
        executions: "Executions",
        dayExecutionsTitle: "Day executions",
        tradeImages: "Trade images",
        screenshotAltPrefix: "Screenshot",
        noImageSelected: "No image selected",
        imageCurrentBadge: "Current",
        imageNewBadge: "New",
        imageKeepHint: "Kept if no new image is added",
        viewImage: "View image",
        imagePreviewTitle: "Image preview",
        downloadImage: "Download image",
        removeImage: "Remove image",
        closeImageViewer: "Close image preview",
        imageTypeError: "Each file must be an image.",
        imageCompressionFailed: "Image compression failed.",
        dateTime: "Date and time",
        setup: "Setup",
        result: "Result",
        netPnl: "Net P&L",
        gpValue: "P/L",
        ratio: "Ratio",
        lots: "Lots",
        capitalPercent: "% capital",
        confidence: "Confidence",
        capitalReference: "Reference capital",
        riskAmount: "Risk amount",
        notes: "Notes",
        noNotes: "No note was provided for this trade.",
        editTradeButton: "Edit trade",
        chartMissing: "Chart.js is not loaded. Check asset loading.",
        tradeSaveFailed: "The trade could not be saved.",
        demoLoadFailed: "The demo dataset could not be loaded.",
        countdownOverdue: "Overdue by",
        countdownDisabled: "Disabled",
        countdownDay: "d",
        countdownHour: "h",
        countdownMinute: "m",
        countdownSecond: "s",
    };
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
        charts: {},
        controller: null,
        flashTimeout: null,
        compressedScreenshotFiles: [],
        previewObjectUrls: [],
        expandedPanelChart: null,
        lastPayload: null,
        tradeLookup: new Map(),
        dayTradeMap: {},
        calendarDayMap: {},
        preferences: buildInitialPreferences(),
        editingTradeId: null,
        editingCapitalBase: null,
        editingCapitalBaseFormatted: null,
        existingScreenshots: [],
        removedScreenshotIds: new Set(),
        imageViewerContext: null,
    };

    const endpoints = {
        dashboard: appNode.dataset.dashboardUrl,
        trade: appNode.dataset.tradeUrl,
        tradeUpdateBase: appNode.dataset.tradeUpdateBaseUrl,
        demo: appNode.dataset.demoUrl,
    };

    const metricsGrid = document.getElementById("metrics-grid");
    const monthSelector = document.getElementById("month-selector");
    const flashMessage = document.getElementById("flash-message");
    const pageLoader = document.getElementById("dashboard-loader");
    const demoButton = document.getElementById("demo-button");
    const refreshButton = document.getElementById("refresh-button");
    const openTradeModalButton = document.getElementById("open-trade-modal");
    const openTradeModalSecondaryButton = document.getElementById("open-trade-modal-secondary");
    const tradeModal = document.getElementById("trade-modal");
    const tradeModalTitle = document.getElementById("trade-modal-title");
    const closeTradeModalButton = document.getElementById("close-trade-modal");
    const panelModal = document.getElementById("panel-modal");
    const panelModalTitle = document.getElementById("panel-modal-title");
    const closePanelModalButton = document.getElementById("close-panel-modal");
    const expandedChartWrap = document.getElementById("expanded-chart-wrap");
    const expandedPanelCanvas = document.getElementById("expanded-panel-canvas");
    const expandedCalendarWrap = document.getElementById("expanded-calendar-wrap");
    const expandedCalendarGrid = document.getElementById("expanded-calendar-grid");
    const expandedCalendarWeeks = document.getElementById("expanded-calendar-weeks");
    const detailModal = document.getElementById("detail-modal");
    const detailModalTitle = document.getElementById("detail-modal-title");
    const detailModalSubtitle = document.getElementById("detail-modal-subtitle");
    const detailModalBody = document.getElementById("detail-modal-body");
    const closeDetailModalButton = document.getElementById("close-detail-modal");
    const monthTradesButton = document.getElementById("month-trades-button");
    const monthTradesCount = document.getElementById("month-trades-count");
    const monthTradesModal = document.getElementById("month-trades-modal");
    const monthTradesModalTitle = document.getElementById("month-trades-modal-title");
    const monthTradesModalSubtitle = document.getElementById("month-trades-modal-subtitle");
    const monthTradesList = document.getElementById("month-trades-list");
    const closeMonthTradesModalButton = document.getElementById("close-month-trades-modal");
    const imageViewerModal = document.getElementById("image-viewer-modal");
    const closeImageViewerButton = document.getElementById("close-image-viewer");
    const imageViewerTitle = document.getElementById("image-viewer-title");
    const imageViewerImage = document.getElementById("image-viewer-image");
    const imageViewerDownload = document.getElementById("image-viewer-download");
    const imageViewerRemoveButton = document.getElementById("image-viewer-remove");
    const tradeForm = document.getElementById("trade-form");
    const lastUpdate = document.getElementById("last-update");
    const symbolInput = document.getElementById("symbol");
    const directionInput = document.getElementById("direction");
    const resultInput = document.getElementById("result");
    const setupInput = document.getElementById("setup");
    const confidenceInput = document.getElementById("confidence");
    const ratioInput = document.getElementById("rr_ratio");
    const lotSizeInput = document.getElementById("lot_size");
    const gpValueInput = document.getElementById("gp_value");
    const capitalImpactLabel = document.getElementById("capital-impact-label");
    const capitalImpactPercent = document.getElementById("capital-impact-percent");
    const capitalHint = document.getElementById("trade-capital-hint");
    const screenshotInput = document.getElementById("screenshots");
    const imagePreview = document.getElementById("image-preview");
    const imagePreviewName = document.getElementById("image-preview-name");
    const imagePreviewSize = document.getElementById("image-preview-size");
    const imagePreviewGrid = document.getElementById("image-preview-grid");
    const recentTradesContainer = document.getElementById("recent-trades");
    const calendarGrid = document.getElementById("calendar-grid");
    const expandButtons = document.querySelectorAll("[data-expand-panel]");
    const tradeFormSubmitButton = tradeForm.querySelector('button[type="submit"]');
    const serverRefreshBanner = document.querySelector("[data-server-refresh-due-at]");
    const serverRefreshCountdown = document.getElementById("server-refresh-countdown");

    document.addEventListener("DOMContentLoaded", () => {
        renderMetricSkeletons();
        seedExecutedAt();
        initializeServerRefreshCountdown();
        bindEvents();
        loadDashboard();
    });

    function bindEvents() {
        monthSelector.addEventListener("change", () => {
            loadDashboard(monthSelector.value);
        });

        refreshButton.addEventListener("click", () => {
            loadDashboard(monthSelector.value);
        });

        if (demoButton) {
            demoButton.addEventListener("click", handleDemoSeed);
        }
        if (monthTradesButton) {
            monthTradesButton.addEventListener("click", openMonthTradesModal);
        }
        openTradeModalButton.addEventListener("click", openTradeModal);
        openTradeModalSecondaryButton.addEventListener("click", openTradeModal);
        closeTradeModalButton.addEventListener("click", closeTradeModal);
        closePanelModalButton.addEventListener("click", closePanelModal);
        closeDetailModalButton.addEventListener("click", closeDetailModal);
        closeMonthTradesModalButton.addEventListener("click", closeMonthTradesModal);
        closeImageViewerButton.addEventListener("click", closeImageViewer);
        expandButtons.forEach((button) => {
            button.addEventListener("click", () => openPanelModal(button.dataset.expandPanel));
        });
        tradeForm.addEventListener("submit", handleTradeSubmit);
        resultInput.addEventListener("change", updateCapitalImpactPreview);
        ratioInput.addEventListener("input", updateCapitalImpactPreview);
        gpValueInput.addEventListener("input", updateCapitalImpactPreview);
        screenshotInput.addEventListener("change", handleScreenshotChange);
        imagePreviewGrid.addEventListener("click", handleImagePreviewGridClick);
        recentTradesContainer.addEventListener("click", handleTradeCardClick);
        monthTradesList.addEventListener("click", handleTradeCardClick);
        monthTradesList.addEventListener("click", handleTradeEditClick);
        calendarGrid.addEventListener("click", handleCalendarCellClick);
        expandedCalendarGrid.addEventListener("click", handleCalendarCellClick);
        detailModalBody.addEventListener("click", handleImageViewerTriggerClick);
        detailModalBody.addEventListener("click", handleTradeCardClick);
        detailModalBody.addEventListener("click", handleTradeEditClick);
        tradeModal.addEventListener("click", (event) => {
            if (event.target.matches("[data-close-modal]")) {
                closeTradeModal();
            }
        });
        panelModal.addEventListener("click", (event) => {
            if (event.target.matches("[data-close-panel-modal]")) {
                closePanelModal();
            }
        });
        detailModal.addEventListener("click", (event) => {
            if (event.target.matches("[data-close-detail-modal]")) {
                closeDetailModal();
            }
        });
        monthTradesModal.addEventListener("click", (event) => {
            if (event.target.matches("[data-close-month-trades-modal]")) {
                closeMonthTradesModal();
            }
        });
        imageViewerModal.addEventListener("click", (event) => {
            if (event.target.matches("[data-close-image-viewer]")) {
                closeImageViewer();
            }
        });
        imageViewerRemoveButton.addEventListener("click", handleImageViewerRemove);
        document.addEventListener("keydown", (event) => {
            if (event.key !== "Escape") {
                return;
            }
            if (!imageViewerModal.hidden) {
                closeImageViewer();
                return;
            }
            if (!tradeModal.hidden) {
                closeTradeModal();
                return;
            }
            if (!panelModal.hidden) {
                closePanelModal();
                return;
            }
            if (!detailModal.hidden) {
                closeDetailModal();
                return;
            }
            if (!monthTradesModal.hidden) {
                closeMonthTradesModal();
            }
        });
    }

    function formatServerRefreshCountdown(totalSeconds) {
        const isOverdue = totalSeconds < 0;
        let remaining = Math.abs(Math.floor(totalSeconds));
        const days = Math.floor(remaining / 86400);
        remaining -= days * 86400;
        const hours = Math.floor(remaining / 3600);
        remaining -= hours * 3600;
        const minutes = Math.floor(remaining / 60);
        const seconds = remaining - (minutes * 60);

        let value = "";
        if (days > 0) {
            value = `${days} ${strings.countdownDay} ${hours} ${strings.countdownHour} ${minutes} ${strings.countdownMinute} ${seconds} ${strings.countdownSecond}`;
        } else if (hours > 0) {
            value = `${hours} ${strings.countdownHour} ${minutes} ${strings.countdownMinute} ${seconds} ${strings.countdownSecond}`;
        } else if (minutes > 0) {
            value = `${minutes} ${strings.countdownMinute} ${seconds} ${strings.countdownSecond}`;
        } else {
            value = `${seconds} ${strings.countdownSecond}`;
        }

        return isOverdue ? `${strings.countdownOverdue} ${value}` : value;
    }

    function initializeServerRefreshCountdown() {
        if (!serverRefreshBanner || !serverRefreshCountdown) {
            return;
        }

        const dueAt = serverRefreshBanner.dataset.serverRefreshDueAt;
        if (!dueAt) {
            serverRefreshCountdown.textContent = strings.countdownDisabled;
            return;
        }

        const dueDate = new Date(dueAt);
        if (Number.isNaN(dueDate.getTime())) {
            return;
        }

        const tick = () => {
            const totalSeconds = Math.floor((dueDate.getTime() - Date.now()) / 1000);
            serverRefreshCountdown.textContent = formatServerRefreshCountdown(totalSeconds);
        };

        tick();
        window.setInterval(tick, 1000);
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

    function formatCurrency(value, currency = "USD") {
        const amount = Number.parseFloat(value || 0);
        if (Number.isNaN(amount)) {
            return new Intl.NumberFormat(uiLocale, {
                style: "currency",
                currency,
            }).format(0);
        }
        return new Intl.NumberFormat(uiLocale, {
            style: "currency",
            currency,
        }).format(amount);
    }

    function buildInitialPreferences() {
        const capitalBase = appNode.dataset.capitalBase || "10000.00";
        const currentCapital = appNode.dataset.currentCapital || capitalBase;
        const currency = appNode.dataset.currencyCode || "USD";
        return {
            default_symbol: appNode.dataset.defaultSymbol || "XAUUSD",
            default_direction: appNode.dataset.defaultDirection || "LONG",
            default_result: "TAKE_PROFIT",
            default_setup: appNode.dataset.defaultSetup || "",
            default_lot_size: appNode.dataset.defaultLotSize || "1.00",
            default_gp_value: appNode.dataset.defaultGpValue || "0.00",
            default_confidence: appNode.dataset.defaultConfidence || "3",
            currency,
            capital_base: capitalBase,
            capital_base_formatted: formatCurrency(capitalBase, currency),
            current_capital: currentCapital,
            current_capital_formatted: formatCurrency(currentCapital, currency),
        };
    }

    function getPreviewCapitalContext() {
        if (state.editingTradeId && state.editingCapitalBase) {
            return {
                value: Number.parseFloat(state.editingCapitalBase),
                formatted: state.editingCapitalBaseFormatted
                    || formatCurrency(state.editingCapitalBase, state.preferences?.currency || "USD"),
                label: strings.referenceCapitalPrefix,
            };
        }

        const currentCapital = state.preferences?.current_capital
            || appNode.dataset.currentCapital
            || state.preferences?.capital_base
            || appNode.dataset.capitalBase
            || "0";
        return {
            value: Number.parseFloat(currentCapital),
            formatted: state.preferences?.current_capital_formatted
                || formatCurrency(currentCapital, state.preferences?.currency || "USD"),
            label: strings.currentCapitalPrefix,
        };
    }

    function updateTradeCapitalHint() {
        if (!capitalHint) {
            return;
        }

        const capitalContext = getPreviewCapitalContext();
        capitalHint.textContent = `${capitalContext.label} ${capitalContext.formatted}.`;
    }

    function updateCapitalImpactPreview() {
        if (!capitalImpactPercent || !capitalImpactLabel) {
            return;
        }

        const capitalBase = getPreviewCapitalContext().value;
        const gpValue = Number.parseFloat(gpValueInput?.value || "");
        const result = resultInput?.value || "TAKE_PROFIT";

        if (result === "BREAK_EVEN") {
            capitalImpactLabel.textContent = strings.impactCapital;
            capitalImpactPercent.textContent = "0.00%";
            capitalImpactPercent.className = "field-static-value is-flat";
            return;
        }

        if (!Number.isFinite(capitalBase) || capitalBase <= 0 || !Number.isFinite(gpValue)) {
            capitalImpactLabel.textContent = result === "STOP_LOSS" ? strings.lossCapital : strings.gainCapital;
            capitalImpactPercent.textContent = "--";
            capitalImpactPercent.className = `field-static-value ${result === "STOP_LOSS" ? "is-loss" : "is-profit"}`;
            return;
        }

        const capitalPercent = (Math.abs(gpValue) / capitalBase) * 100;

        if (result === "STOP_LOSS") {
            capitalImpactLabel.textContent = strings.lossCapital;
            capitalImpactPercent.textContent = `-${capitalPercent.toFixed(2)}%`;
            capitalImpactPercent.className = "field-static-value is-loss";
            return;
        }

        capitalImpactLabel.textContent = strings.gainCapital;
        capitalImpactPercent.textContent = `+${capitalPercent.toFixed(2)}%`;
        capitalImpactPercent.className = "field-static-value is-profit";
    }

    function applyTradeDefaults(overwrite = true) {
        const preferences = state.preferences || buildInitialPreferences();

        if (symbolInput && (overwrite || !symbolInput.value)) {
            symbolInput.value = preferences.default_symbol || "XAUUSD";
        }
        if (directionInput && (overwrite || !directionInput.value)) {
            directionInput.value = preferences.default_direction || "LONG";
        }
        if (resultInput && (overwrite || !resultInput.value)) {
            resultInput.value = preferences.default_result || "TAKE_PROFIT";
        }
        if (setupInput && (overwrite || !setupInput.value)) {
            setupInput.value = preferences.default_setup || "";
        }
        if (confidenceInput && (overwrite || !confidenceInput.value)) {
            confidenceInput.value = String(preferences.default_confidence || "3");
        }
        if (lotSizeInput && (overwrite || !lotSizeInput.value)) {
            lotSizeInput.value = preferences.default_lot_size || "1.00";
        }
        if (gpValueInput && (overwrite || !gpValueInput.value)) {
            gpValueInput.value = preferences.default_gp_value || "0.00";
        }

        updateTradeCapitalHint();
        updateCapitalImpactPreview();
    }

    function seedExecutedAt() {
        const input = document.getElementById("executed_at");
        if (!input) {
            return;
        }

        if (!input.value) {
            const now = new Date();
            const local = new Date(now.getTime() - (now.getTimezoneOffset() * 60000));
            input.value = local.toISOString().slice(0, 16);
        }

        applyTradeDefaults(true);
    }

    function formatFileSize(size) {
        if (size < 1024) {
            return `${size} o`;
        }
        if (size < 1024 * 1024) {
            return `${(size / 1024).toFixed(1)} Ko`;
        }
        return `${(size / (1024 * 1024)).toFixed(2)} Mo`;
    }

    function formatImageCountLabel(count, context = "selected") {
        if (langCode.startsWith("fr")) {
            if (context === "existing") {
                return count > 1 ? `${count} images actuellement associees` : "1 image actuellement associee";
            }
            if (context === "gallery") {
                return count > 1 ? `${count} images dans la galerie` : "1 image dans la galerie";
            }
            if (context === "new") {
                return count > 1 ? `${count} nouvelles images seront ajoutees` : "1 nouvelle image sera ajoutee";
            }
            return count > 1 ? `${count} images selectionnees` : "1 image selectionnee";
        }

        if (context === "existing") {
            return count > 1 ? `${count} images currently attached` : "1 image currently attached";
        }
        if (context === "gallery") {
            return count > 1 ? `${count} images in the gallery` : "1 image in the gallery";
        }
        if (context === "new") {
            return count > 1 ? `${count} new images will be added` : "1 new image will be added";
        }
        return count > 1 ? `${count} images selected` : "1 image selected";
    }

    function formatTradeImageCount(count) {
        if (langCode.startsWith("fr")) {
            return `${count} image${count === 1 ? "" : "s"}`;
        }
        return `${count} image${count === 1 ? "" : "s"}`;
    }

    function revokePreviewUrls() {
        state.previewObjectUrls.forEach((url) => {
            URL.revokeObjectURL(url);
        });
        state.previewObjectUrls = [];
    }

    function removePreviewUrlAt(index) {
        const [previewUrl] = state.previewObjectUrls.splice(index, 1);
        if (previewUrl) {
            URL.revokeObjectURL(previewUrl);
        }
    }

    function renderActionIcon(kind) {
        if (kind === "download") {
            return `
                <svg viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M12 4v10"></path>
                    <path d="M8 11l4 4 4-4"></path>
                    <path d="M5 19h14"></path>
                </svg>
            `;
        }

        return `
            <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M5 7h14"></path>
                <path d="M9 7V5h6v2"></path>
                <path d="M9 10v7"></path>
                <path d="M15 10v7"></path>
                <path d="M7 7l1 12h8l1-12"></path>
            </svg>
        `;
    }

    function buildImageViewerAttributes(item) {
        const attributes = [
            'data-open-image-viewer',
            `data-image-src="${escapeHtml(item.src)}"`,
            `data-image-name="${escapeHtml(item.name || "")}"`,
            `data-image-alt="${escapeHtml(item.alt)}"`,
        ];

        if (item.deletable) {
            attributes.push('data-image-can-remove="true"');
            attributes.push(`data-image-kind="${escapeHtml(item.kind || "")}"`);
            attributes.push(`data-image-id="${escapeHtml(item.id || "")}"`);
        }

        return attributes.join(" ");
    }

    function renderImagePreviewGrid(items) {
        imagePreviewGrid.innerHTML = items.map((item, index) => {
            const primaryClass = index === 0 && items.length > 1 ? " is-primary" : "";
            const badge = item.badge ? `<span class="image-preview-badge">${escapeHtml(item.badge)}</span>` : "";
            return `
                <figure class="image-preview-tile${primaryClass}">
                    <button
                        type="button"
                        class="image-preview-open"
                        ${buildImageViewerAttributes(item)}
                        aria-label="${strings.viewImage}"
                        title="${strings.viewImage}"
                    >
                        <img src="${item.src}" alt="${escapeHtml(item.alt)}">
                    </button>
                    ${badge}
                    <div class="image-tile-actions">
                        <a
                            class="image-tile-action"
                            href="${escapeHtml(item.src)}"
                            download="${escapeHtml(item.name || `trade-image-${index + 1}.jpg`)}"
                            aria-label="${strings.downloadImage}"
                            title="${strings.downloadImage}"
                            data-download-image
                        >
                            ${renderActionIcon("download")}
                        </a>
                        ${item.deletable ? `
                            <button
                                type="button"
                                class="image-tile-action is-danger"
                                data-remove-preview-image="${escapeHtml(item.kind || "")}"
                                data-image-id="${escapeHtml(item.id || "")}"
                                aria-label="${strings.removeImage}"
                                title="${strings.removeImage}"
                            >
                                ${renderActionIcon("remove")}
                            </button>
                        ` : ""}
                    </div>
                </figure>
            `;
        }).join("");
    }

    function rebuildImagePreview() {
        const existingScreenshots = state.existingScreenshots || [];
        const previewUrls = state.previewObjectUrls || [];
        const previewFiles = state.compressedScreenshotFiles || [];
        const items = [
            ...existingScreenshots.map((screenshot, index) => ({
                kind: "existing",
                id: String(screenshot.id ?? `fallback-${index}`),
                src: screenshot.url,
                alt: `${strings.screenshotAltPrefix} ${index + 1}`,
                name: screenshot.name || `trade-image-${index + 1}.jpg`,
                badge: strings.imageCurrentBadge,
                deletable: true,
            })),
            ...previewUrls.map((url, index) => ({
                kind: "new",
                id: String(index),
                src: url,
                alt: `${strings.screenshotAltPrefix} ${existingScreenshots.length + index + 1}`,
                name: previewFiles[index]?.name || `trade-image-${existingScreenshots.length + index + 1}.jpg`,
                badge: strings.imageNewBadge,
                deletable: true,
            })),
        ];

        if (!items.length) {
            imagePreview.hidden = true;
            imagePreviewGrid.innerHTML = "";
            imagePreviewName.textContent = strings.noImageSelected;
            imagePreviewSize.textContent = "--";
            return;
        }

        renderImagePreviewGrid(items);

        if (existingScreenshots.length && previewFiles.length) {
            const originalTotal = previewFiles.reduce((sum, file) => sum + (file.originalSize || file.size), 0);
            const compressedTotal = previewFiles.reduce((sum, file) => sum + file.size, 0);
            imagePreviewName.textContent = formatImageCountLabel(items.length, "gallery");
            imagePreviewSize.textContent = `${formatImageCountLabel(previewFiles.length, "new")} | ${formatFileSize(originalTotal)} -> ${formatFileSize(compressedTotal)}`;
        } else if (previewFiles.length) {
            const originalTotal = previewFiles.reduce((sum, file) => sum + (file.originalSize || file.size), 0);
            const compressedTotal = previewFiles.reduce((sum, file) => sum + file.size, 0);
            imagePreviewName.textContent = formatImageCountLabel(previewFiles.length, "selected");
            imagePreviewSize.textContent = `${formatFileSize(originalTotal)} -> ${formatFileSize(compressedTotal)}`;
        } else {
            imagePreviewName.textContent = formatImageCountLabel(existingScreenshots.length, "existing");
            imagePreviewSize.textContent = strings.imageKeepHint;
        }

        imagePreview.hidden = false;
    }

    function resetImagePreview() {
        state.compressedScreenshotFiles = [];
        state.existingScreenshots = [];
        state.removedScreenshotIds = new Set();
        revokePreviewUrls();
        rebuildImagePreview();
    }

    function showExistingImagePreview(screenshots) {
        state.existingScreenshots = Array.isArray(screenshots)
            ? screenshots.filter((item) => item && item.url).map((item, index) => ({
                id: item.id ?? `fallback-${index}`,
                url: item.url,
                name: item.name || `trade-image-${index + 1}.jpg`,
            }))
            : [];
        state.removedScreenshotIds = new Set();
        revokePreviewUrls();
        state.compressedScreenshotFiles = [];
        rebuildImagePreview();
    }

    function updateModalOpenState() {
        const hasVisibleModal = !tradeModal.hidden || !panelModal.hidden || !detailModal.hidden || !monthTradesModal.hidden || !imageViewerModal.hidden;
        document.body.classList.toggle("modal-open", hasVisibleModal);
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

    function buildTradeUpdateUrl(tradeId) {
        return endpoints.tradeUpdateBase.replace("/0/update/", `/${tradeId}/update/`);
    }

    function getTradeScreenshots(trade) {
        if (Array.isArray(trade?.screenshots) && trade.screenshots.length) {
            return trade.screenshots.filter((item) => item && item.url).map((item, index) => ({
                id: item.id ?? `fallback-${index}`,
                url: item.url,
                name: item.name || `trade-image-${index + 1}.jpg`,
            }));
        }
        if (Array.isArray(trade?.screenshot_urls) && trade.screenshot_urls.length) {
            return trade.screenshot_urls.filter(Boolean).map((url, index) => ({
                id: `fallback-${index}`,
                url,
                name: `trade-image-${index + 1}.jpg`,
            }));
        }
        return trade?.screenshot_url ? [{
            id: "fallback-0",
            url: trade.screenshot_url,
            name: "trade-image-1.jpg",
        }] : [];
    }

    function getTradeScreenshotUrls(trade) {
        return getTradeScreenshots(trade).map((item) => item.url);
    }

    function getTradeScreenshotCount(trade) {
        const explicitCount = Number.parseInt(trade?.screenshot_count, 10);
        if (Number.isFinite(explicitCount)) {
            return explicitCount;
        }
        return getTradeScreenshots(trade).length;
    }

    function renderTradeImageCountBadge(trade) {
        return `<span class="trade-media-pill">${formatTradeImageCount(getTradeScreenshotCount(trade))}</span>`;
    }

    function renderTradeImageCover(trade, imageClass) {
        const screenshots = getTradeScreenshots(trade);
        if (!screenshots.length) {
            return "";
        }
        const countBadge = screenshots.length > 1
            ? `<span class="trade-image-count">+${screenshots.length - 1}</span>`
            : "";
        return `
            <div class="trade-image-frame">
                <img class="${imageClass}" src="${screenshots[0].url}" alt="${strings.screenshotAltPrefix} ${escapeHtml(trade.symbol)}">
                ${countBadge}
            </div>
        `;
    }

    function renderTradeImageGallery(trade) {
        const screenshots = getTradeScreenshots(trade);
        if (!screenshots.length) {
            return "";
        }
        return `
            <section class="detail-section">
                <h3>${strings.tradeImages}</h3>
                <div class="detail-image-gallery">
                    ${screenshots.map((screenshot, index) => {
                        const primaryClass = index === 0 && screenshots.length > 1 ? " is-primary" : "";
                        return `
                            <button
                                type="button"
                                class="detail-image-tile${primaryClass}"
                                data-open-image-viewer
                                data-image-src="${escapeHtml(screenshot.url)}"
                                data-image-name="${escapeHtml(screenshot.name || `trade-image-${index + 1}.jpg`)}"
                                data-image-alt="${strings.screenshotAltPrefix} ${index + 1} ${escapeHtml(trade.symbol)}"
                                aria-label="${strings.viewImage}"
                                title="${strings.viewImage}"
                            >
                                <img class="detail-image" src="${screenshot.url}" alt="${strings.screenshotAltPrefix} ${index + 1} ${escapeHtml(trade.symbol)}">
                            </button>
                        `;
                    }).join("")}
                </div>
            </section>
        `;
    }

    function setTradeModalMode(mode = "create") {
        const isEdit = mode === "edit";
        tradeModalTitle.textContent = isEdit ? strings.editTrade : strings.newTrade;
        tradeFormSubmitButton.textContent = isEdit ? strings.saveChanges : strings.saveTrade;
    }

    function formatDateTimeLocal(isoDateString) {
        const value = new Date(isoDateString);
        if (Number.isNaN(value.getTime())) {
            return "";
        }
        const local = new Date(value.getTime() - (value.getTimezoneOffset() * 60000));
        return local.toISOString().slice(0, 16);
    }

    function fillTradeForm(trade) {
        if (!trade) {
            return;
        }

        tradeForm.reset();
        resetImagePreview();
        state.editingTradeId = trade.id;
        state.editingCapitalBase = trade.capital_base_value || null;
        state.editingCapitalBaseFormatted = trade.capital_base_formatted || null;
        setTradeModalMode("edit");
        document.getElementById("executed_at").value = trade.executed_at_input || formatDateTimeLocal(trade.executed_at);
        document.getElementById("entry_price").value = trade.entry_price_value || "0.0001";
        symbolInput.value = trade.symbol || "";
        directionInput.value = trade.direction_code || (trade.direction === "Short" ? "SHORT" : "LONG");
        resultInput.value = trade.result_code || trade.result || "TAKE_PROFIT";
        setupInput.value = trade.setup || "";
        confidenceInput.value = String(trade.confidence_value || trade.confidence || "3");
        ratioInput.value = trade.ratio_value ?? (trade.ratio == null ? "" : String(Math.abs(trade.ratio)));
        lotSizeInput.value = trade.lot_size_value ?? (trade.lot_size == null ? "" : String(trade.lot_size));
        gpValueInput.value = trade.gp_value_value ?? (trade.gp_value == null ? "" : String(Math.abs(trade.gp_value)));
        document.getElementById("notes").value = trade.notes || "";
        screenshotInput.value = "";
        showExistingImagePreview(getTradeScreenshots(trade));
        updateTradeCapitalHint();
        updateCapitalImpactPreview();
    }

    function openTradeModal() {
        state.editingTradeId = null;
        state.editingCapitalBase = null;
        state.editingCapitalBaseFormatted = null;
        setTradeModalMode("create");
        tradeForm.reset();
        resetImagePreview();
        seedExecutedAt();
        openModal(tradeModal);
        window.setTimeout(() => {
            symbolInput.focus();
        }, 40);
    }

    function closeTradeModal() {
        closeModal(tradeModal);
    }

    function closePanelModal() {
        if (state.expandedPanelChart) {
            state.expandedPanelChart.destroy();
            state.expandedPanelChart = null;
        }
        closeModal(panelModal);
    }

    function closeDetailModal() {
        closeModal(detailModal);
    }

    function closeMonthTradesModal() {
        closeModal(monthTradesModal);
    }

    function closeImageViewer() {
        state.imageViewerContext = null;
        imageViewerImage.removeAttribute("src");
        imageViewerImage.alt = "";
        imageViewerDownload.removeAttribute("href");
        imageViewerDownload.removeAttribute("download");
        imageViewerTitle.textContent = strings.imagePreviewTitle;
        imageViewerRemoveButton.hidden = true;
        imageViewerRemoveButton.dataset.imageKind = "";
        imageViewerRemoveButton.dataset.imageId = "";
        closeModal(imageViewerModal);
    }

    async function handleScreenshotChange(event) {
        const files = Array.from(event.target.files || []);
        if (!files.length) {
            return;
        }

        if (files.some((file) => !file.type.startsWith("image/"))) {
            screenshotInput.value = "";
            showFlash(strings.imageTypeError, "error");
            return;
        }

        try {
            const compressedFiles = [];
            for (const file of files) {
                const compressedFile = await compressImageFile(file);
                compressedFile.originalSize = file.size;
                compressedFiles.push(compressedFile);
            }
            state.compressedScreenshotFiles = [
                ...state.compressedScreenshotFiles,
                ...compressedFiles,
            ];
            state.previewObjectUrls = [
                ...state.previewObjectUrls,
                ...compressedFiles.map((file) => URL.createObjectURL(file)),
            ];
            screenshotInput.value = "";
            rebuildImagePreview();
        } catch (error) {
            screenshotInput.value = "";
            showFlash(error.message || strings.imageCompressionFailed, "error");
        }
    }

    function openImageViewer({ src, name, alt, imageKind = "", imageId = "", allowRemove = false }) {
        if (!src) {
            return;
        }

        state.imageViewerContext = allowRemove
            ? { imageKind, imageId }
            : null;
        imageViewerTitle.textContent = name || strings.imagePreviewTitle;
        imageViewerImage.src = src;
        imageViewerImage.alt = alt || name || strings.imagePreviewTitle;
        imageViewerDownload.href = src;
        imageViewerDownload.download = name || "trade-image.jpg";
        imageViewerRemoveButton.hidden = !allowRemove;
        imageViewerRemoveButton.dataset.imageKind = allowRemove ? imageKind : "";
        imageViewerRemoveButton.dataset.imageId = allowRemove ? imageId : "";
        openModal(imageViewerModal);
    }

    function openImageViewerFromTrigger(trigger) {
        if (!trigger) {
            return;
        }

        openImageViewer({
            src: trigger.dataset.imageSrc,
            name: trigger.dataset.imageName,
            alt: trigger.dataset.imageAlt,
            imageKind: trigger.dataset.imageKind,
            imageId: trigger.dataset.imageId,
            allowRemove: trigger.dataset.imageCanRemove === "true",
        });
    }

    function removeExistingPreviewImage(imageId) {
        if (!imageId) {
            return;
        }

        state.existingScreenshots = state.existingScreenshots.filter(
            (screenshot) => String(screenshot.id) !== String(imageId),
        );
        if (!String(imageId).startsWith("fallback-")) {
            state.removedScreenshotIds.add(String(imageId));
        }
        rebuildImagePreview();
    }

    function removeNewPreviewImage(imageId) {
        const previewIndex = Number.parseInt(imageId, 10);
        if (!Number.isFinite(previewIndex) || previewIndex < 0) {
            return;
        }

        state.compressedScreenshotFiles.splice(previewIndex, 1);
        removePreviewUrlAt(previewIndex);
        rebuildImagePreview();
    }

    function handleImagePreviewGridClick(event) {
        if (event.target.closest("[data-download-image]")) {
            return;
        }

        const removeTrigger = event.target.closest("[data-remove-preview-image]");
        if (removeTrigger) {
            event.preventDefault();
            const imageKind = removeTrigger.dataset.removePreviewImage;
            const imageId = removeTrigger.dataset.imageId;
            if (imageKind === "existing") {
                removeExistingPreviewImage(imageId);
            } else if (imageKind === "new") {
                removeNewPreviewImage(imageId);
            }
            return;
        }

        const viewerTrigger = event.target.closest("[data-open-image-viewer]");
        if (viewerTrigger) {
            event.preventDefault();
            openImageViewerFromTrigger(viewerTrigger);
        }
    }

    function handleImageViewerTriggerClick(event) {
        const viewerTrigger = event.target.closest("[data-open-image-viewer]");
        if (!viewerTrigger) {
            return;
        }

        event.preventDefault();
        openImageViewerFromTrigger(viewerTrigger);
    }

    function handleImageViewerRemove() {
        const imageKind = imageViewerRemoveButton.dataset.imageKind;
        const imageId = imageViewerRemoveButton.dataset.imageId;
        if (imageKind === "existing") {
            removeExistingPreviewImage(imageId);
        } else if (imageKind === "new") {
            removeNewPreviewImage(imageId);
        }
        closeImageViewer();
    }

    async function compressImageFile(file) {
        const sourceImage = await loadImageFile(file);
        const maxDimension = 1600;
        const ratio = Math.min(maxDimension / sourceImage.width, maxDimension / sourceImage.height, 1);
        const canvas = document.createElement("canvas");
        canvas.width = Math.max(1, Math.round(sourceImage.width * ratio));
        canvas.height = Math.max(1, Math.round(sourceImage.height * ratio));

        const context = canvas.getContext("2d");
        context.drawImage(sourceImage, 0, 0, canvas.width, canvas.height);

        const outputType = "image/jpeg";
        const targetMaxBytes = 900 * 1024;
        let quality = 0.82;
        let blob = await canvasToBlob(canvas, outputType, quality);

        while (blob.size > targetMaxBytes && quality > 0.45) {
            quality -= 0.08;
            blob = await canvasToBlob(canvas, outputType, quality);
        }

        const baseName = file.name.replace(/\.[^.]+$/, "") || "trade";
        return new File([blob], `${baseName}-compressed.jpg`, { type: outputType });
    }

    function loadImageFile(file) {
        return new Promise((resolve, reject) => {
            const url = URL.createObjectURL(file);
            const image = new Image();
            image.onload = () => {
                URL.revokeObjectURL(url);
                resolve(image);
            };
            image.onerror = () => {
                URL.revokeObjectURL(url);
                reject(new Error("Image invalide ou non lisible."));
            };
            image.src = url;
        });
    }

    function canvasToBlob(canvas, type, quality) {
        return new Promise((resolve, reject) => {
            canvas.toBlob((blob) => {
                if (!blob) {
                    reject(new Error("La compression a echoue."));
                    return;
                }
                resolve(blob);
            }, type, quality);
        });
    }

    function setBusy(isBusy, loaderMessage = strings.loadingDashboard) {
        setButtonLoading(refreshButton, isBusy, strings.loading);
        if (demoButton && !demoButton.classList.contains("is-loading")) {
            demoButton.disabled = isBusy;
        }
        togglePageLoader(pageLoader, isBusy, loaderMessage);
    }

    async function loadDashboard(month = "") {
        if (state.controller) {
            state.controller.abort();
        }

        const controller = new AbortController();
        state.controller = controller;
        setBusy(true, strings.loadingDashboardDetails);

        try {
            const url = new URL(endpoints.dashboard, window.location.origin);
            if (month) {
                url.searchParams.set("month", month);
            }

            const response = await fetch(url, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
                signal: controller.signal,
            });

            if (!response.ok) {
                throw new Error(strings.dashboardFailed);
            }

            const payload = await response.json();
            renderDashboard(payload);
            lastUpdate.textContent = `${strings.lastUpdatePrefix} ${new Date().toLocaleTimeString(uiLocale, { hour: "2-digit", minute: "2-digit" })}`;
        } catch (error) {
            if (error.name !== "AbortError") {
                showFlash(error.message, "error");
            }
        } finally {
            if (state.controller === controller) {
                state.controller = null;
                setBusy(false);
            }
        }
    }

    function renderDashboard(payload) {
        state.lastPayload = payload;
        state.preferences = payload.preferences || state.preferences;
        indexPayloadDetails(payload);
        renderMonthOptions(payload.available_months, payload.summary.selected_month);
        renderOverview(payload.overview, payload.summary.selected_month_label);
        renderMetrics(payload.metrics);
        renderScorecard(payload.scorecard, payload.overview.score);
        renderCharts(payload.charts);
        renderCalendar(payload.calendar);
        renderRecentTrades(payload.recent_trades);
        renderMonthlyTrades(payload.monthly_trades || [], payload.summary.selected_month_label);
        updateTradeCapitalHint();
        if (demoButton) {
            demoButton.hidden = payload.overview.all_time_trade_count > 0;
        }
    }

    function indexPayloadDetails(payload) {
        state.tradeLookup = new Map();
        state.dayTradeMap = payload.calendar.trade_map || {};
        state.calendarDayMap = {};

        payload.recent_trades.forEach((trade) => {
            state.tradeLookup.set(String(trade.id), trade);
        });

        (payload.monthly_trades || []).forEach((trade) => {
            state.tradeLookup.set(String(trade.id), trade);
        });

        Object.entries(state.dayTradeMap).forEach(([date, trades]) => {
            trades.forEach((trade) => {
                state.tradeLookup.set(String(trade.id), trade);
            });
        });

        payload.calendar.rows.flat().forEach((day) => {
            state.calendarDayMap[day.iso] = day;
        });
    }

    function buildTradeCardMarkup(trade) {
        return `
            <button type="button" class="recent-trade recent-trade-button" data-trade-id="${trade.id}">
                <div class="recent-trade-header">
                    <div class="recent-trade-title">
                        <strong>${escapeHtml(trade.symbol)} | ${escapeHtml(trade.direction)}</strong>
                        <span>${escapeHtml(trade.setup)}</span>
                    </div>
                    ${renderTradeImageCountBadge(trade)}
                </div>
                <div class="recent-trade-meta">
                    <span>${escapeHtml(trade.executed_at_label)}</span>
                    <span class="pnl-pill ${trade.pnl_tone}">${escapeHtml(trade.pnl_formatted)}</span>
                </div>
                <div class="recent-trade-meta">
                    <span>${escapeHtml(trade.result_label)} | ${escapeHtml(trade.ratio_label)}</span>
                    <span>${escapeHtml(trade.gp_value_label)} | ${escapeHtml(trade.capital_change_percent_label)}</span>
                </div>
                <div class="recent-trade-meta">
                    <span>${escapeHtml(trade.market)}</span>
                </div>
            </button>
        `;
    }

    function renderMonthOptions(options, selectedValue) {
        monthSelector.innerHTML = options.map((option) => {
            const selected = option.value === selectedValue ? "selected" : "";
            return `<option value="${option.value}" ${selected}>${option.label}</option>`;
        }).join("");
    }

    function renderOverview(overview, selectedMonthLabel) {
        document.getElementById("sidebar-score").textContent = overview.score;
        document.getElementById("sidebar-month").textContent = selectedMonthLabel;
        document.getElementById("overview-pnl").textContent = overview.all_time_pnl;
        document.getElementById("overview-trades").textContent = overview.all_time_trade_count;
        document.getElementById("overview-setup").textContent = overview.best_setup;
    }

    function renderMetrics(metrics) {
        metricsGrid.innerHTML = metrics.map((metric) => {
            return `
                <article class="metric-card ${metric.tone}">
                    <div class="metric-card-header">
                        <div class="metric-card-copy">
                            <span class="metric-card-title">${metric.label}</span>
                            <strong class="metric-card-value">${metric.value}</strong>
                            <p class="metric-card-detail">${metric.detail}</p>
                        </div>
                        <div class="metric-ring" style="--progress:${metric.progress};"></div>
                    </div>
                    <div class="metric-progress" style="--progress:${metric.progress}%;"><span></span></div>
                </article>
            `;
        }).join("");
    }

    function renderScorecard(scorecard, scoreValue) {
        document.getElementById("score-pill").textContent = `Score ${scoreValue}`;
        document.getElementById("score-value").textContent = scorecard.value;
        document.getElementById("score-caption").textContent = scorecard.caption;
        document.getElementById("insight-list").innerHTML = scorecard.insights.map((line) => {
            return `<li>${line}</li>`;
        }).join("");
    }

    function renderCharts(charts) {
        if (!window.Chart) {
            showFlash(strings.chartMissing, "error");
            return;
        }

        upsertChart("radar", "radar-chart", getChartConfig("radar", charts));
        upsertChart("cumulative", "cumulative-chart", getChartConfig("cumulative", charts));
        upsertChart("daily", "daily-chart", getChartConfig("daily", charts));
        upsertChart("combo", "combo-chart", getChartConfig("combo", charts));
    }

    function getChartConfig(kind, charts, expanded = false) {
        const textColor = "#c6cee1";
        const gridColor = "rgba(255,255,255,0.06)";
        const green = "#35d49a";
        const greenFill = "rgba(53,212,154,0.18)";
        const blue = "#7ab8ff";
        const blueFill = "rgba(122,184,255,0.18)";
        const red = "#ef6464";

        if (kind === "radar") {
            return {
                type: "radar",
                data: {
                    labels: charts.radar.labels,
                    datasets: [{
                        label: "Score",
                        data: charts.radar.values,
                        backgroundColor: "rgba(122,184,255,0.16)",
                        borderColor: blue,
                        borderWidth: 2,
                        pointBackgroundColor: green,
                        pointBorderColor: "#081019",
                        pointHoverRadius: 5,
                    }],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                    },
                    scales: {
                        r: {
                            min: 0,
                            max: 100,
                            ticks: { display: false },
                            grid: { color: gridColor },
                            angleLines: { color: gridColor },
                            pointLabels: {
                                color: textColor,
                                font: { size: expanded ? 13 : 11, family: "Manrope" },
                            },
                        },
                    },
                },
            };
        }

        if (kind === "cumulative") {
            return {
                type: "line",
                data: {
                    labels: fallbackLabels(charts.cumulative.labels),
                    datasets: [{
                        label: "P&L cumulatif",
                        data: fallbackValues(charts.cumulative.values),
                        tension: 0.35,
                        fill: true,
                        borderColor: green,
                        backgroundColor: greenFill,
                        pointRadius: 0,
                    }],
                },
                options: buildCartesianOptions(textColor, gridColor),
            };
        }

        if (kind === "daily") {
            return {
                type: "bar",
                data: {
                    labels: fallbackLabels(charts.daily.labels),
                    datasets: [{
                        label: "P&L journalier",
                        data: fallbackValues(charts.daily.values),
                        borderRadius: 8,
                        backgroundColor: fallbackValues(charts.daily.values).map((value) => value >= 0 ? green : red),
                    }],
                },
                options: buildCartesianOptions(textColor, gridColor),
            };
        }

        return {
            type: "bar",
            data: {
                labels: fallbackLabels(charts.combo.labels),
                datasets: [
                    {
                        type: "bar",
                        label: "P&L journalier",
                        data: fallbackValues(charts.combo.daily),
                        borderRadius: 8,
                        backgroundColor: fallbackValues(charts.combo.daily).map((value) => value >= 0 ? green : red),
                        yAxisID: "y",
                    },
                    {
                        type: "line",
                        label: "Cumulatif",
                        data: fallbackValues(charts.combo.cumulative),
                        tension: 0.35,
                        fill: true,
                        borderColor: blue,
                        backgroundColor: blueFill,
                        pointRadius: 0,
                        yAxisID: "y1",
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: "index",
                    intersect: false,
                },
                plugins: {
                    legend: {
                        labels: {
                            color: textColor,
                            boxWidth: 12,
                        },
                    },
                },
                scales: {
                    x: {
                        ticks: { color: textColor },
                        grid: { color: "transparent" },
                    },
                    y: {
                        ticks: { color: textColor },
                        grid: { color: gridColor },
                    },
                    y1: {
                        position: "right",
                        ticks: { color: textColor },
                        grid: { drawOnChartArea: false },
                    },
                },
            },
        };
    }

    function buildCartesianOptions(textColor, gridColor) {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
            },
            scales: {
                x: {
                    ticks: { color: textColor },
                    grid: { color: "transparent" },
                },
                y: {
                    ticks: { color: textColor },
                    grid: { color: gridColor },
                },
            },
        };
    }

    function upsertChart(key, canvasId, config) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            return;
        }

        if (state.charts[key]) {
            state.charts[key].destroy();
        }

        state.charts[key] = new window.Chart(canvas, config);
    }

    function fallbackLabels(labels) {
        return labels.length ? labels : [strings.noData];
    }

    function fallbackValues(values) {
        return values.length ? values : [0];
    }

    function buildCalendarMarkup(calendar) {
        const gridHtml = calendar.rows.map((row) => {
            return row.map((day) => {
                const toneClass = day.tone === "profit" ? "is-profit" : day.tone === "loss" ? "is-loss" : "";
                const otherClass = day.in_month ? "" : "is-other";
                const clickableClass = day.in_month && day.trade_count ? "is-clickable" : "";
                const subtitle = day.trade_count ? `${day.trade_count} ${strings.dayTradeCountSuffix}` : strings.noExecution;

                if (day.in_month && day.trade_count) {
                    return `
                        <button type="button" class="calendar-cell ${toneClass} ${otherClass} ${clickableClass}" data-calendar-date="${day.iso}">
                            <div class="calendar-cell-top">
                                <span class="calendar-cell-day">${day.day}</span>
                                <span class="calendar-cell-trades">${day.trade_count || ""}</span>
                            </div>
                            <div>
                                <strong class="calendar-cell-value">${day.pnl_formatted}</strong>
                                <div class="calendar-cell-subtitle">${subtitle}</div>
                            </div>
                        </button>
                    `;
                }

                return `
                    <article class="calendar-cell ${toneClass} ${otherClass}">
                        <div class="calendar-cell-top">
                            <span class="calendar-cell-day">${day.day}</span>
                            <span class="calendar-cell-trades">${day.trade_count || ""}</span>
                        </div>
                        <div>
                            <strong class="calendar-cell-value">${day.in_month ? day.pnl_formatted : ""}</strong>
                            <div class="calendar-cell-subtitle">${day.in_month ? subtitle : ""}</div>
                        </div>
                    </article>
                `;
            }).join("");
        }).join("");

        const weekHtml = calendar.week_summaries.map((week) => {
            return `
                <article class="week-summary ${week.tone}">
                    <span>${week.label}</span>
                    <strong>${week.pnl_formatted}</strong>
                    <p>${week.active_days} jour(s) actifs</p>
                </article>
            `;
        }).join("");

        return { gridHtml, weekHtml };
    }

    function renderCalendar(calendar) {
        document.getElementById("calendar-label").textContent = calendar.label;
        const { gridHtml, weekHtml } = buildCalendarMarkup(calendar);
        calendarGrid.innerHTML = gridHtml;
        document.getElementById("calendar-weeks").innerHTML = weekHtml;
    }

    function renderRecentTrades(trades) {
        const container = document.getElementById("recent-trades");

        if (!trades.length) {
            container.innerHTML = `
                <div class="empty-state">
                    ${strings.noExecutionYet}
                </div>
            `;
            return;
        }

        container.innerHTML = trades.map((trade) => buildTradeCardMarkup(trade)).join("");
    }

    function renderMonthlyTrades(trades, selectedMonthLabel) {
        if (monthTradesCount) {
            monthTradesCount.textContent = `${trades.length} ${strings.monthTradesCountSuffix}`;
        }

        if (!monthTradesButton || !monthTradesList || !monthTradesModalSubtitle) {
            return;
        }

        monthTradesButton.hidden = !trades.length;
        monthTradesModalTitle.textContent = strings.monthTradesTitle;
        monthTradesModalSubtitle.textContent = `${trades.length} ${strings.monthTradesSubtitle} ${selectedMonthLabel}`;

        if (!trades.length) {
            monthTradesList.innerHTML = `
                <div class="empty-state">
                    ${strings.monthTradesEmpty}
                </div>
            `;
            return;
        }

        monthTradesList.innerHTML = trades.map((trade) => buildTradeCardMarkup(trade)).join("");
    }

    function handleTradeCardClick(event) {
        if (event.target.closest("[data-edit-trade-id]")) {
            return;
        }

        const tradeTrigger = event.target.closest("[data-trade-id]");
        if (!tradeTrigger) {
            return;
        }

        openTradeDetail(tradeTrigger.dataset.tradeId);
    }

    function handleTradeEditClick(event) {
        const editTrigger = event.target.closest("[data-edit-trade-id]");
        if (!editTrigger) {
            return;
        }

        event.preventDefault();
        event.stopPropagation();
        beginTradeEdit(editTrigger.dataset.editTradeId);
    }

    function handleCalendarCellClick(event) {
        const dateTrigger = event.target.closest("[data-calendar-date]");
        if (!dateTrigger) {
            return;
        }

        const date = dateTrigger.dataset.calendarDate;
        const dayTrades = state.dayTradeMap[date] || [];
        if (!dayTrades.length) {
            return;
        }
        if (dayTrades.length === 1) {
            openTradeDetail(dayTrades[0].id);
            return;
        }

        openDayDetail(date);
    }

    function openMonthTradesModal() {
        if (!state.lastPayload) {
            return;
        }

        const trades = state.lastPayload.monthly_trades || [];
        if (!trades.length) {
            return;
        }

        monthTradesModalTitle.textContent = strings.monthTradesTitle;
        monthTradesModalSubtitle.textContent = `${trades.length} ${strings.monthTradesSubtitle} ${state.lastPayload.summary.selected_month_label}`;
        openModal(monthTradesModal);
    }

    function openPanelModal(kind) {
        if (!state.lastPayload) {
            return;
        }

        const titles = {
            radar: strings.radarTitle,
            cumulative: strings.cumulativeTitle,
            daily: strings.dailyTitle,
            combo: strings.comboTitle,
            calendar: strings.calendarTitle,
        };

        panelModalTitle.textContent = titles[kind] || strings.panelDetailTitle;

        if (kind === "calendar") {
            if (state.expandedPanelChart) {
                state.expandedPanelChart.destroy();
                state.expandedPanelChart = null;
            }
            expandedChartWrap.hidden = true;
            expandedCalendarWrap.hidden = false;
            const { gridHtml, weekHtml } = buildCalendarMarkup(state.lastPayload.calendar);
            expandedCalendarGrid.innerHTML = gridHtml;
            expandedCalendarWeeks.innerHTML = weekHtml;
        } else {
            expandedCalendarWrap.hidden = true;
            expandedChartWrap.hidden = false;

            if (state.expandedPanelChart) {
                state.expandedPanelChart.destroy();
                state.expandedPanelChart = null;
            }

            state.expandedPanelChart = new window.Chart(
                expandedPanelCanvas,
                getChartConfig(kind, state.lastPayload.charts, true),
            );
        }

        openModal(panelModal);
    }

    function formatDisplayDate(dateString) {
        return new Date(`${dateString}T12:00:00`).toLocaleDateString(uiLocale, {
            weekday: "long",
            day: "numeric",
            month: "long",
            year: "numeric",
        });
    }

    function getDirectionTone(direction) {
        return direction === "Short" ? "short" : "long";
    }

    function renderDirectionBadge(direction) {
        return `<span class="direction-badge ${getDirectionTone(direction)}">${escapeHtml(direction)}</span>`;
    }

    function openDayDetail(dateString) {
        const day = state.calendarDayMap[dateString];
        const trades = state.dayTradeMap[dateString] || [];
        detailModalTitle.textContent = formatDisplayDate(dateString);
        detailModalSubtitle.textContent = `${day.trade_count} ${strings.dayTradeCountSuffix} | ${day.pnl_formatted}`;
        detailModalBody.innerHTML = `
            <div class="detail-grid">
                <article class="detail-card">
                    <span>${strings.dayPerformance}</span>
                    <strong>${day.pnl_formatted}</strong>
                </article>
                <article class="detail-card">
                    <span>${strings.executions}</span>
                    <strong>${day.trade_count}</strong>
                </article>
                <article class="detail-card">
                    <span>Statut</span>
                    <strong>${day.tone === "profit" ? strings.positiveDay : day.tone === "loss" ? strings.negativeDay : strings.neutralDay}</strong>
                </article>
            </div>
            <section class="detail-section">
                <h3>${strings.dayExecutionsTitle}</h3>
                <div class="day-trade-list">
                    ${trades.map((trade) => {
                        return `
                            <button type="button" class="day-trade-item" data-trade-id="${trade.id}">
                                ${renderTradeImageCover(trade, "day-trade-thumb")}
                                <div class="day-trade-main">
                                    <div class="day-trade-topline">
                                        <strong>${escapeHtml(trade.symbol)}</strong>
                                        ${renderDirectionBadge(trade.direction)}
                                    </div>
                                    <span>${escapeHtml(trade.result_label)} | ${escapeHtml(trade.setup)} | ${escapeHtml(trade.executed_at_label)}</span>
                                </div>
                                <span class="pnl-pill ${trade.pnl_tone}">${escapeHtml(trade.pnl_formatted)}</span>
                            </button>
                        `;
                    }).join("")}
                </div>
            </section>
        `;
        openModal(detailModal);
    }

    function openTradeDetail(tradeId) {
        const trade = state.tradeLookup.get(String(tradeId));
        if (!trade) {
            return;
        }

        if (!monthTradesModal.hidden) {
            closeMonthTradesModal();
        }

        detailModalTitle.textContent = `${trade.symbol} | ${trade.direction}`;
        detailModalSubtitle.textContent = `${trade.setup} | ${trade.executed_at_label}`;
        detailModalBody.innerHTML = `
            <div class="detail-hero">
                <div class="detail-hero-copy">
                    ${renderDirectionBadge(trade.direction)}
                    <div class="detail-hero-badges">
                        <span class="detail-meta-pill">${escapeHtml(trade.result_label)}</span>
                        <span class="detail-meta-pill">${escapeHtml(trade.market)}</span>
                        <span class="detail-meta-pill">${escapeHtml(trade.executed_at_label)}</span>
                    </div>
                    <p>${escapeHtml(trade.setup)}</p>
                </div>
                <span class="pnl-pill ${trade.pnl_tone}">${escapeHtml(trade.pnl_formatted)}</span>
            </div>
            ${renderTradeImageGallery(trade)}
            <div class="detail-grid">
                <article class="detail-card">
                    <span>${strings.dateTime}</span>
                    <strong>${escapeHtml(trade.executed_at_label)}</strong>
                </article>
                <article class="detail-card">
                    <span>${strings.setup}</span>
                    <strong>${escapeHtml(trade.setup)}</strong>
                </article>
                <article class="detail-card">
                    <span>${strings.result}</span>
                    <strong>${escapeHtml(trade.result_label)}</strong>
                </article>
                <article class="detail-card">
                    <span>${strings.netPnl}</span>
                    <strong>${escapeHtml(trade.pnl_formatted)}</strong>
                </article>
                <article class="detail-card">
                    <span>${strings.gpValue}</span>
                    <strong>${escapeHtml(trade.gp_value_label)}</strong>
                </article>
                <article class="detail-card">
                    <span>${strings.ratio}</span>
                    <strong>${escapeHtml(trade.ratio_label)}</strong>
                </article>
                <article class="detail-card">
                    <span>${strings.lots}</span>
                    <strong>${escapeHtml(trade.lot_size_label)}</strong>
                </article>
                <article class="detail-card">
                    <span>${strings.capitalPercent}</span>
                    <strong>${escapeHtml(trade.capital_change_percent_label)}</strong>
                </article>
                <article class="detail-card">
                    <span>${strings.confidence}</span>
                    <strong>${escapeHtml(trade.confidence_label)}</strong>
                </article>
                <article class="detail-card">
                    <span>${strings.capitalReference}</span>
                    <strong>${escapeHtml(trade.capital_base_formatted)}</strong>
                </article>
                <article class="detail-card">
                    <span>${strings.riskAmount}</span>
                    <strong>${escapeHtml(trade.risk_amount_formatted)}</strong>
                </article>
            </div>
            <section class="detail-section">
                <h3>${strings.notes}</h3>
                <p>${escapeHtml(trade.notes || strings.noNotes)}</p>
            </section>
            <div class="detail-actions">
                <button type="button" class="ghost-button" data-edit-trade-id="${trade.id}">
                    ${strings.editTradeButton}
                </button>
            </div>
        `;
        openModal(detailModal);
    }

    function beginTradeEdit(tradeId) {
        const trade = state.tradeLookup.get(String(tradeId));
        if (!trade) {
            return;
        }

        closeDetailModal();
        fillTradeForm(trade);
        openModal(tradeModal);
        window.setTimeout(() => {
            symbolInput.focus();
        }, 40);
    }

    async function handleTradeSubmit(event) {
        event.preventDefault();
        const formData = new FormData(tradeForm);
        formData.delete("screenshots");
        formData.delete("removed_screenshot_ids");
        state.compressedScreenshotFiles.forEach((file) => {
            formData.append("screenshots", file, file.name);
        });
        state.removedScreenshotIds.forEach((imageId) => {
            formData.append("removed_screenshot_ids", imageId);
        });
        const submitButton = tradeFormSubmitButton;
        const isEdit = Boolean(state.editingTradeId);
        const endpoint = isEdit ? buildTradeUpdateUrl(state.editingTradeId) : endpoints.trade;

        setButtonLoading(submitButton, true, isEdit ? strings.saveChanges : strings.saveTrade);
        togglePageLoader(pageLoader, true, isEdit ? strings.loadingTradeUpdate : strings.loadingTradeSave);

        try {
            const response = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCsrfToken(),
                },
                body: formData,
            });

            const result = await response.json();

            if (!response.ok) {
                const message = flattenErrors(result.errors) || result.message || strings.tradeSaveFailed;
                throw new Error(message);
            }

            showFlash(
                isEdit
                    ? strings.tradeUpdated
                    : strings.tradeSaved,
                "success",
            );
            tradeForm.reset();
            state.editingTradeId = null;
            state.editingCapitalBase = null;
            state.editingCapitalBaseFormatted = null;
            setTradeModalMode("create");
            resetImagePreview();
            seedExecutedAt();
            closeTradeModal();
            await loadDashboard(result.trade.executed_at.slice(0, 7));
        } catch (error) {
            showFlash(error.message, "error");
        } finally {
            setButtonLoading(submitButton, false);
            if (!state.controller) {
                togglePageLoader(pageLoader, false);
            }
        }
    }

    async function handleDemoSeed() {
        if (!demoButton) {
            return;
        }
        setButtonLoading(demoButton, true, strings.loading);
        togglePageLoader(pageLoader, true, strings.loadingDemo);

        try {
            const response = await fetch(endpoints.demo, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCsrfToken(),
                },
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.message || strings.demoLoadFailed);
            }

            showFlash(result.message, "success");
            await loadDashboard();
        } catch (error) {
            showFlash(error.message, "error");
        } finally {
            setButtonLoading(demoButton, false);
            if (!state.controller) {
                togglePageLoader(pageLoader, false);
            }
        }
    }

    function flattenErrors(errors = {}) {
        return Object.values(errors)
            .flat()
            .map((entry) => entry.message)
            .join(" ");
    }
}

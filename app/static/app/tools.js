(function () {
    const app = document.getElementById("tools-app");
    if (!(app instanceof HTMLElement)) {
        return;
    }

    const langCode = (document.documentElement.lang || "fr").toLowerCase();
    const locale = document.body.dataset.uiLocale || "fr-FR";
    const currencyCode = app.dataset.currencyCode || "USD";
    const defaultRiskPercent = Math.max(0, parseNumber(app.dataset.defaultRiskPercent, 1));
    const toolsModal = document.getElementById("tools-modal");
    const toolsModalTitle = document.getElementById("tools-modal-title");
    const toolsModalCopy = document.getElementById("tools-modal-copy");
    const toolPanels = Array.from(app.querySelectorAll("[data-tool-panel]"));
    const calculatorHistoryNode = document.getElementById("calculator-history");
    const calculatorDisplayNode = document.getElementById("calculator-display");
    let activeTool = "risk-trade";

    const strings = langCode.startsWith("fr") ? {
        calculatorError: "Erreur",
        toolDefaultTitle: "Outil",
        toolDefaultCopy: "Execute les calculs de ce module dans le compte actif.",
        riskTradeNote: "{percent} du capital actuel = {value}.",
        marginUsed: "Marge utilisee: {value} du capital.",
        ruinNotePositive: "Estimation probabiliste basee sur le win rate, le payoff moyen et le risque par trade.",
        ruinNoteNegative: "Expectancy negative ou nulle: la probabilite de ruine est consideree comme elevee.",
    } : {
        calculatorError: "Error",
        toolDefaultTitle: "Tool",
        toolDefaultCopy: "Run calculations for this module using the active account.",
        riskTradeNote: "{percent} of current capital = {value}.",
        marginUsed: "Margin used: {value} of capital.",
        ruinNotePositive: "Probability estimate based on win rate, average payoff, and risk per trade.",
        ruinNoteNegative: "Negative or zero expectancy: risk of ruin is considered high.",
    };

    const calculatorState = {
        expression: "",
        history: "0",
        display: "0",
        lastResult: 0,
        justEvaluated: false,
        hasError: false,
    };

    function parseNumber(value, fallback = 0) {
        const parsed = Number.parseFloat(String(value ?? "").replace(",", "."));
        return Number.isFinite(parsed) ? parsed : fallback;
    }

    function trimTrailingZeroDecimals(value) {
        return String(value ?? "").replace(/([.,])00(?=(?:\s*[^\d\s]+)?\s*$)/, "");
    }

    function formatNumber(value, digits = 2) {
        if (!Number.isFinite(value)) {
            return "--";
        }
        return trimTrailingZeroDecimals(new Intl.NumberFormat(locale, {
            minimumFractionDigits: digits,
            maximumFractionDigits: digits,
        }).format(value));
    }

    function formatSignedNumber(value, digits = 2) {
        if (!Number.isFinite(value)) {
            return "--";
        }
        return `${value > 0 ? "+" : ""}${formatNumber(value, digits)}`;
    }

    function formatCurrency(value) {
        if (!Number.isFinite(value)) {
            return "--";
        }
        return trimTrailingZeroDecimals(new Intl.NumberFormat(locale, {
            style: "currency",
            currency: currencyCode,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }).format(value));
    }

    function formatSignedCurrency(value) {
        if (!Number.isFinite(value)) {
            return "--";
        }
        return `${value > 0 ? "+" : ""}${formatCurrency(value)}`;
    }

    function formatPercent(value, digits = 2) {
        if (!Number.isFinite(value)) {
            return "--";
        }
        return `${formatNumber(value, digits)}%`;
    }

    function formatCalculatorValue(value) {
        if (!Number.isFinite(value)) {
            return strings.calculatorError;
        }

        const absoluteValue = Math.abs(value);
        if ((absoluteValue >= 1000000000) || (absoluteValue > 0 && absoluteValue < 0.000001)) {
            return value.toExponential(6).replace(/\.?0+e/, "e");
        }

        return new Intl.NumberFormat(locale, {
            minimumFractionDigits: 0,
            maximumFractionDigits: 8,
        }).format(value);
    }

    function setText(id, value) {
        const node = document.getElementById(id);
        if (node) {
            node.textContent = value;
        }
    }

    function getToolMeta(toolKey) {
        const panel = toolPanels.find((item) => item.dataset.toolPanel === toolKey) || null;
        const heading = panel?.querySelector("h2")?.textContent?.trim() || strings.toolDefaultTitle;
        const copy = panel?.querySelector(".tool-copy")?.textContent?.trim() || strings.toolDefaultCopy;

        return {
            panel,
            title: heading,
            copy,
        };
    }

    function setActiveTool(toolKey, meta = {}) {
        const match = getToolMeta(toolKey);
        const panel = match.panel || getToolMeta("calculator").panel;

        if (!(panel instanceof HTMLElement)) {
            return;
        }

        activeTool = panel.dataset.toolPanel || "calculator";
        toolPanels.forEach((item) => {
            item.classList.toggle("is-active", item === panel);
        });

        if (toolsModalTitle) {
            toolsModalTitle.textContent = meta.title || match.title;
        }
        if (toolsModalCopy) {
            toolsModalCopy.textContent = meta.copy || match.copy;
        }
    }

    function prettifyExpression(expression) {
        return expression.replace(/\*/g, "x");
    }

    function isOperator(value) {
        return ["+", "-", "*", "/"].includes(value);
    }

    function countOccurrences(source, pattern) {
        return (source.match(pattern) || []).length;
    }

    function safeEvaluate(expression) {
        if (!expression || !/^[0-9+\-*/().\s]+$/.test(expression)) {
            return { ok: false, value: 0 };
        }

        try {
            const result = Function(`"use strict"; return (${expression});`)();
            if (!Number.isFinite(result)) {
                return { ok: false, value: 0 };
            }

            return { ok: true, value: result };
        } catch (error) {
            return { ok: false, value: 0 };
        }
    }

    function renderCalculator() {
        if (calculatorHistoryNode) {
            calculatorHistoryNode.textContent = calculatorState.history || "0";
        }
        if (calculatorDisplayNode) {
            if (calculatorState.hasError) {
                calculatorDisplayNode.textContent = strings.calculatorError;
                return;
            }

            if (calculatorState.justEvaluated) {
                calculatorDisplayNode.textContent = calculatorState.display;
                return;
            }

            calculatorDisplayNode.textContent = calculatorState.expression
                ? prettifyExpression(calculatorState.expression)
                : "0";
        }
    }

    function clearCalculator() {
        calculatorState.expression = "";
        calculatorState.history = "0";
        calculatorState.display = "0";
        calculatorState.lastResult = 0;
        calculatorState.justEvaluated = false;
        calculatorState.hasError = false;
        renderCalculator();
    }

    function showCalculatorError() {
        calculatorState.history = calculatorState.expression
            ? `${prettifyExpression(calculatorState.expression)} =`
            : "0";
        calculatorState.display = strings.calculatorError;
        calculatorState.justEvaluated = false;
        calculatorState.hasError = true;
        renderCalculator();
    }

    function getCurrentNumberToken() {
        const tokens = calculatorState.expression.split(/[+\-*/()]/);
        return tokens[tokens.length - 1] || "";
    }

    function appendCalculatorValue(value) {
        if (!value) {
            return;
        }

        if (calculatorState.hasError) {
            clearCalculator();
        }

        if (calculatorState.justEvaluated) {
            if (/[0-9.(]/.test(value)) {
                calculatorState.expression = "";
            } else if (isOperator(value)) {
                calculatorState.expression = String(calculatorState.lastResult);
            }
            calculatorState.history = "0";
            calculatorState.justEvaluated = false;
        }

        const lastCharacter = calculatorState.expression.slice(-1);

        if (value === "(") {
            if (calculatorState.expression && /[0-9.)]/.test(lastCharacter)) {
                calculatorState.expression += "*";
            }
            calculatorState.expression += value;
            renderCalculator();
            return;
        }

        if (value === ")") {
            const openCount = countOccurrences(calculatorState.expression, /\(/g);
            const closeCount = countOccurrences(calculatorState.expression, /\)/g);
            if (!calculatorState.expression || openCount <= closeCount || isOperator(lastCharacter) || lastCharacter === "(") {
                return;
            }
            calculatorState.expression += value;
            renderCalculator();
            return;
        }

        if (value === ".") {
            const currentToken = getCurrentNumberToken();
            if (currentToken.includes(".")) {
                return;
            }
            if (!calculatorState.expression || isOperator(lastCharacter) || lastCharacter === "(") {
                calculatorState.expression += "0";
            }
            calculatorState.expression += value;
            renderCalculator();
            return;
        }

        if (isOperator(value)) {
            if (!calculatorState.expression) {
                if (value === "-") {
                    calculatorState.expression = value;
                    renderCalculator();
                }
                return;
            }

            if (isOperator(lastCharacter)) {
                if (value === "-" && lastCharacter !== "-") {
                    calculatorState.expression += value;
                } else {
                    calculatorState.expression = `${calculatorState.expression.slice(0, -1)}${value}`;
                }
                renderCalculator();
                return;
            }

            if (lastCharacter === "(") {
                if (value === "-") {
                    calculatorState.expression += value;
                    renderCalculator();
                }
                return;
            }

            calculatorState.expression += value;
            renderCalculator();
            return;
        }

        if (/[0-9]/.test(value)) {
            if (calculatorState.expression === "0") {
                calculatorState.expression = value;
            } else {
                calculatorState.expression += value;
            }
            renderCalculator();
        }
    }

    function deleteCalculatorValue() {
        if (calculatorState.hasError) {
            clearCalculator();
            return;
        }

        if (calculatorState.justEvaluated) {
            calculatorState.justEvaluated = false;
            calculatorState.history = "0";
        }

        if (!calculatorState.expression) {
            renderCalculator();
            return;
        }

        calculatorState.expression = calculatorState.expression.slice(0, -1);
        renderCalculator();
    }

    function evaluateCalculator() {
        if (calculatorState.hasError || !calculatorState.expression) {
            return;
        }

        let expression = calculatorState.expression.trim();
        const lastCharacter = expression.slice(-1);

        if (!expression || isOperator(lastCharacter) || lastCharacter === "(" || lastCharacter === "." || expression === "-") {
            showCalculatorError();
            return;
        }

        const openCount = countOccurrences(expression, /\(/g);
        const closeCount = countOccurrences(expression, /\)/g);
        if (openCount > closeCount) {
            expression += ")".repeat(openCount - closeCount);
        }

        const evaluation = safeEvaluate(expression);
        if (!evaluation.ok) {
            showCalculatorError();
            return;
        }

        calculatorState.expression = String(evaluation.value);
        calculatorState.history = `${prettifyExpression(expression)} =`;
        calculatorState.display = formatCalculatorValue(evaluation.value);
        calculatorState.lastResult = evaluation.value;
        calculatorState.justEvaluated = true;
        calculatorState.hasError = false;
        renderCalculator();
    }

    function calculateCompound() {
        const initialCapital = parseNumber(document.getElementById("compound-capital")?.value);
        const periodicReturn = parseNumber(document.getElementById("compound-return")?.value) / 100;
        const periods = Math.max(0, Math.round(parseNumber(document.getElementById("compound-periods")?.value)));
        let capital = initialCapital;
        const rows = [];

        for (let period = 1; period <= periods; period += 1) {
            const capitalStart = capital;
            const gain = capitalStart * periodicReturn;
            capital = capitalStart + gain;
            rows.push({
                period,
                capitalStart,
                gain,
                capitalEnd: capital,
            });
        }

        const compoundProfit = capital - initialCapital;
        const compoundGrowth = initialCapital > 0 ? (compoundProfit / initialCapital) * 100 : 0;
        const breakdownTarget = document.getElementById("compound-breakdown");

        setText("compound-final", formatCurrency(capital));
        setText("compound-profit", formatSignedCurrency(compoundProfit));
        setText("compound-growth", formatPercent(compoundGrowth));

        if (breakdownTarget) {
            breakdownTarget.innerHTML = rows.map((row) => `
                <tr>
                    <td>${row.period}</td>
                    <td>${formatCurrency(row.capitalStart)}</td>
                    <td>${formatSignedCurrency(row.gain)}</td>
                    <td>${formatCurrency(row.capitalEnd)}</td>
                </tr>
            `).join("");

            if (!rows.length) {
                breakdownTarget.innerHTML = `
                    <tr>
                        <td>--</td>
                        <td>${formatCurrency(initialCapital)}</td>
                        <td>${formatCurrency(0)}</td>
                        <td>${formatCurrency(initialCapital)}</td>
                    </tr>
                `;
            }
        }
    }

    function calculateRiskPerTrade() {
        const capital = Math.max(0, parseNumber(document.getElementById("risk-trade-capital")?.value));
        const riskPercent = defaultRiskPercent;
        const riskAmount = capital * (riskPercent / 100);

        setText("risk-trade-badge", formatPercent(riskPercent));
        setText("risk-trade-amount", formatCurrency(riskAmount));
        setText(
            "risk-trade-note",
            strings.riskTradeNote
                .replace("{percent}", formatPercent(riskPercent))
                .replace("{value}", formatCurrency(riskAmount)),
        );
    }

    function calculatePositionSize() {
        const capital = parseNumber(document.getElementById("position-capital")?.value);
        const riskPercent = parseNumber(document.getElementById("position-risk")?.value);
        const stopPips = parseNumber(document.getElementById("position-stop")?.value);
        const pipValuePerLot = parseNumber(document.getElementById("position-pip-value")?.value);
        const contractSize = parseNumber(document.getElementById("position-contract")?.value, 100000);
        const riskAmount = capital * (riskPercent / 100);
        const lots = stopPips > 0 && pipValuePerLot > 0 ? riskAmount / (stopPips * pipValuePerLot) : 0;

        setText("position-risk-amount", formatCurrency(riskAmount));
        setText("position-lots", `${formatNumber(lots, 2)} lot(s)`);
        setText("position-units", formatNumber(lots * contractSize, 0));
    }

    function calculateSLTP() {
        const direction = document.getElementById("sltp-direction")?.value || "LONG";
        const entry = parseNumber(document.getElementById("sltp-entry")?.value);
        const stopPips = parseNumber(document.getElementById("sltp-stop-pips")?.value);
        const rr = parseNumber(document.getElementById("sltp-rr")?.value);
        const pipSize = parseNumber(document.getElementById("sltp-pip-size")?.value, 0.0001);
        const signed = direction === "LONG" ? 1 : -1;

        setText("sltp-stop-price", formatNumber(entry - (signed * stopPips * pipSize), 5));
        setText("sltp-target-price", formatNumber(entry + (signed * stopPips * rr * pipSize), 5));
        setText("sltp-target-pips", formatNumber(stopPips * rr, 1));
    }

    function calculateProfitLoss() {
        const direction = document.getElementById("pl-direction")?.value || "LONG";
        const entry = parseNumber(document.getElementById("pl-entry")?.value);
        const exit = parseNumber(document.getElementById("pl-exit")?.value);
        const lots = parseNumber(document.getElementById("pl-lots")?.value);
        const contractSize = parseNumber(document.getElementById("pl-contract")?.value, 100000);
        const pipSize = parseNumber(document.getElementById("pl-pip-size")?.value, 0.0001);
        const fees = parseNumber(document.getElementById("pl-fees")?.value);
        const signedDelta = (exit - entry) * (direction === "LONG" ? 1 : -1);
        const gross = signedDelta * lots * contractSize;

        setText("pl-pips", formatSignedNumber(pipSize > 0 ? signedDelta / pipSize : 0, 1));
        setText("pl-gross", formatSignedCurrency(gross));
        setText("pl-net", formatSignedCurrency(gross - fees));
    }

    function calculateMargin() {
        const capital = parseNumber(document.getElementById("margin-capital")?.value);
        const price = parseNumber(document.getElementById("margin-price")?.value);
        const lots = parseNumber(document.getElementById("margin-lots")?.value);
        const contractSize = parseNumber(document.getElementById("margin-contract")?.value, 100000);
        const leverage = parseNumber(document.getElementById("margin-leverage")?.value);
        const notional = lots * contractSize * price;
        const required = leverage > 0 ? notional / leverage : 0;

        setText("margin-notional", formatCurrency(notional));
        setText("margin-required", formatCurrency(required));
        setText("margin-free", formatSignedCurrency(capital - required));
        setText(
            "margin-ratio-note",
            strings.marginUsed.replace("{value}", formatPercent(capital > 0 ? (required / capital) * 100 : 0)),
        );
    }

    function calculatePipValue() {
        const lots = parseNumber(document.getElementById("pip-lots")?.value);
        const contractSize = parseNumber(document.getElementById("pip-contract")?.value, 100000);
        const pipSize = parseNumber(document.getElementById("pip-size")?.value, 0.0001);
        const conversion = parseNumber(document.getElementById("pip-conversion")?.value, 1);
        const quoteValue = lots * contractSize * pipSize;
        const accountValue = quoteValue * conversion;

        setText("pip-quote-value", formatNumber(quoteValue, 4));
        setText("pip-account-value", formatCurrency(accountValue));
        setText("pip-ten-value", formatCurrency(accountValue * 10));
    }

    function renderLevels(containerId, levels) {
        const container = document.getElementById(containerId);
        if (!(container instanceof HTMLElement)) {
            return;
        }

        container.innerHTML = levels.map((level) => `
            <div class="tool-level-row">
                <span>${level.label}</span>
                <strong>${formatNumber(level.value, 5)}</strong>
            </div>
        `).join("");
    }

    function calculateFibonacci() {
        const direction = document.getElementById("fibo-direction")?.value || "bullish";
        const high = parseNumber(document.getElementById("fibo-high")?.value);
        const low = parseNumber(document.getElementById("fibo-low")?.value);
        const top = Math.max(high, low);
        const bottom = Math.min(high, low);
        const range = top - bottom;

        renderLevels("fibo-retracements", [0.236, 0.382, 0.5, 0.618, 0.786].map((ratio) => ({
            label: `${ratio * 100}%`,
            value: direction === "bullish" ? top - (range * ratio) : bottom + (range * ratio),
        })));
        renderLevels("fibo-extensions", [1.272, 1.618, 2].map((ratio) => ({
            label: `${ratio * 100}%`,
            value: direction === "bullish" ? top + (range * (ratio - 1)) : bottom - (range * (ratio - 1)),
        })));
    }

    function calculatePivots() {
        const high = parseNumber(document.getElementById("pivot-high")?.value);
        const low = parseNumber(document.getElementById("pivot-low")?.value);
        const close = parseNumber(document.getElementById("pivot-close")?.value);
        const pp = (high + low + close) / 3;
        const rows = [
            { name: "R3", value: high + (2 * (pp - low)), kind: "Resistance" },
            { name: "R2", value: pp + (high - low), kind: "Resistance" },
            { name: "R1", value: (2 * pp) - low, kind: "Resistance" },
            { name: "PP", value: pp, kind: "Pivot" },
            { name: "S1", value: (2 * pp) - high, kind: "Support" },
            { name: "S2", value: pp - (high - low), kind: "Support" },
            { name: "S3", value: low - (2 * (high - pp)), kind: "Support" },
        ];
        const target = document.getElementById("pivot-levels");

        if (target) {
            target.innerHTML = rows.map((row) => `
                <tr>
                    <td>${row.name}</td>
                    <td>${formatNumber(row.value, 5)}</td>
                    <td>${row.kind}</td>
                </tr>
            `).join("");
        }
    }

    function calculateDrawdown() {
        const peak = parseNumber(document.getElementById("drawdown-peak")?.value);
        const current = parseNumber(document.getElementById("drawdown-current")?.value);
        const amount = peak - current;

        setText("drawdown-amount", formatCurrency(amount));
        setText("drawdown-percent", formatPercent(peak > 0 ? (amount / peak) * 100 : 0));
        setText("drawdown-recovery", formatPercent(current > 0 ? (amount / current) * 100 : 0));
    }

    function calculateRiskOfRuin() {
        const winRate = parseNumber(document.getElementById("ruin-win-rate")?.value) / 100;
        const avgWin = parseNumber(document.getElementById("ruin-avg-win")?.value);
        const avgLoss = parseNumber(document.getElementById("ruin-avg-loss")?.value, 1);
        const riskPerTrade = parseNumber(document.getElementById("ruin-risk-trade")?.value);
        const maxDrawdown = parseNumber(document.getElementById("ruin-max-dd")?.value);
        const lossRate = 1 - winRate;
        const expectancy = (winRate * avgWin) - (lossRate * avgLoss);
        const capitalUnits = riskPerTrade > 0 ? maxDrawdown / riskPerTrade : 0;
        const rewardFactor = avgLoss > 0 ? avgWin / avgLoss : 0;
        let ruinProbability = 1;

        if (winRate > 0 && rewardFactor > 0 && (winRate * rewardFactor) > lossRate && capitalUnits > 0) {
            ruinProbability = Math.pow(lossRate / (winRate * rewardFactor), capitalUnits);
        }
        if (expectancy <= 0 || !Number.isFinite(ruinProbability)) {
            ruinProbability = 1;
        }

        setText("ruin-expectancy", `${formatSignedNumber(expectancy, 2)}R`);
        setText("ruin-capital-units", formatNumber(capitalUnits, 1));
        setText("ruin-risk", formatPercent(Math.max(0, Math.min(ruinProbability * 100, 100))));
        setText(
            "ruin-note",
            expectancy > 0
                ? strings.ruinNotePositive
                : strings.ruinNoteNegative
        );
    }

    function recomputeAll() {
        calculateRiskPerTrade();
        calculateCompound();
        calculatePositionSize();
        calculateSLTP();
        calculateProfitLoss();
        calculateMargin();
        calculatePipValue();
        calculateFibonacci();
        calculatePivots();
        calculateDrawdown();
        calculateRiskOfRuin();
    }

    app.addEventListener("click", (event) => {
        const toolTrigger = event.target.closest("[data-tool-open]");
        if (toolTrigger instanceof HTMLElement) {
            setActiveTool(toolTrigger.dataset.toolOpen || "calculator", {
                title: toolTrigger.dataset.toolTitle,
                copy: toolTrigger.dataset.toolCopy,
            });
        }

        const calculatorButton = event.target.closest("[data-calculator-value], [data-calculator-action]");
        if (!(calculatorButton instanceof HTMLElement)) {
            return;
        }

        event.preventDefault();

        const calculatorValue = calculatorButton.dataset.calculatorValue;
        const calculatorAction = calculatorButton.dataset.calculatorAction;

        if (calculatorAction === "clear") {
            clearCalculator();
            return;
        }

        if (calculatorAction === "delete") {
            deleteCalculatorValue();
            return;
        }

        if (calculatorAction === "evaluate") {
            evaluateCalculator();
            return;
        }

        appendCalculatorValue(calculatorValue || "");
    });

    document.addEventListener("keydown", (event) => {
        if (!(toolsModal instanceof HTMLElement) || toolsModal.hidden || activeTool !== "calculator") {
            return;
        }

        if (event.altKey || event.ctrlKey || event.metaKey) {
            return;
        }

        const focusedElement = document.activeElement;
        if (
            focusedElement instanceof HTMLElement &&
            (focusedElement.matches("input, select, textarea") || focusedElement.isContentEditable)
        ) {
            return;
        }

        if (/^[0-9]$/.test(event.key) || ["+", "-", "*", "/", "(", ")", "."].includes(event.key)) {
            event.preventDefault();
            appendCalculatorValue(event.key);
            return;
        }

        if (event.key === "Enter" || event.key === "=") {
            event.preventDefault();
            evaluateCalculator();
            return;
        }

        if (event.key === "Backspace" || event.key === "Delete") {
            event.preventDefault();
            deleteCalculatorValue();
            return;
        }

        if (event.key.toLowerCase() === "c") {
            event.preventDefault();
            clearCalculator();
        }
    });

    app.addEventListener("input", recomputeAll);
    app.addEventListener("change", recomputeAll);

    setActiveTool("risk-trade");
    clearCalculator();
    recomputeAll();
}());

(function () {
    const defaultLocale = document.body?.dataset.uiLocale || "fr-FR";
    const currencySymbols = {
        USD: "$",
        EUR: "\u20AC",
        GBP: "\u00A3",
        CHF: "CHF ",
        XAF: "FCFA ",
        XOF: "CFA ",
    };

    function formatFixedNumber(value, { locale = defaultLocale, digits = 2, useGrouping = true } = {}) {
        return new Intl.NumberFormat(locale, {
            useGrouping,
            minimumFractionDigits: digits,
            maximumFractionDigits: digits,
        }).format(value);
    }

    function trimZeroDecimalsOnly(value) {
        return String(value ?? "").replace(/([.,])00$/, "");
    }

    function trimTrailingFractionZeros(value) {
        return String(value ?? "")
            .replace(/([.,]\d*?[1-9])0+$/, "$1")
            .replace(/([.,])0+$/, "");
    }

    function getCurrencySymbol(currency = "USD") {
        return currencySymbols[currency] || `${currency} `;
    }

    function formatCompactAmount(value, { locale = defaultLocale, digits = 2, threshold = 1000 } = {}) {
        const numericValue = Number.parseFloat(value);
        if (!Number.isFinite(numericValue)) {
            return "--";
        }

        const absoluteValue = Math.abs(numericValue);
        if (absoluteValue >= threshold) {
            return `${trimTrailingFractionZeros(formatFixedNumber(absoluteValue / threshold, {
                locale,
                digits,
                useGrouping: false,
            }))}k`;
        }

        return trimZeroDecimalsOnly(formatFixedNumber(absoluteValue, {
            locale,
            digits,
            useGrouping: true,
        }));
    }

    function formatCurrency(value, { currency = "USD", locale = defaultLocale, digits = 2 } = {}) {
        const numericValue = Number.parseFloat(value);
        if (!Number.isFinite(numericValue)) {
            return `${getCurrencySymbol(currency)}0`;
        }

        const sign = numericValue < 0 ? "-" : "";
        return `${sign}${getCurrencySymbol(currency)}${formatCompactAmount(Math.abs(numericValue), {
            locale,
            digits,
        })}`;
    }

    window.AkiliCurrency = {
        formatCompactAmount,
        formatCurrency,
        getCurrencySymbol,
    };
})();

(function () {
    const langCode = (document.documentElement.lang || "fr").toLowerCase();
    const strings = langCode.startsWith("fr") ? {
        installTitle: "Installer ZEN TRADING",
        installCopy: "Ajoutez l'application a votre ecran d'accueil pour y acceder plus vite, meme avec une connexion instable.",
        iosCopy: "Sur iPhone, utilisez le bouton Partager puis Ajouter a l'ecran d'accueil.",
        unavailableCopy: "Si rien ne s'ouvre, utilisez le menu du navigateur puis Installer l'application ou Ajouter a l'ecran d'accueil.",
        install: "Installer l'application",
        installing: "Ouverture...",
        later: "Plus tard",
        close: "Fermer le bandeau d'installation",
    } : {
        installTitle: "Install ZEN TRADING",
        installCopy: "Add the app to your home screen for faster access, even with an unstable connection.",
        iosCopy: "On iPhone, use Share, then Add to Home Screen.",
        unavailableCopy: "If nothing opens, use the browser menu, then Install app or Add to Home Screen.",
        install: "Install app",
        installing: "Opening...",
        later: "Later",
        close: "Close install banner",
    };

    const DISMISS_KEY = "zenTradingInstallDismissedAt";
    const DISMISS_TTL = 7 * 24 * 60 * 60 * 1000;
    let deferredPrompt = null;
    let banner = null;

    function isStandalone() {
        return window.matchMedia("(display-mode: standalone)").matches
            || window.navigator.standalone === true;
    }

    function recentlyDismissed() {
        const dismissedAt = Number(window.localStorage.getItem(DISMISS_KEY) || 0);
        return dismissedAt && Date.now() - dismissedAt < DISMISS_TTL;
    }

    function dismissBanner() {
        window.localStorage.setItem(DISMISS_KEY, String(Date.now()));
        if (banner) {
            banner.remove();
            banner = null;
        }
    }

    function createBanner({ ios = false } = {}) {
        if (banner || isStandalone() || recentlyDismissed()) {
            return;
        }

        banner = document.createElement("section");
        banner.className = "pwa-install-banner";
        banner.setAttribute("aria-label", strings.installTitle);
        banner.innerHTML = `
            <div class="pwa-install-banner__icon" aria-hidden="true">
                <img src="/static/app/favicon.png" alt="">
            </div>
            <div class="pwa-install-banner__content">
                <strong>${strings.installTitle}</strong>
                <p>${ios ? strings.iosCopy : strings.installCopy}</p>
            </div>
            <div class="pwa-install-banner__actions">
                ${ios ? "" : `<button class="pwa-install-banner__install" type="button" data-pwa-install-button>${strings.install}</button>`}
                <button class="pwa-install-banner__dismiss" type="button" aria-label="${strings.close}">${strings.later}</button>
            </div>
        `;

        document.body.appendChild(banner);
        window.setTimeout(() => banner?.classList.add("is-visible"), 30);

        banner.querySelector(".pwa-install-banner__dismiss")?.addEventListener("click", dismissBanner);
        banner.querySelector("[data-pwa-install-button]")?.addEventListener("click", async (event) => {
            if (!deferredPrompt) {
                const copy = banner?.querySelector(".pwa-install-banner__content p");
                if (copy) {
                    copy.textContent = strings.unavailableCopy;
                }
                return;
            }

            const installButton = event.currentTarget;
            installButton.disabled = true;
            installButton.textContent = strings.installing;
            deferredPrompt.prompt();
            await deferredPrompt.userChoice;
            deferredPrompt = null;
            dismissBanner();
        });
    }

    function shouldShowInstallBannerOnLoad() {
        return window.location.pathname === "/gestion/connexion/";
    }

    function isIosInstallCandidate() {
        const platform = window.navigator.platform || "";
        const userAgent = window.navigator.userAgent || "";
        const isIos = /iPad|iPhone|iPod/.test(platform)
            || (platform === "MacIntel" && window.navigator.maxTouchPoints > 1);
        return isIos && /Safari/.test(userAgent) && !/CriOS|FxiOS|EdgiOS/.test(userAgent);
    }

    window.addEventListener("beforeinstallprompt", (event) => {
        event.preventDefault();
        deferredPrompt = event;
        createBanner();
    });

    window.addEventListener("appinstalled", () => {
        deferredPrompt = null;
        dismissBanner();
    });

    document.addEventListener("DOMContentLoaded", () => {
        if (isIosInstallCandidate()) {
            window.setTimeout(() => createBanner({ ios: true }), 900);
            return;
        }

        if (shouldShowInstallBannerOnLoad()) {
            window.setTimeout(() => createBanner(), 900);
        }
    }, { once: true });
})();

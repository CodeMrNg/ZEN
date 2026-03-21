from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseServerError
from django.template.loader import render_to_string
from django.urls import reverse

from .localization import get_language_direction, get_language_locale, normalize_language


ERROR_PAGE_CONTENT = {
    "fr": {
        "brand_subtitle": "Plateforme de performance",
        "brand_note": "ZEN TRADING centralise votre journal, votre capital et vos outils de pilotage dans un espace de suivi professionnel.",
        "actions_eyebrow": "Actions rapides",
        "support_badge": "Recuperation",
        "action_dashboard": "Retour au dashboard",
        "action_signin": "Retour a la connexion",
        "action_settings": "Ouvrir les parametres",
        "action_register": "Creer un compte",
        "action_reload": "Recharger la page",
        "status_label": "Statut",
        "statuses": {
            404: {
                "eyebrow": "Erreur 404",
                "title": "Page introuvable",
                "copy": "Le lien demande n existe pas ou a ete deplace. Revenez vers une page stable depuis les actions proposees.",
                "panel_title": "Reprendre la navigation",
                "panel_copy": "Choisissez une destination stable puis verifiez l adresse demandee si le probleme revient.",
                "hero_cards": [
                    {"label": "Statut", "value": "404", "copy": "Ressource absente ou URL invalide."},
                    {"label": "Navigation", "value": "Retour rapide", "copy": "Utilisez les liens proposes pour reprendre la navigation."},
                    {"label": "Controle", "value": "Verifier l URL", "copy": "Un favori obsolete ou un lien incomplet provoque souvent cette erreur."},
                ],
                "guidance_items": [
                    {"title": "Verifier le lien", "copy": "Controlez l URL saisie ou le bouton utilise pour atteindre cette page."},
                    {"title": "Revenir a un ecran stable", "copy": "Le dashboard, les parametres ou la connexion restent les points de reprise les plus fiables."},
                    {"title": "Mettre a jour vos raccourcis", "copy": "Si vous ouvrez cette page depuis un favori, remplacez-le par le lien actuel."},
                ],
            },
            500: {
                "eyebrow": "Erreur 500",
                "title": "Incident serveur temporaire",
                "copy": "Une erreur interne a interrompu cette page. Rechargez-la dans un instant ou revenez vers un ecran stable.",
                "panel_title": "Stabiliser la session",
                "panel_copy": "Revenez vers une page fiable, puis rechargez cette vue uniquement si le probleme etait temporaire.",
                "hero_cards": [
                    {"label": "Statut", "value": "500", "copy": "Erreur interne detectee pendant le traitement de la requete."},
                    {"label": "Action", "value": "Reessayer", "copy": "Une simple recharge suffit souvent apres un incident ponctuel."},
                    {"label": "Continuer", "value": "Retour stable", "copy": "Le dashboard ou la connexion restent les points de reprise les plus fiables."},
                ],
                "guidance_items": [
                    {"title": "Recharger apres quelques secondes", "copy": "Le probleme peut venir d un traitement temporairement indisponible."},
                    {"title": "Revenir vers une page stable", "copy": "Utilisez le dashboard, les parametres ou la connexion pour reprendre votre session."},
                    {"title": "Verifier les journaux si besoin", "copy": "Si l erreur persiste en local ou en production, consultez les logs du serveur."},
                ],
            },
        },
    },
    "en": {
        "brand_subtitle": "Performance platform",
        "brand_note": "ZEN TRADING centralizes your journal, capital, and decision tools in one professional trading workspace.",
        "actions_eyebrow": "Quick actions",
        "support_badge": "Recovery",
        "action_dashboard": "Back to dashboard",
        "action_signin": "Back to sign in",
        "action_settings": "Open settings",
        "action_register": "Create account",
        "action_reload": "Reload page",
        "status_label": "Status",
        "statuses": {
            404: {
                "eyebrow": "Error 404",
                "title": "Page not found",
                "copy": "The requested link does not exist or has moved. Return to a stable screen using the actions below.",
                "panel_title": "Resume navigation",
                "panel_copy": "Choose a stable destination, then verify the requested address if the issue happens again.",
                "hero_cards": [
                    {"label": "Status", "value": "404", "copy": "Missing resource or invalid URL."},
                    {"label": "Navigation", "value": "Quick return", "copy": "Use the suggested links to resume navigation."},
                    {"label": "Check", "value": "Review the URL", "copy": "An outdated bookmark or incomplete link often causes this error."},
                ],
                "guidance_items": [
                    {"title": "Check the link", "copy": "Review the typed URL or the button used to reach this page."},
                    {"title": "Return to a stable screen", "copy": "The dashboard, settings, or sign-in page remain the safest recovery points."},
                    {"title": "Update saved shortcuts", "copy": "If this page comes from a bookmark, replace it with the current link."},
                ],
            },
            500: {
                "eyebrow": "Error 500",
                "title": "Temporary server issue",
                "copy": "An internal error interrupted this page. Reload it in a moment or return to a stable screen.",
                "panel_title": "Stabilize the session",
                "panel_copy": "Return to a reliable page, then reload this view only if the problem was temporary.",
                "hero_cards": [
                    {"label": "Status", "value": "500", "copy": "An internal error occurred while processing the request."},
                    {"label": "Action", "value": "Retry", "copy": "A simple reload is often enough after a short incident."},
                    {"label": "Continue", "value": "Stable return", "copy": "The dashboard or sign-in page remain the safest recovery points."},
                ],
                "guidance_items": [
                    {"title": "Reload after a few seconds", "copy": "The issue may come from a temporarily unavailable process."},
                    {"title": "Return to a stable page", "copy": "Use the dashboard, settings, or sign-in page to continue your session."},
                    {"title": "Check logs if needed", "copy": "If the error persists locally or in production, inspect the server logs."},
                ],
            },
        },
    },
}


def _resolve_language(request):
    return normalize_language(
        getattr(request, "LANGUAGE_CODE", None)
        or request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
    )


def _build_common_context(request, language, payload):
    user = getattr(request, "user", None)
    is_authenticated = bool(getattr(user, "is_authenticated", False))

    return {
        "app_language": language,
        "app_language_locale": get_language_locale(language),
        "app_language_direction": get_language_direction(language),
        "brand_subtitle": payload["brand_subtitle"],
        "brand_note": payload["brand_note"],
        "actions_eyebrow": payload["actions_eyebrow"],
        "support_badge": payload["support_badge"],
        "primary_url": reverse("app:dashboard") if is_authenticated else reverse("app:login"),
        "primary_label": payload["action_dashboard"] if is_authenticated else payload["action_signin"],
    }


def _render_error_page(request, status_code, *, secondary_type="link", secondary_url="", secondary_label=""):
    language = _resolve_language(request)
    payload = ERROR_PAGE_CONTENT.get(language, ERROR_PAGE_CONTENT["fr"])
    page = payload["statuses"][status_code]
    context = {
        **_build_common_context(request, language, payload),
        "page_title": page["title"],
        "meta_description": page["copy"],
        "eyebrow": page["eyebrow"],
        "headline": page["title"],
        "copy": page["copy"],
        "status_code": status_code,
        "status_label": payload["status_label"],
        "hero_cards": page["hero_cards"],
        "panel_title": page["panel_title"],
        "panel_copy": page["panel_copy"],
        "guidance_items": page["guidance_items"],
        "secondary_type": secondary_type,
        "secondary_url": secondary_url,
        "secondary_label": secondary_label,
    }
    html = render_to_string("error_page.html", context)
    if status_code == 404:
        return HttpResponseNotFound(html)
    return HttpResponseServerError(html)


def custom_page_not_found(request, exception):
    user = getattr(request, "user", None)
    is_authenticated = bool(getattr(user, "is_authenticated", False))
    language = _resolve_language(request)
    payload = ERROR_PAGE_CONTENT.get(language, ERROR_PAGE_CONTENT["fr"])
    secondary_url = reverse("app:settings") if is_authenticated else reverse("app:register")
    secondary_label = payload["action_settings"] if is_authenticated else payload["action_register"]
    return _render_error_page(
        request,
        404,
        secondary_type="link",
        secondary_url=secondary_url,
        secondary_label=secondary_label,
    )


def custom_server_error(request):
    language = _resolve_language(request)
    payload = ERROR_PAGE_CONTENT.get(language, ERROR_PAGE_CONTENT["fr"])
    return _render_error_page(
        request,
        500,
        secondary_type="reload",
        secondary_label=payload["action_reload"],
    )

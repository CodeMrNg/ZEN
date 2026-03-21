from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import CapitalMovement, ServerRefreshStatus, SocialLink, Trade, TradingAccount, TradingPreference


admin.site.site_header = "ZEN TRADING Admin"
admin.site.site_title = "ZEN TRADING"
admin.site.index_title = "Administration"
admin.site.empty_value_display = "--"


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    date_hierarchy = "executed_at"
    ordering = ("-executed_at", "-created_at")
    list_per_page = 50
    list_select_related = ("user", "account")
    autocomplete_fields = ("user", "account")
    search_fields = ("symbol", "setup", "notes", "user__username", "user__email", "account__name", "account__broker")
    list_filter = ("account", "direction", "result", "setup", "market", "executed_at")
    readonly_fields = (
        "display_gross_pnl",
        "display_net_pnl",
        "display_resolved_result",
        "screenshot_preview",
        "created_at",
        "updated_at",
    )
    list_display = (
        "executed_at",
        "user",
        "account",
        "symbol",
        "direction",
        "display_resolved_result",
        "setup",
        "display_net_pnl",
        "display_capital_base",
        "confidence",
    )
    fieldsets = (
        (
            "Execution",
            {
                "fields": (
                    "user",
                    "account",
                    "executed_at",
                    "symbol",
                    "market",
                    "direction",
                    "result",
                    "setup",
                    "confidence",
                )
            },
        ),
        (
            "Ratios et capital",
            {
                "fields": (
                    "rr_ratio",
                    "gp_value",
                    "fees",
                    "risk_amount",
                    "risk_percent",
                    "capital_base",
                    "lot_size",
                    "quantity",
                )
            },
        ),
        (
            "Prix",
            {
                "fields": (
                    "entry_price",
                    "exit_price",
                )
            },
        ),
        (
            "Capture et notes",
            {
                "fields": (
                    "screenshot",
                    "screenshot_preview",
                    "notes",
                )
            },
        ),
        (
            "Calculs",
            {
                "fields": (
                    "display_resolved_result",
                    "display_gross_pnl",
                    "display_net_pnl",
                )
            },
        ),
        (
            "Meta",
            {
                "classes": ("collapse",),
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    @admin.display(description="Resultat")
    def display_resolved_result(self, obj):
        return obj.resolved_result_label

    @admin.display(description="P&L brut")
    def display_gross_pnl(self, obj):
        return f"{obj.gross_pnl:,.2f}"

    @admin.display(description="P&L net")
    def display_net_pnl(self, obj):
        return f"{obj.net_pnl:,.2f}"

    @admin.display(description="Capital ref.")
    def display_capital_base(self, obj):
        return f"{obj.capital_base:,.2f}"

    @admin.display(description="Capture")
    def screenshot_preview(self, obj):
        if not obj.screenshot:
            return "Aucune image"
        return format_html(
            '<a href="{url}" target="_blank" rel="noopener noreferrer">'
            '<img src="{url}" alt="Capture trade" style="max-width: 240px; border-radius: 12px; border: 1px solid #2b3446;" />'
            "</a>",
            url=obj.screenshot.url,
        )


@admin.register(TradingPreference)
class TradingPreferenceAdmin(admin.ModelAdmin):
    ordering = ("user__username",)
    list_per_page = 50
    list_select_related = ("user", "active_account")
    autocomplete_fields = ("user", "active_account")
    search_fields = ("user__username", "user__email", "default_symbol", "default_setup")
    readonly_fields = ("created_at", "updated_at", "currency_symbol")
    list_display = (
        "user",
        "active_account",
        "default_symbol",
        "default_direction",
        "default_setup",
        "capital_base",
        "currency",
        "updated_at",
    )
    list_filter = ("default_direction", "currency", "updated_at")
    fieldsets = (
        (
            "Compte",
            {
                "fields": (
                    "user",
                    "active_account",
                    "currency",
                    "currency_symbol",
                    "capital_base",
                )
            },
        ),
        (
            "Valeurs par defaut",
            {
                "fields": (
                    "default_symbol",
                    "default_direction",
                    "default_setup",
                    "default_lot_size",
                    "default_fees",
                    "default_confidence",
                    "default_risk_percent",
                )
            },
        ),
        (
            "Meta",
            {
                "classes": ("collapse",),
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


@admin.register(TradingAccount)
class TradingAccountAdmin(admin.ModelAdmin):
    ordering = ("user__username", "created_at")
    list_per_page = 50
    list_select_related = ("user",)
    autocomplete_fields = ("user",)
    search_fields = ("user__username", "user__email", "name", "broker", "account_identifier")
    list_filter = ("currency", "archived_at", "created_at")
    readonly_fields = ("currency_symbol", "created_at", "updated_at")
    list_display = (
        "name",
        "user",
        "broker",
        "account_identifier",
        "capital_base",
        "currency",
        "archived_at",
        "updated_at",
    )
    fieldsets = (
        (
            "Compte de trading",
            {
                "fields": (
                    "user",
                    "name",
                    "broker",
                    "account_identifier",
                    "capital_base",
                    "currency",
                    "archived_at",
                    "currency_symbol",
                )
            },
        ),
        (
            "Meta",
            {
                "classes": ("collapse",),
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


@admin.register(CapitalMovement)
class CapitalMovementAdmin(admin.ModelAdmin):
    date_hierarchy = "occurred_at"
    ordering = ("-occurred_at", "-created_at")
    list_per_page = 50
    list_select_related = ("user", "account")
    autocomplete_fields = ("user", "account")
    search_fields = ("user__username", "user__email", "note", "account__name", "account__broker")
    list_filter = ("account", "kind", "occurred_at")
    readonly_fields = ("created_at", "updated_at")
    list_display = (
        "occurred_at",
        "user",
        "account",
        "kind",
        "amount",
        "note",
    )
    fieldsets = (
        (
            "Mouvement",
            {
                "fields": (
                    "user",
                    "account",
                    "kind",
                    "amount",
                    "occurred_at",
                    "note",
                )
            },
        ),
        (
            "Meta",
            {
                "classes": ("collapse",),
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


@admin.register(ServerRefreshStatus)
class ServerRefreshStatusAdmin(admin.ModelAdmin):
    list_display = (
        "display_tracking_status",
        "last_refreshed_at",
        "display_next_refresh_due_at",
        "display_is_overdue",
        "updated_at",
    )
    readonly_fields = (
        "display_tracking_status",
        "display_next_refresh_due_at",
        "display_is_overdue",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "Suivi mensuel",
            {
                "fields": (
                    "is_enabled",
                    "last_refreshed_at",
                    "display_tracking_status",
                    "display_next_refresh_due_at",
                    "display_is_overdue",
                )
            },
        ),
        (
            "Meta",
            {
                "classes": ("collapse",),
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    def has_add_permission(self, request):
        return not ServerRefreshStatus.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        if ServerRefreshStatus.objects.exists():
            status = ServerRefreshStatus.objects.first()
            return redirect(reverse("admin:app_serverrefreshstatus_change", args=[status.pk]))
        return super().changelist_view(request, extra_context=extra_context)

    @admin.display(description="Statut")
    def display_tracking_status(self, obj):
        if not obj.is_enabled:
            return format_html(
                '<span style="display:inline-flex;align-items:center;padding:6px 10px;border-radius:999px;'
                'border:1px solid rgba(143,155,179,.24);background:rgba(143,155,179,.12);font-weight:700;">Desactive</span>'
            )
        if obj.is_overdue:
            return format_html(
                '<span style="display:inline-flex;align-items:center;padding:6px 10px;border-radius:999px;'
                'border:1px solid rgba(239,100,100,.24);background:rgba(239,100,100,.12);font-weight:700;color:#b42318;">En retard</span>'
            )
        return format_html(
            '<span style="display:inline-flex;align-items:center;padding:6px 10px;border-radius:999px;'
            'border:1px solid rgba(200,248,0,.28);background:rgba(200,248,0,.16);font-weight:700;">Suivi actif</span>'
        )

    @admin.display(description="Prochaine echeance")
    def display_next_refresh_due_at(self, obj):
        return timezone.localtime(obj.next_refresh_due_at).strftime("%d/%m/%Y %H:%M")

    @admin.display(boolean=True, description="En retard")
    def display_is_overdue(self, obj):
        return obj.is_overdue


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    ordering = ("sort_order", "pk")
    list_per_page = 20
    search_fields = ("label", "url", "platform")
    list_filter = ("platform", "is_active")
    list_editable = ("is_active", "sort_order")
    readonly_fields = ("icon_preview", "url_link", "created_at", "updated_at")
    list_display = (
        "icon_preview",
        "display_name",
        "platform",
        "url_link",
        "is_active",
        "sort_order",
        "updated_at",
    )
    fieldsets = (
        (
            "Diffusion globale",
            {
                "fields": (
                    "platform",
                    "label",
                    "url",
                    "sort_order",
                    "is_active",
                )
            },
        ),
        (
            "Apercu",
            {
                "fields": (
                    "icon_preview",
                    "url_link",
                )
            },
        ),
        (
            "Meta",
            {
                "classes": ("collapse",),
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    @admin.display(description="Nom")
    def display_name(self, obj):
        return obj.display_name

    @admin.display(description="Icone")
    def icon_preview(self, obj):
        if obj is None:
            return "Choisissez un reseau"

        badge = (obj.platform[:2] if obj.platform != SocialLink.Platform.LINKEDIN else "in").upper()
        if obj.platform == SocialLink.Platform.INSTAGRAM:
            badge = "IG"
        elif obj.platform == SocialLink.Platform.WHATSAPP:
            badge = "WA"
        elif obj.platform == SocialLink.Platform.TELEGRAM:
            badge = "TG"
        elif obj.platform == SocialLink.Platform.YOUTUBE:
            badge = "YT"
        elif obj.platform == SocialLink.Platform.GITHUB:
            badge = "GH"
        elif obj.platform == SocialLink.Platform.TIKTOK:
            badge = "TT"
        elif obj.platform == SocialLink.Platform.WEBSITE:
            badge = "WB"

        return format_html(
            '<span style="display:inline-flex;align-items:center;justify-content:center;min-width:38px;height:38px;padding:0 10px;border-radius:12px;border:1px solid rgba(200,248,0,.28);background:rgba(200,248,0,.16);font-weight:800;">{}</span>',
            badge,
        )

    @admin.display(description="Lien")
    def url_link(self, obj):
        if obj is None or not obj.url:
            return "Lien non renseigne"

        return format_html(
            '<a href="{url}" target="_blank" rel="noopener noreferrer">{url}</a>',
            url=obj.url,
        )

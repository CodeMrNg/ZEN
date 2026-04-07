from decimal import Decimal, InvalidOperation

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import translation
from django.utils.http import url_has_allowed_host_and_scheme
from django.urls import reverse_lazy
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import FormView

from .forms import (
    CapitalMovementForm,
    DeleteAccountForm,
    LoginForm,
    SignUpForm,
    TradeCreateForm,
    TradingAccountForm,
    TradingAccountEditForm,
    TradingPasswordChangeForm,
    TradingPreferenceForm,
)
from .models import TradingAccount
from .localization import normalize_language, translate
from .services import (
    archive_trading_account_for_user,
    build_server_refresh_snapshot,
    build_account_label,
    build_transactions_payload_for_user,
    build_dashboard_payload_for_user,
    create_capital_movement_for_user,
    create_trade_for_user,
    disable_server_refresh_tracking,
    enable_server_refresh_tracking,
    format_currency,
    format_signed_percent,
    get_or_create_active_account_for_user,
    get_current_capital_for_user,
    get_or_create_preferences_for_user,
    ensure_sqlite_decimal_storage_integrity,
    mark_server_refresh_updated,
    get_archived_trading_accounts_for_user,
    get_trading_accounts_for_user,
    restore_trading_account_for_user,
    switch_active_account_for_user,
    sync_preferences_with_account,
    seed_demo_trades_for_user,
    update_trade_for_user,
)


def apply_language_cookie(response, language):
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        language,
        max_age=getattr(settings, 'LANGUAGE_COOKIE_AGE', 31536000),
        samesite=getattr(settings, 'LANGUAGE_COOKIE_SAMESITE', 'Lax'),
        secure=getattr(settings, 'LANGUAGE_COOKIE_SECURE', False),
    )
    return response


def persist_request_language_for_user(request, user, language=None):
    language = normalize_language(
        language
        or getattr(request, 'LANGUAGE_CODE', None)
        or request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
    )

    if user and getattr(user, 'pk', None):
        preferences = get_or_create_preferences_for_user(user.pk)
        if preferences.ui_language != language:
            preferences.ui_language = language
            preferences.save(update_fields=['ui_language', 'updated_at'])

    return language


def get_saved_language_for_user(user, fallback=None):
    if not user or not getattr(user, 'pk', None):
        return normalize_language(fallback)

    preferences = get_or_create_preferences_for_user(user.pk)
    return normalize_language(preferences.ui_language or fallback)


def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('app:dashboard')
    return redirect('app:login')


@require_POST
def set_language_view(request):
    language = normalize_language(request.POST.get('language'))
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse_lazy('app:login')

    if not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = reverse_lazy('app:login')

    if request.user.is_authenticated:
        language = persist_request_language_for_user(request, request.user, language=language)

    translation.activate(language)
    request.LANGUAGE_CODE = language
    response = redirect(next_url)
    return apply_language_cookie(response, language)


class TradingLoginView(LoginView):
    template_name = 'app/auth.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['language'] = normalize_language(getattr(self.request, 'LANGUAGE_CODE', None))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mode'] = 'login'
        context['page_title'] = translate(
            'views.login.title',
            language=normalize_language(getattr(self.request, 'LANGUAGE_CODE', None)),
            default='Connexion',
        )
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        language = get_saved_language_for_user(
            form.get_user(),
            fallback=getattr(self.request, 'LANGUAGE_CODE', None),
        )
        translation.activate(language)
        self.request.LANGUAGE_CODE = language
        return apply_language_cookie(response, language)


class RegisterView(FormView):
    template_name = 'app/auth.html'
    form_class = SignUpForm
    success_url = reverse_lazy('app:dashboard')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        language = get_saved_language_for_user(user, fallback='fr')
        translation.activate(language)
        self.request.LANGUAGE_CODE = language
        response = super().form_valid(form)
        return apply_language_cookie(response, language)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['language'] = normalize_language(getattr(self.request, 'LANGUAGE_CODE', None))
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mode'] = 'register'
        context['page_title'] = translate(
            'views.register.title',
            language=normalize_language(getattr(self.request, 'LANGUAGE_CODE', None)),
            default='Inscription',
        )
        return context


@require_POST
def logout_view(request):
    logout(request)
    response = redirect('app:login')
    response.delete_cookie(settings.LANGUAGE_COOKIE_NAME)
    return response


@login_required
def _build_dashboard_view_context(request):
    preferences = get_or_create_preferences_for_user(request.user.pk)
    active_account = get_or_create_active_account_for_user(request.user.pk, preferences)
    return {
        'trade_preferences': preferences,
        'trade_current_capital': get_current_capital_for_user(request.user.pk, preferences, account=active_account),
        'active_account': active_account,
        'trading_accounts': get_trading_accounts_for_user(request.user.pk),
        'server_refresh': build_server_refresh_snapshot(language=getattr(request, 'LANGUAGE_CODE', None)) if request.user.is_superuser else None,
    }


@login_required
def dashboard_view(request):
    try:
        return render(request, 'app/dashboard.html', _build_dashboard_view_context(request))
    except InvalidOperation:
        # Retry once after a full SQLite decimal cleanup in case stale malformed rows
        # slipped past the targeted per-user repair path.
        ensure_sqlite_decimal_storage_integrity()
        return render(request, 'app/dashboard.html', _build_dashboard_view_context(request))


@login_required
def transactions_view(request):
    preferences = get_or_create_preferences_for_user(request.user.pk)
    active_account = get_or_create_active_account_for_user(request.user.pk, preferences)
    return render(
        request,
        'app/transactions.html',
        {
            'trade_preferences': preferences,
            'active_account': active_account,
            'trading_accounts': get_trading_accounts_for_user(request.user.pk),
        },
    )


@login_required
def tools_view(request):
    preferences = get_or_create_preferences_for_user(request.user.pk)
    active_account = get_or_create_active_account_for_user(request.user.pk, preferences)
    current_capital = get_current_capital_for_user(request.user.pk, preferences, account=active_account)
    risk_one_percent = current_capital * Decimal('0.01')
    risk_two_percent = current_capital * Decimal('0.02')
    return render(
        request,
        'app/tools.html',
        {
            'trade_preferences': preferences,
            'active_account': active_account,
            'trading_accounts': get_trading_accounts_for_user(request.user.pk),
            'current_capital': current_capital,
            'current_capital_formatted': format_currency(current_capital, active_account.currency),
            'risk_one_percent_formatted': format_currency(risk_one_percent, active_account.currency),
            'risk_two_percent_formatted': format_currency(risk_two_percent, active_account.currency),
            'initial_capital_formatted': format_currency(active_account.capital_base, active_account.currency),
        },
    )


@login_required
def settings_view(request):
    language = normalize_language(getattr(request, 'LANGUAGE_CODE', None))
    response_language = None
    preferences = get_or_create_preferences_for_user(request.user.pk)
    active_account = get_or_create_active_account_for_user(request.user.pk, preferences)
    server_refresh = build_server_refresh_snapshot(language=language) if request.user.is_superuser else None
    success_message = None
    error_message = None
    show_account_form_modal = False
    show_account_edit_modal = False
    preferences_form = TradingPreferenceForm(instance=preferences, language=language)
    account_form = TradingAccountForm(prefix='create-account', initial={'currency': active_account.currency}, language=language)
    edit_account_form = TradingAccountEditForm(
        instance=active_account,
        prefix='edit-account',
        initial={'set_active': True},
        language=language,
    )
    editing_account = active_account
    password_form = TradingPasswordChangeForm(request.user, language=language)
    delete_account_form = DeleteAccountForm(user=request.user, language=language)
    trading_accounts = get_trading_accounts_for_user(request.user.pk)
    archived_trading_accounts = get_archived_trading_accounts_for_user(request.user.pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'preferences':
            preferences_form = TradingPreferenceForm(request.POST, instance=preferences, language=language)
            if preferences_form.is_valid():
                selected_language = normalize_language(preferences_form.cleaned_data.get('ui_language'))
                preferences = preferences_form.save()
                active_account.name = active_account.name or 'Compte principal'
                active_account.capital_base = preferences_form.cleaned_data['capital_base']
                active_account.currency = preferences_form.cleaned_data['currency']
                active_account.save(update_fields=['capital_base', 'currency', 'updated_at'])
                preferences = sync_preferences_with_account(preferences, active_account)
                if selected_language != language:
                    language = selected_language
                    response_language = language
                    translation.activate(language)
                    request.LANGUAGE_CODE = language
                success_message = translate('views.success.configuration_saved', language=language, default='Configuration enregistree.')
                preferences_form = TradingPreferenceForm(instance=preferences, language=language)
                account_form = TradingAccountForm(prefix='create-account', initial={'currency': active_account.currency}, language=language)
                edit_account_form = TradingAccountEditForm(
                    instance=active_account,
                    prefix='edit-account',
                    initial={'set_active': True},
                    language=language,
                )
                editing_account = active_account
                password_form = TradingPasswordChangeForm(request.user, language=language)
                delete_account_form = DeleteAccountForm(user=request.user, language=language)
        elif action == 'create_account':
            account_form = TradingAccountForm(request.POST, prefix='create-account', language=language)
            if account_form.is_valid():
                new_account = account_form.save(commit=False)
                new_account.user = request.user
                new_account.save()
                if account_form.cleaned_data.get('set_active') or preferences.active_account_id is None:
                    active_account = new_account
                    preferences = sync_preferences_with_account(preferences, new_account)
                success_message = translate('views.success.account_created', language=language, default='Compte de trading cree.')
                preferences_form = TradingPreferenceForm(instance=preferences, language=language)
                account_form = TradingAccountForm(prefix='create-account', initial={'currency': active_account.currency}, language=language)
                trading_accounts = get_trading_accounts_for_user(request.user.pk)
                archived_trading_accounts = get_archived_trading_accounts_for_user(request.user.pk)
            else:
                show_account_form_modal = True
        elif action == 'update_account':
            account_id = request.POST.get('account_id')
            editing_account = TradingAccount.objects.filter(
                user=request.user,
                pk=account_id,
                archived_at__isnull=True,
            ).first()
            if editing_account is None:
                error_message = translate('views.error.account_missing', language=language, default='Compte de trading introuvable.')
            else:
                edit_account_form = TradingAccountEditForm(
                    request.POST,
                    instance=editing_account,
                    prefix='edit-account',
                    language=language,
                )
                if edit_account_form.is_valid():
                    updated_account = edit_account_form.save()
                    should_activate = (
                        edit_account_form.cleaned_data.get('set_active')
                        or active_account.id == updated_account.id
                    )
                    if should_activate:
                        active_account = updated_account
                        preferences = sync_preferences_with_account(preferences, updated_account)
                        preferences_form = TradingPreferenceForm(instance=preferences, language=language)
                    editing_account = updated_account
                    edit_account_form = TradingAccountEditForm(
                        instance=updated_account,
                        prefix='edit-account',
                        initial={'set_active': active_account.id == updated_account.id},
                        language=language,
                    )
                    success_message = translate('views.success.account_updated', language=language, default='Compte mis a jour : {account}.', account=updated_account.name)
                else:
                    show_account_edit_modal = True
        elif action == 'activate_account':
            account_id = request.POST.get('account_id')
            selected_account = switch_active_account_for_user(request.user.pk, account_id)
            if selected_account:
                active_account = selected_account
                preferences = get_or_create_preferences_for_user(request.user.pk)
                preferences_form = TradingPreferenceForm(instance=preferences, language=language)
                success_message = translate('views.success.account_activated', language=language, default='Compte actif defini sur {account}.', account=selected_account.name)
            else:
                error_message = translate('views.error.account_activate_failed', language=language, default='Activation du compte impossible.')
        elif action == 'archive_account':
            result = archive_trading_account_for_user(request.user.pk, request.POST.get('account_id'))
            if result.get('ok'):
                success_message = result['message']
                preferences = get_or_create_preferences_for_user(request.user.pk)
                active_account = get_or_create_active_account_for_user(request.user.pk, preferences)
                preferences_form = TradingPreferenceForm(instance=preferences, language=language)
                trading_accounts = get_trading_accounts_for_user(request.user.pk)
                archived_trading_accounts = get_archived_trading_accounts_for_user(request.user.pk)
            else:
                error_message = result.get(
                    'message',
                    translate('views.error.account_archive_failed', language=language, default='Archivage du compte impossible.'),
                )
        elif action == 'restore_account':
            result = restore_trading_account_for_user(request.user.pk, request.POST.get('account_id'))
            if result.get('ok'):
                success_message = result['message']
                trading_accounts = get_trading_accounts_for_user(request.user.pk)
                archived_trading_accounts = get_archived_trading_accounts_for_user(request.user.pk)
            else:
                error_message = result.get(
                    'message',
                    translate('views.error.account_restore_failed', language=language, default='Restauration du compte impossible.'),
                )
        elif action == 'password':
            password_form = TradingPasswordChangeForm(request.user, request.POST, language=language)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                success_message = translate('views.success.password_updated', language=language, default='Mot de passe mis a jour.')
                password_form = TradingPasswordChangeForm(request.user, language=language)
        elif action == 'server_refresh_mark_updated':
            if request.user.is_superuser:
                mark_server_refresh_updated()
                server_refresh = build_server_refresh_snapshot(language=language)
                success_message = translate(
                    'views.success.server_refresh_updated',
                    language=language,
                    default='Le compte a rebours serveur a ete reinitialise pour un mois.',
                )
            else:
                error_message = translate(
                    'views.error.super_admin_only',
                    language=language,
                    default='Action reservee au super administrateur.',
                )
        elif action == 'server_refresh_disable':
            if request.user.is_superuser:
                disable_server_refresh_tracking()
                server_refresh = build_server_refresh_snapshot(language=language)
                success_message = translate(
                    'views.success.server_refresh_disabled',
                    language=language,
                    default='Le suivi mensuel du serveur a ete desactive.',
                )
            else:
                error_message = translate(
                    'views.error.super_admin_only',
                    language=language,
                    default='Action reservee au super administrateur.',
                )
        elif action == 'server_refresh_enable':
            if request.user.is_superuser:
                enable_server_refresh_tracking()
                server_refresh = build_server_refresh_snapshot(language=language)
                success_message = translate(
                    'views.success.server_refresh_enabled',
                    language=language,
                    default='Le suivi mensuel du serveur a ete reactive pour un nouveau cycle.',
                )
            else:
                error_message = translate(
                    'views.error.super_admin_only',
                    language=language,
                    default='Action reservee au super administrateur.',
                )
        elif action == 'delete_account':
            delete_account_form = DeleteAccountForm(request.POST, user=request.user, language=language)
            if delete_account_form.is_valid():
                user = request.user
                logout(request)
                user.delete()
                response = redirect('app:login')
                response.delete_cookie(settings.LANGUAGE_COOKIE_NAME)
                return response

    trading_accounts = get_trading_accounts_for_user(request.user.pk)
    archived_trading_accounts = get_archived_trading_accounts_for_user(request.user.pk)
    if request.user.is_superuser:
        server_refresh = build_server_refresh_snapshot(language=language)
    current_capital = get_current_capital_for_user(request.user.pk, preferences, account=active_account)
    initial_capital_gp_percent = (
        ((current_capital - active_account.capital_base) / active_account.capital_base) * Decimal('100')
        if active_account.capital_base
        else Decimal('0.00')
    ).quantize(Decimal('0.01'))

    response = render(
        request,
        'app/settings.html',
        {
            'preferences': preferences,
            'active_account': active_account,
            'trading_accounts': trading_accounts,
            'archived_trading_accounts': archived_trading_accounts,
            'current_capital': current_capital,
            'current_capital_formatted': format_currency(current_capital, active_account.currency),
            'initial_capital_formatted': format_currency(active_account.capital_base, active_account.currency),
            'initial_capital_gp_percent': initial_capital_gp_percent,
            'initial_capital_gp_percent_label': format_signed_percent(initial_capital_gp_percent),
            'initial_capital_gp_tone': (
                'profit' if initial_capital_gp_percent > 0 else
                'loss' if initial_capital_gp_percent < 0 else
                'flat'
            ),
            'preferences_form': preferences_form,
            'account_form': account_form,
            'show_account_form_modal': show_account_form_modal,
            'edit_account_form': edit_account_form,
            'editing_account': editing_account,
            'show_account_edit_modal': show_account_edit_modal,
            'password_form': password_form,
            'delete_account_form': delete_account_form,
            'success_message': success_message,
            'error_message': error_message,
            'server_refresh': server_refresh,
        },
    )
    if response_language:
        return apply_language_cookie(response, response_language)
    return response


@login_required
@require_POST
async def switch_account_view(request):
    user = await request.auser()
    language = normalize_language(getattr(request, 'LANGUAGE_CODE', None))
    payload = await sync_to_async(lambda: request.POST.copy(), thread_sensitive=True)()
    account_id = payload.get('account_id')

    account = await sync_to_async(switch_active_account_for_user)(user.pk, account_id)
    if account is None:
        return JsonResponse({'ok': False, 'message': 'Compte de trading introuvable.'}, status=404)

    return JsonResponse(
        {
            'ok': True,
            'message': f"{translate('views.success.account_activated', language=language, default='Compte actif defini sur {account}.', account=build_account_label(account, language=language))}",
            'account': {
                'id': account.id,
                'name': account.name,
                'label': build_account_label(account, language=language),
            },
        }
    )


@login_required
@require_GET
async def dashboard_data_view(request):
    user = await request.auser()
    language = normalize_language(getattr(request, 'LANGUAGE_CODE', None))
    payload = await sync_to_async(build_dashboard_payload_for_user)(
        user.pk,
        request.GET.get('month'),
        request.GET.get('year'),
        language,
    )
    return JsonResponse(payload)


@login_required
@require_GET
async def transactions_data_view(request):
    user = await request.auser()
    language = normalize_language(getattr(request, 'LANGUAGE_CODE', None))
    payload = await sync_to_async(build_transactions_payload_for_user)(user.pk, language)
    return JsonResponse(payload)


@login_required
@require_POST
async def create_trade_view(request):
    user = await request.auser()
    language = normalize_language(getattr(request, 'LANGUAGE_CODE', None))
    payload = await sync_to_async(lambda: request.POST.copy(), thread_sensitive=True)()
    files = await sync_to_async(lambda: request.FILES.copy(), thread_sensitive=True)()

    result = await sync_to_async(create_trade_for_user)(
        user.pk,
        payload,
        files,
        TradeCreateForm,
        language,
    )
    status = 201 if result.get('ok') else 400
    return JsonResponse(result, status=status)


@login_required
@require_POST
async def update_trade_view(request, trade_id):
    user = await request.auser()
    language = normalize_language(getattr(request, 'LANGUAGE_CODE', None))
    payload = await sync_to_async(lambda: request.POST.copy(), thread_sensitive=True)()
    files = await sync_to_async(lambda: request.FILES.copy(), thread_sensitive=True)()

    result = await sync_to_async(update_trade_for_user)(
        user.pk,
        trade_id,
        payload,
        files,
        TradeCreateForm,
        language,
    )
    status = 200 if result.get('ok') else 400
    if result.get('message') == 'Trade introuvable.':
        status = 404
    return JsonResponse(result, status=status)


@login_required
@require_POST
async def create_capital_movement_view(request):
    user = await request.auser()
    language = normalize_language(getattr(request, 'LANGUAGE_CODE', None))
    payload = await sync_to_async(lambda: request.POST.copy(), thread_sensitive=True)()

    result = await sync_to_async(create_capital_movement_for_user)(
        user.pk,
        payload,
        CapitalMovementForm,
        language,
    )
    status = 201 if result.get('ok') else 400
    return JsonResponse(result, status=status)


@login_required
@require_POST
async def seed_demo_data_view(request):
    user = await request.auser()
    language = normalize_language(getattr(request, 'LANGUAGE_CODE', None))
    if not user.is_superuser:
        return JsonResponse(
            {
                'ok': False,
                'message': translate('dashboard.demo.super_admin_only', language),
            },
            status=403,
        )
    result = await sync_to_async(seed_demo_trades_for_user)(user.pk, language)
    status = 200 if result.get('ok') else 400
    return JsonResponse(result, status=status)

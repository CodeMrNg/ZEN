import shutil
import tempfile
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .error_views import custom_page_not_found, custom_server_error
from .localization import translate
from .models import CapitalMovement, ServerRefreshStatus, SocialLink, Trade, TradingAccount, TradingPreference


class DashboardAccessTests(TestCase):
    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse('app:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('app:login'), response.url)

    def test_transactions_requires_authentication(self):
        response = self.client.get(reverse('app:transactions'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('app:login'), response.url)

    def test_tools_requires_authentication(self):
        response = self.client.get(reverse('app:tools'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('app:login'), response.url)


@override_settings(APP_TRANSLATION_PROVIDER="builtin")
class ErrorPageViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_custom_404_page_renders_french_content_for_guest(self):
        request = self.factory.get("/page-introuvable/")
        request.user = AnonymousUser()

        response = custom_page_not_found(request, Exception("missing"))

        self.assertEqual(response.status_code, 404)
        self.assertIn("Page introuvable", response.content.decode("utf-8"))
        self.assertIn(reverse("app:login"), response.content.decode("utf-8"))
        self.assertIn(reverse("app:register"), response.content.decode("utf-8"))

    def test_custom_500_page_renders_english_content_from_cookie(self):
        request = self.factory.get("/boom/")
        request.user = type("AuthenticatedUser", (), {"is_authenticated": True})()
        request.COOKIES["django_language"] = "en"

        response = custom_server_error(request)

        content = response.content.decode("utf-8")
        self.assertEqual(response.status_code, 500)
        self.assertIn("Temporary server issue", content)
        self.assertIn("Back to dashboard", content)
        self.assertIn("Reload page", content)
        self.assertIn('lang="en"', content)


class LocalizationProviderTests(SimpleTestCase):
    @override_settings(APP_TRANSLATION_PROVIDER="google_free")
    @patch("app.localization.translate_with_provider")
    def test_translate_uses_external_provider_when_configured(self, mock_translate_with_provider):
        mock_translate_with_provider.return_value = "Account updated: FTMO."

        value = translate(
            "views.success.account_updated",
            language="en",
            account="FTMO",
        )

        self.assertEqual(value, "Account updated: FTMO.")
        mock_translate_with_provider.assert_called_once_with(
            "Compte mis a jour : FTMO.",
            target_language="en",
            source_language="fr",
        )

    @override_settings(APP_TRANSLATION_PROVIDER="google_free")
    @patch("app.localization.translate_with_provider")
    def test_translate_falls_back_to_builtin_when_provider_returns_none(self, mock_translate_with_provider):
        mock_translate_with_provider.return_value = None

        value = translate("dashboard.header.title", language="en")

        self.assertEqual(value, "Performance dashboard")


@override_settings(APP_TRANSLATION_PROVIDER="builtin")
class TradingJournalApiTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.settings_ctx = self.settings(MEDIA_ROOT=self.media_root)
        self.settings_ctx.enable()
        self.user = User.objects.create_user(
            username='mikefx',
            email='mike@example.com',
            password='S3curePass123',
        )
        self.client.force_login(self.user)

    def tearDown(self):
        self.settings_ctx.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)
        super().tearDown()

    def get_active_account(self):
        preferences, _ = TradingPreference.objects.get_or_create(user=self.user)
        account, _ = TradingAccount.objects.get_or_create(
            user=self.user,
            name='Compte principal',
            defaults={
                'capital_base': preferences.capital_base,
                'currency': preferences.currency,
            },
        )
        if preferences.active_account_id != account.id:
            preferences.active_account = account
            preferences.capital_base = account.capital_base
            preferences.currency = account.currency
            preferences.save(update_fields=['active_account', 'capital_base', 'currency'])
        return account

    def create_trade(self):
        account = self.get_active_account()
        return Trade.objects.create(
            user=self.user,
            account=account,
            executed_at=timezone.now(),
            symbol='XAUUSD',
            market='Commodities',
            direction=Trade.Direction.LONG,
            result=Trade.Result.TAKE_PROFIT,
            setup='Breakout',
            entry_price=Decimal('1.1000'),
            rr_ratio=Decimal('2.50'),
            exit_price=Decimal('1.1250'),
            quantity=Decimal('100.00'),
            lot_size=Decimal('1.00'),
            gp_value=Decimal('125.00'),
            fees=Decimal('5.00'),
            risk_amount=Decimal('40.00'),
            risk_percent=Decimal('0.40'),
            capital_base=account.capital_base,
            confidence=4,
            notes='Trade test',
        )

    def make_test_image(self, name='trade.gif'):
        return SimpleUploadedFile(
            name,
            (
                b'GIF89a\x01\x00\x01\x00\x80\x00\x00'
                b'\x00\x00\x00\xff\xff\xff!\xf9\x04'
                b'\x01\x00\x00\x00\x00,\x00\x00\x00'
                b'\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
            ),
            content_type='image/gif',
        )

    def test_dashboard_api_returns_metrics(self):
        self.create_trade()
        response = self.client.get(reverse('app:dashboard-data'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['summary']['has_data'])
        self.assertEqual(payload['overview']['all_time_trade_count'], 1)
        self.assertEqual(len(payload['metrics']), 5)
        self.assertIn('trade_map', payload['calendar'])
        self.assertEqual(payload['preferences']['default_symbol'], 'XAUUSD')
        self.assertEqual(payload['preferences']['currency'], 'USD')
        self.assertEqual(payload['preferences']['current_capital_formatted'], '$10,095.00')
        self.assertEqual(len(payload['recent_trades']), 1)
        self.assertEqual(len(payload['monthly_trades']), 1)

    def test_dashboard_api_limits_recent_trades_to_five_and_exposes_full_month_list(self):
        account = self.get_active_account()
        now = timezone.now()

        for index in range(7):
            Trade.objects.create(
                user=self.user,
                account=account,
                executed_at=now - timedelta(minutes=(6 - index)),
                symbol='XAUUSD',
                market='Commodities',
                direction=Trade.Direction.LONG,
                result=Trade.Result.TAKE_PROFIT,
                setup=f'Trade {index + 1}',
                entry_price=Decimal('1.1000'),
                rr_ratio=Decimal('1.50'),
                exit_price=Decimal('1.1000'),
                quantity=Decimal('1.00'),
                lot_size=Decimal('1.00'),
                gp_value=Decimal('100.00'),
                fees=Decimal('0.00'),
                risk_amount=Decimal('50.00'),
                risk_percent=Decimal('0.50'),
                capital_base=Decimal('10000.00'),
                confidence=4,
            )

        Trade.objects.create(
            user=self.user,
            account=account,
            executed_at=now - timedelta(days=40),
            symbol='NAS100',
            market='Indices',
            direction=Trade.Direction.SHORT,
            result=Trade.Result.STOP_LOSS,
            setup='Old month trade',
            entry_price=Decimal('1.1000'),
            rr_ratio=Decimal('-1.00'),
            exit_price=Decimal('1.1000'),
            quantity=Decimal('1.00'),
            lot_size=Decimal('1.00'),
            gp_value=Decimal('-50.00'),
            fees=Decimal('0.00'),
            risk_amount=Decimal('50.00'),
            risk_percent=Decimal('0.50'),
            capital_base=Decimal('10000.00'),
            confidence=3,
        )

        response = self.client.get(reverse('app:dashboard-data'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload['recent_trades']), 5)
        self.assertEqual(len(payload['monthly_trades']), 7)
        self.assertEqual(payload['monthly_trades'][0]['setup'], 'Trade 7')
        self.assertEqual(payload['recent_trades'][0]['setup'], 'Trade 7')
        self.assertEqual(payload['recent_trades'][-1]['setup'], 'Trade 3')

    def test_settings_preferences_update_user_language_and_cookie(self):
        response = self.client.post(
            reverse('app:settings'),
            data={
                'action': 'preferences',
                'ui_language': 'en',
                'default_symbol': 'eurusd',
                'default_direction': 'SHORT',
                'default_setup': 'Asia reversal',
                'default_lot_size': '2.50',
                'default_fees': '3.75',
                'default_confidence': '4',
                'capital_base': '25000.00',
                'currency': 'EUR',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<html lang="en"', html=False)
        self.assertEqual(response.cookies['django_language'].value, 'en')
        self.assertEqual(int(response.cookies['django_language']['max-age']), 31536000)

        preferences = TradingPreference.objects.get(user=self.user)
        self.assertEqual(preferences.ui_language, 'en')

    def test_authenticated_user_language_is_restored_without_cookie(self):
        TradingPreference.objects.update_or_create(
            user=self.user,
            defaults={'ui_language': 'es'},
        )
        client = self.client_class()
        client.force_login(self.user)

        response = client.get(reverse('app:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<html lang="fr"', html=False)
        self.assertEqual(response.cookies['django_language'].value, 'fr')

    def test_language_is_only_configurable_in_settings_with_fr_and_en(self):
        dashboard_response = self.client.get(reverse('app:dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertNotContains(dashboard_response, 'data-language-switcher', html=False)

        settings_response = self.client.get(reverse('app:settings'))
        self.assertEqual(settings_response.status_code, 200)
        self.assertContains(settings_response, 'name="ui_language"', html=False)
        self.assertContains(settings_response, 'value="fr"', html=False)
        self.assertContains(settings_response, 'value="en"', html=False)
        self.assertNotContains(settings_response, 'value="es"', html=False)
        self.assertNotContains(settings_response, 'value="pt"', html=False)
        self.assertNotContains(settings_response, 'value="ar"', html=False)
        self.assertNotContains(settings_response, 'value="zh-hans"', html=False)

    def test_login_uses_saved_user_language_instead_of_request_cookie(self):
        TradingPreference.objects.update_or_create(
            user=self.user,
            defaults={'ui_language': 'en'},
        )
        client = self.client_class()
        client.cookies['django_language'] = 'fr'

        login_response = client.post(
            reverse('app:login'),
            data={
                'username': 'mikefx',
                'password': 'S3curePass123',
            },
        )

        self.assertEqual(login_response.status_code, 302)
        self.assertEqual(login_response['Location'], reverse('app:dashboard'))
        self.assertEqual(login_response.cookies['django_language'].value, 'en')

        preferences = TradingPreference.objects.get(user=self.user)
        self.assertEqual(preferences.ui_language, 'en')

        dashboard_response = client.get(reverse('app:dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertContains(dashboard_response, '<html lang="en"', html=False)

    def test_dashboard_trade_payload_exposes_raw_values_for_edit(self):
        Trade.objects.create(
            user=self.user,
            executed_at=timezone.now(),
            symbol='NAS100',
            market='Indices',
            direction=Trade.Direction.SHORT,
            result=Trade.Result.STOP_LOSS,
            setup='Opening drive',
            entry_price=Decimal('3020.5000'),
            rr_ratio=Decimal('-1.50'),
            exit_price=Decimal('3020.5000'),
            quantity=Decimal('2.00'),
            lot_size=Decimal('2.00'),
            gp_value=Decimal('-150.00'),
            fees=Decimal('0.00'),
            risk_amount=Decimal('100.00'),
            risk_percent=Decimal('1.00'),
            confidence=5,
            notes='Test edition front',
        )

        response = self.client.get(reverse('app:dashboard-data'))

        self.assertEqual(response.status_code, 200)
        trade_payload = response.json()['recent_trades'][0]
        self.assertEqual(trade_payload['direction_code'], 'SHORT')
        self.assertEqual(trade_payload['result_code'], 'STOP_LOSS')
        self.assertEqual(trade_payload['entry_price_value'], '3020.5000')
        self.assertEqual(trade_payload['ratio_value'], '1.50')
        self.assertEqual(trade_payload['gp_value_value'], '150.00')
        self.assertEqual(trade_payload['lot_size_value'], '2.00')

    def test_trade_creation_api_creates_trade(self):
        TradingPreference.objects.update_or_create(
            user=self.user,
            defaults={
                'capital_base': Decimal('25000.00'),
                'default_symbol': 'XAUUSD',
            },
        )
        payload = {
            'executed_at': '2026-03-20T10:30',
            'symbol': 'xauusd',
            'direction': 'LONG',
            'setup': 'VWAP reclaim',
            'entry_price': '3020.5000',
            'rr_ratio': '2.50',
            'result': 'STOP_LOSS',
            'lot_size': '3.00',
            'gp_value': '625.00',
            'confidence': 5,
            'notes': 'Execution propre',
            'screenshots': [
                self.make_test_image('trade-a.gif'),
                self.make_test_image('trade-b.gif'),
            ],
        }

        response = self.client.post(reverse('app:trade-create'), data=payload)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['trade']['capital_change_percent_label'], '-2.50%')
        self.assertEqual(response.json()['trade']['screenshot_count'], 2)
        self.assertEqual(len(response.json()['trade']['screenshot_urls']), 2)
        self.assertEqual(len(response.json()['trade']['screenshots']), 2)
        self.assertEqual(Trade.objects.count(), 1)
        trade = Trade.objects.get()
        self.assertEqual(trade.symbol, 'XAUUSD')
        self.assertEqual(trade.market, 'Commodities')
        self.assertEqual(trade.result, Trade.Result.STOP_LOSS)
        self.assertEqual(trade.rr_ratio, Decimal('-2.50'))
        self.assertEqual(trade.gp_value, Decimal('-625.00'))
        self.assertEqual(trade.fees, Decimal('0.00'))
        self.assertEqual(trade.capital_base, Decimal('25000.00'))
        self.assertEqual(trade.risk_amount, Decimal('250.00'))
        self.assertEqual(trade.risk_percent, Decimal('1.00'))
        self.assertEqual(trade.screenshots.count(), 2)

    def test_dashboard_api_serializes_trade_gallery(self):
        trade = self.create_trade()
        trade.screenshots.create(image=self.make_test_image('gallery-a.gif'), sort_order=0)
        trade.screenshots.create(image=self.make_test_image('gallery-b.gif'), sort_order=1)

        response = self.client.get(reverse('app:dashboard-data'))

        self.assertEqual(response.status_code, 200)
        trade_payload = response.json()['recent_trades'][0]
        self.assertEqual(trade_payload['screenshot_count'], 2)
        self.assertEqual(len(trade_payload['screenshot_urls']), 2)
        self.assertEqual(len(trade_payload['screenshots']), 2)
        self.assertTrue(trade_payload['screenshot_url'])

    def test_trade_creation_api_uses_current_capital_as_reference(self):
        TradingPreference.objects.update_or_create(
            user=self.user,
            defaults={
                'capital_base': Decimal('10000.00'),
                'default_symbol': 'XAUUSD',
            },
        )
        self.create_trade()
        CapitalMovement.objects.create(
            user=self.user,
            kind=CapitalMovement.Kind.DEPOSIT,
            amount=Decimal('500.00'),
            occurred_at=timezone.now(),
            note='Ajout de capital',
        )
        CapitalMovement.objects.create(
            user=self.user,
            kind=CapitalMovement.Kind.WITHDRAWAL,
            amount=Decimal('200.00'),
            occurred_at=timezone.now(),
            note='Retrait profit',
        )

        response = self.client.post(
            reverse('app:trade-create'),
            data={
                'executed_at': '2026-03-20T10:30',
                'symbol': 'xauusd',
                'direction': 'LONG',
                'setup': 'VWAP reclaim',
                'entry_price': '3020.5000',
                'rr_ratio': '2.50',
                'result': 'STOP_LOSS',
                'lot_size': '3.00',
                'gp_value': '625.00',
                'confidence': 5,
                'notes': 'Execution sur capital actuel',
            },
        )

        self.assertEqual(response.status_code, 201)
        trade = Trade.objects.order_by('-id').first()
        self.assertEqual(trade.capital_base, Decimal('10395.00'))
        self.assertEqual(trade.risk_amount, Decimal('250.00'))
        self.assertEqual(trade.risk_percent, Decimal('2.41'))
        self.assertEqual(response.json()['trade']['capital_change_percent_label'], '-6.01%')

    def test_demo_seed_endpoint_populates_when_empty(self):
        self.user.is_superuser = True
        self.user.save(update_fields=['is_superuser'])
        response = self.client.post(reverse('app:demo-seed'))

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(Trade.objects.count(), 10)

    def test_demo_seed_endpoint_is_restricted_to_super_admin(self):
        response = self.client.post(reverse('app:demo-seed'))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['ok'], False)

    def test_dashboard_shows_super_admin_badge_and_demo_button_only_for_super_admin(self):
        self.get_active_account()

        response = self.client.get(reverse('app:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="demo-button"', html=False)
        self.assertNotContains(response, 'Super admin')

        self.user.is_superuser = True
        self.user.save(update_fields=['is_superuser'])

        response = self.client.get(reverse('app:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="demo-button"', html=False)
        self.assertContains(response, 'Super admin')

    def test_dashboard_shows_server_refresh_countdown_only_for_super_admin(self):
        self.get_active_account()
        ServerRefreshStatus.objects.create(
            is_enabled=True,
            last_refreshed_at=timezone.now() - timedelta(days=10),
        )

        response = self.client.get(reverse('app:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="server-refresh-countdown"', html=False)

        self.user.is_superuser = True
        self.user.save(update_fields=['is_superuser'])

        response = self.client.get(reverse('app:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="server-refresh-countdown"', html=False)
        self.assertContains(response, 'Actualisation mensuelle du serveur')

    def test_dashboard_hides_server_refresh_card_when_disabled(self):
        self.get_active_account()
        self.user.is_superuser = True
        self.user.save(update_fields=['is_superuser'])
        ServerRefreshStatus.objects.create(
            is_enabled=False,
            last_refreshed_at=timezone.now() - timedelta(days=10),
        )

        response = self.client.get(reverse('app:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="server-refresh-countdown"', html=False)
        self.assertNotContains(response, 'Actualisation mensuelle du serveur')

    def test_settings_view_allows_super_admin_to_refresh_server_countdown(self):
        self.user.is_superuser = True
        self.user.save(update_fields=['is_superuser'])
        server_refresh = ServerRefreshStatus.objects.create(
            is_enabled=True,
            last_refreshed_at=timezone.now() - timedelta(days=20),
        )
        previous_refresh_at = server_refresh.last_refreshed_at

        response = self.client.post(
            reverse('app:settings'),
            data={'action': 'server_refresh_mark_updated'},
        )

        self.assertEqual(response.status_code, 200)
        server_refresh.refresh_from_db()
        self.assertTrue(server_refresh.is_enabled)
        self.assertGreater(server_refresh.last_refreshed_at, previous_refresh_at)
        self.assertContains(response, 'Le compte a rebours serveur a ete reinitialise pour un mois.')

    def test_settings_view_allows_super_admin_to_disable_and_enable_server_countdown(self):
        self.user.is_superuser = True
        self.user.save(update_fields=['is_superuser'])
        server_refresh = ServerRefreshStatus.objects.create(
            is_enabled=True,
            last_refreshed_at=timezone.now() - timedelta(days=12),
        )

        disable_response = self.client.post(
            reverse('app:settings'),
            data={'action': 'server_refresh_disable'},
        )

        self.assertEqual(disable_response.status_code, 200)
        server_refresh.refresh_from_db()
        self.assertFalse(server_refresh.is_enabled)
        self.assertContains(disable_response, 'Le suivi mensuel du serveur a ete desactive.')

        previous_refresh_at = server_refresh.last_refreshed_at
        enable_response = self.client.post(
            reverse('app:settings'),
            data={'action': 'server_refresh_enable'},
        )

        self.assertEqual(enable_response.status_code, 200)
        server_refresh.refresh_from_db()
        self.assertTrue(server_refresh.is_enabled)
        self.assertGreater(server_refresh.last_refreshed_at, previous_refresh_at)
        self.assertContains(enable_response, 'Le suivi mensuel du serveur a ete reactive pour un nouveau cycle.')

    def test_settings_view_rejects_server_refresh_actions_for_non_super_admin(self):
        server_refresh = ServerRefreshStatus.objects.create(
            is_enabled=True,
            last_refreshed_at=timezone.now() - timedelta(days=5),
        )

        response = self.client.post(
            reverse('app:settings'),
            data={'action': 'server_refresh_disable'},
        )

        self.assertEqual(response.status_code, 200)
        server_refresh.refresh_from_db()
        self.assertTrue(server_refresh.is_enabled)
        self.assertContains(response, 'Action reservee au super administrateur.')

    def test_transactions_api_returns_monthly_history(self):
        self.create_trade()
        Trade.objects.create(
            user=self.user,
            executed_at=timezone.now() - timedelta(days=35),
            symbol='XAUUSD',
            market='Commodities',
            direction=Trade.Direction.LONG,
            result=Trade.Result.STOP_LOSS,
            setup='Failed breakout',
            entry_price=Decimal('1.1000'),
            rr_ratio=Decimal('-1.00'),
            exit_price=Decimal('1.1000'),
            quantity=Decimal('1.00'),
            lot_size=Decimal('1.00'),
            gp_value=Decimal('-50.00'),
            fees=Decimal('0.00'),
            risk_amount=Decimal('50.00'),
            risk_percent=Decimal('0.50'),
            confidence=3,
            notes='Mois faible',
        )
        CapitalMovement.objects.create(
            user=self.user,
            kind=CapitalMovement.Kind.DEPOSIT,
            amount=Decimal('500.00'),
            occurred_at=timezone.now(),
            note='Ajout de capital',
        )
        CapitalMovement.objects.create(
            user=self.user,
            kind=CapitalMovement.Kind.WITHDRAWAL,
            amount=Decimal('200.00'),
            occurred_at=timezone.now(),
            note='Retrait profit',
        )

        response = self.client.get(reverse('app:transactions-data'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['summary']['current_capital_label'], '$10,345.00')
        self.assertEqual(payload['summary']['trade_count_month'], 1)
        self.assertEqual(payload['summary']['winners_month'], 1)
        self.assertEqual(payload['summary']['losers_month'], 0)
        self.assertEqual(payload['highlights']['deposits_label'], '$500.00')
        self.assertEqual(payload['highlights']['withdrawals_label'], '$200.00')
        self.assertIn('$395.00', payload['highlights']['best_month_label'])
        self.assertIn('-$50.00', payload['highlights']['worst_month_label'])
        self.assertEqual(len(payload['monthly_history']), 2)
        self.assertEqual(len(payload['all_movements']), 2)
        self.assertEqual(payload['all_movements'][0]['kind'], 'WITHDRAWAL')
        self.assertEqual(payload['all_movements'][1]['kind'], 'DEPOSIT')
        self.assertEqual(payload['monthly_history'][0]['capital_start_label'], '$9,950.00')
        self.assertEqual(payload['monthly_history'][1]['capital_start_label'], '$10,000.00')
        self.assertEqual(payload['monthly_history'][0]['trade_count'], 1)
        self.assertEqual(payload['monthly_history'][0]['winners'], 1)
        self.assertEqual(payload['monthly_history'][0]['losers'], 0)
        self.assertTrue(payload['monthly_history'][0]['is_best_month'])
        self.assertTrue(payload['monthly_history'][1]['is_worst_month'])

    def test_capital_movement_create_api_creates_withdrawal(self):
        response = self.client.post(
            reverse('app:capital-movement-create'),
            data={
                'kind': CapitalMovement.Kind.WITHDRAWAL,
                'occurred_at': '2026-03-22T12:45',
                'amount': '150.00',
                'note': 'Retrait hebdo',
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(CapitalMovement.objects.count(), 1)
        movement = CapitalMovement.objects.get()
        self.assertEqual(movement.kind, CapitalMovement.Kind.WITHDRAWAL)
        self.assertEqual(movement.amount, Decimal('150.00'))
        self.assertEqual(response.json()['movement']['amount_label'], '-$150.00')

    def test_trade_update_api_updates_trade(self):
        trade = self.create_trade()
        TradingPreference.objects.update_or_create(
            user=self.user,
            defaults={
                'capital_base': Decimal('25000.00'),
                'default_symbol': 'XAUUSD',
            },
        )

        response = self.client.post(
            reverse('app:trade-update', args=[trade.pk]),
            data={
                'executed_at': '2026-03-22T09:15',
                'symbol': 'nas100',
                'direction': 'SHORT',
                'setup': 'NY reversal',
                'entry_price': '0.0001',
                'rr_ratio': '1.50',
                'result': 'TAKE_PROFIT',
                'lot_size': '2.50',
                'gp_value': '150.00',
                'confidence': '5',
                'notes': 'Trade modifie',
            },
        )

        self.assertEqual(response.status_code, 200)
        trade.refresh_from_db()
        self.assertEqual(trade.symbol, 'NAS100')
        self.assertEqual(trade.direction, Trade.Direction.SHORT)
        self.assertEqual(trade.setup, 'NY reversal')
        self.assertEqual(trade.result, Trade.Result.TAKE_PROFIT)
        self.assertEqual(trade.rr_ratio, Decimal('1.50'))
        self.assertEqual(trade.gp_value, Decimal('150.00'))
        self.assertEqual(trade.capital_base, Decimal('10000.00'))
        self.assertEqual(trade.risk_amount, Decimal('100.00'))

    def test_trade_update_api_can_remove_existing_screenshots(self):
        trade = self.create_trade()
        screenshot_a = trade.screenshots.create(image=self.make_test_image('edit-a.gif'), sort_order=0)
        screenshot_b = trade.screenshots.create(image=self.make_test_image('edit-b.gif'), sort_order=1)

        response = self.client.post(
            reverse('app:trade-update', args=[trade.pk]),
            data={
                'executed_at': '2026-03-22T09:15',
                'symbol': 'xauusd',
                'direction': 'LONG',
                'setup': 'Breakout',
                'entry_price': '0.0001',
                'rr_ratio': '2.50',
                'result': 'TAKE_PROFIT',
                'lot_size': '1.00',
                'gp_value': '125.00',
                'confidence': '4',
                'notes': 'Trade avec galerie mise a jour',
                'removed_screenshot_ids': [str(screenshot_a.pk)],
            },
        )

        self.assertEqual(response.status_code, 200)
        trade.refresh_from_db()
        remaining_screenshots = list(trade.screenshots.order_by('sort_order', 'pk'))
        self.assertEqual(len(remaining_screenshots), 1)
        self.assertEqual(remaining_screenshots[0].pk, screenshot_b.pk)
        self.assertEqual(remaining_screenshots[0].sort_order, 0)
        self.assertEqual(response.json()['trade']['screenshot_count'], 1)
        self.assertEqual(response.json()['trade']['screenshots'][0]['id'], str(screenshot_b.pk))

    def test_settings_view_updates_preferences(self):
        response = self.client.post(
            reverse('app:settings'),
            data={
                'action': 'preferences',
                'ui_language': 'fr',
                'default_symbol': 'eurusd',
                'default_direction': 'SHORT',
                'default_setup': 'Asia reversal',
                'default_lot_size': '2.50',
                'default_fees': '3.75',
                'default_confidence': '4',
                'capital_base': '25000.00',
                'currency': 'EUR',
            },
        )

        self.assertEqual(response.status_code, 200)
        preferences = TradingPreference.objects.get(user=self.user)
        self.assertEqual(preferences.default_symbol, 'EURUSD')
        self.assertEqual(preferences.default_direction, Trade.Direction.SHORT)
        self.assertEqual(preferences.default_setup, 'Asia reversal')
        self.assertEqual(preferences.ui_language, 'fr')
        self.assertEqual(preferences.capital_base, Decimal('25000.00'))
        self.assertEqual(preferences.currency, TradingPreference.Currency.EUR)
        self.assertContains(response, 'Configuration enregistree.')

    def test_settings_view_displays_current_and_initial_capital_metrics(self):
        self.create_trade()
        CapitalMovement.objects.create(
            user=self.user,
            account=self.get_active_account(),
            kind=CapitalMovement.Kind.DEPOSIT,
            amount=Decimal('500.00'),
            occurred_at=timezone.now(),
            note='Ajout de capital',
        )
        CapitalMovement.objects.create(
            user=self.user,
            account=self.get_active_account(),
            kind=CapitalMovement.Kind.WITHDRAWAL,
            amount=Decimal('200.00'),
            occurred_at=timezone.now(),
            note='Retrait profit',
        )

        response = self.client.get(reverse('app:settings'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '$10,395.00')
        self.assertContains(response, '$10,000.00')
        self.assertContains(response, '+3.95%')
        self.assertContains(response, 'Capital initial')

    def test_settings_view_does_not_autofocus_any_input(self):
        self.get_active_account()

        response = self.client.get(reverse('app:settings'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'autofocus', html=False)

    def test_settings_view_changes_password(self):
        response = self.client.post(
            reverse('app:settings'),
            data={
                'action': 'password',
                'old_password': 'S3curePass123',
                'new_password1': 'NouveauPass456!',
                'new_password2': 'NouveauPass456!',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NouveauPass456!'))
        self.assertContains(response, 'Mot de passe mis a jour.')

    def test_settings_view_deletes_account(self):
        response = self.client.post(
            reverse('app:settings'),
            data={
                'action': 'delete_account',
                'password': 'S3curePass123',
                'confirmation': 'on',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_settings_view_can_add_and_activate_second_trading_account(self):
        self.get_active_account()

        response = self.client.post(
            reverse('app:settings'),
            data={
                'action': 'create_account',
                'create-account-name': 'FTMO Swing',
                'create-account-broker': 'FTMO',
                'create-account-account_identifier': 'ACC-002',
                'create-account-capital_base': '5000.00',
                'create-account-currency': 'EUR',
                'create-account-set_active': 'on',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(TradingAccount.objects.filter(user=self.user).count(), 2)
        preferences = TradingPreference.objects.get(user=self.user)
        self.assertEqual(preferences.active_account.name, 'FTMO Swing')
        self.assertEqual(preferences.currency, 'EUR')
        self.assertContains(response, 'Compte de trading cree.')

    def test_account_switch_api_changes_active_account(self):
        self.get_active_account()
        second_account = TradingAccount.objects.create(
            user=self.user,
            name='Compte prop',
            broker='FundedNext',
            capital_base=Decimal('5000.00'),
            currency='EUR',
        )

        response = self.client.post(
            reverse('app:account-switch'),
            data={'account_id': second_account.id},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 200)
        preferences = TradingPreference.objects.get(user=self.user)
        self.assertEqual(preferences.active_account_id, second_account.id)
        self.assertEqual(preferences.currency, 'EUR')
        self.assertEqual(response.json()['account']['name'], 'Compte prop')

    def test_settings_view_can_archive_inactive_account(self):
        primary_account = self.get_active_account()
        second_account = TradingAccount.objects.create(
            user=self.user,
            name='FTMO Swing',
            broker='FTMO',
            capital_base=Decimal('5000.00'),
            currency='EUR',
        )

        response = self.client.post(
            reverse('app:settings'),
            data={
                'action': 'archive_account',
                'account_id': second_account.id,
            },
        )

        self.assertEqual(response.status_code, 200)
        second_account.refresh_from_db()
        preferences = TradingPreference.objects.get(user=self.user)
        self.assertIsNotNone(second_account.archived_at)
        self.assertEqual(preferences.active_account_id, primary_account.id)
        self.assertContains(response, 'Compte archive')

    def test_settings_view_can_update_account_information(self):
        active_account = self.get_active_account()

        response = self.client.post(
            reverse('app:settings'),
            data={
                'action': 'update_account',
                'account_id': active_account.id,
                'edit-account-name': 'Compte perso swing',
                'edit-account-broker': 'IC Markets',
                'edit-account-account_identifier': 'ACC-901',
                'edit-account-capital_base': '15000.00',
                'edit-account-currency': 'GBP',
                'edit-account-set_active': 'on',
            },
        )

        self.assertEqual(response.status_code, 200)
        active_account.refresh_from_db()
        preferences = TradingPreference.objects.get(user=self.user)
        self.assertEqual(active_account.name, 'Compte perso swing')
        self.assertEqual(active_account.broker, 'IC Markets')
        self.assertEqual(active_account.account_identifier, 'ACC-901')
        self.assertEqual(active_account.capital_base, Decimal('15000.00'))
        self.assertEqual(active_account.currency, 'GBP')
        self.assertEqual(preferences.active_account_id, active_account.id)
        self.assertEqual(preferences.currency, 'GBP')
        self.assertContains(response, 'Compte mis a jour')

    def test_settings_view_rejects_archiving_active_account(self):
        primary_account = self.get_active_account()
        TradingAccount.objects.create(
            user=self.user,
            name='Compte secondaire',
            broker='FTMO',
            capital_base=Decimal('5000.00'),
            currency='EUR',
        )

        response = self.client.post(
            reverse('app:settings'),
            data={
                'action': 'archive_account',
                'account_id': primary_account.id,
            },
        )

        self.assertEqual(response.status_code, 200)
        primary_account.refresh_from_db()
        self.assertIsNone(primary_account.archived_at)
        self.assertContains(response, 'Le compte actif ne peut pas etre archive.')

    def test_dashboard_api_uses_active_trading_account_only(self):
        primary_account = self.get_active_account()
        Trade.objects.create(
            user=self.user,
            account=primary_account,
            executed_at=timezone.now(),
            symbol='XAUUSD',
            market='Commodities',
            direction=Trade.Direction.LONG,
            result=Trade.Result.TAKE_PROFIT,
            setup='Primary account trade',
            entry_price=Decimal('1.1000'),
            rr_ratio=Decimal('1.00'),
            exit_price=Decimal('1.1000'),
            quantity=Decimal('1.00'),
            lot_size=Decimal('1.00'),
            gp_value=Decimal('100.00'),
            fees=Decimal('0.00'),
            risk_amount=Decimal('100.00'),
            risk_percent=Decimal('1.00'),
            capital_base=Decimal('10000.00'),
            confidence=4,
        )
        second_account = TradingAccount.objects.create(
            user=self.user,
            name='Compte prop',
            broker='FundedNext',
            capital_base=Decimal('5000.00'),
            currency='EUR',
        )
        Trade.objects.create(
            user=self.user,
            account=second_account,
            executed_at=timezone.now(),
            symbol='NAS100',
            market='Indices',
            direction=Trade.Direction.SHORT,
            result=Trade.Result.TAKE_PROFIT,
            setup='Secondary account trade',
            entry_price=Decimal('1.1000'),
            rr_ratio=Decimal('2.00'),
            exit_price=Decimal('1.1000'),
            quantity=Decimal('1.00'),
            lot_size=Decimal('1.00'),
            gp_value=Decimal('300.00'),
            fees=Decimal('0.00'),
            risk_amount=Decimal('150.00'),
            risk_percent=Decimal('3.00'),
            capital_base=Decimal('5000.00'),
            confidence=5,
        )
        preferences = TradingPreference.objects.get(user=self.user)
        preferences.active_account = second_account
        preferences.capital_base = second_account.capital_base
        preferences.currency = second_account.currency
        preferences.save(update_fields=['active_account', 'capital_base', 'currency'])

        response = self.client.get(reverse('app:dashboard-data'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['overview']['all_time_trade_count'], 1)
        self.assertEqual(payload['overview']['best_setup'], 'Secondary account trade')
        self.assertEqual(payload['preferences']['active_account']['name'], 'Compte prop')
        self.assertIn('5,300.00', payload['preferences']['current_capital_formatted'])

    def test_dashboard_renders_only_three_active_global_social_links(self):
        self.get_active_account()
        SocialLink.objects.create(
            platform=SocialLink.Platform.WHATSAPP,
            url='https://wa.me/242000000000',
            sort_order=0,
            is_active=True,
        )
        SocialLink.objects.create(
            platform=SocialLink.Platform.X,
            url='https://x.com/akili',
            sort_order=1,
            is_active=True,
        )
        SocialLink.objects.create(
            platform=SocialLink.Platform.TELEGRAM,
            url='https://t.me/akili',
            sort_order=2,
            is_active=True,
        )
        SocialLink.objects.create(
            platform=SocialLink.Platform.YOUTUBE,
            url='https://youtube.com/@akili',
            sort_order=3,
            is_active=True,
        )
        SocialLink.objects.create(
            platform=SocialLink.Platform.LINKEDIN,
            url='https://linkedin.com/company/akili',
            sort_order=4,
            is_active=True,
        )
        SocialLink.objects.create(
            platform=SocialLink.Platform.INSTAGRAM,
            url='https://instagram.com/akili',
            sort_order=0,
            is_active=False,
        )

        response = self.client.get(reverse('app:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'https://wa.me/242000000000')
        self.assertContains(response, 'https://x.com/akili')
        self.assertContains(response, 'https://t.me/akili')
        self.assertNotContains(response, 'https://youtube.com/@akili')
        self.assertNotContains(response, 'https://linkedin.com/company/akili')
        self.assertNotContains(response, 'https://instagram.com/akili')

    def test_tools_view_renders_core_calculators(self):
        self.get_active_account()

        response = self.client.get(reverse('app:tools'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Outils de trading')
        self.assertContains(response, 'Calculateur de taille de position')
        self.assertContains(response, 'Calculateur de risque de ruine')

import calendar
import re
from datetime import date, timedelta
from decimal import Decimal

from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from .formatting import format_decimal_compact
from .localization import normalize_language, translate
from .models import CapitalMovement, Trade, TradingAccount, TradingPreference

SYMBOL_MARKETS = {
    'XAUUSD': 'Commodities',
    'EURUSD': 'Forex',
    'GBPUSD': 'Forex',
    'USDJPY': 'Forex',
    'NAS100': 'Indices',
    'US30': 'Indices',
    'BTCUSD': 'Crypto',
}


def tr(language, key, default):
    return translate(key, language=language, default=default)


def apply_choice_labels(field, labels):
    choices = [(value, labels.get(value, label)) for value, label in field.choices]
    field.choices = choices
    field.widget.choices = choices


def remove_autofocus_from_fields(form):
    for field in form.fields.values():
        field.widget.attrs.pop('autofocus', None)


class CompactDecimalInput(forms.NumberInput):
    def __init__(self, *args, decimal_places=2, **kwargs):
        self.decimal_places = decimal_places
        super().__init__(*args, **kwargs)

    def format_value(self, value):
        if value in (None, ""):
            return None
        return format_decimal_compact(value, decimal_places=self.decimal_places)


def apply_compact_decimal_widgets(form):
    for field in form.fields.values():
        if isinstance(field, forms.DecimalField):
            field.widget = CompactDecimalInput(
                attrs=field.widget.attrs.copy(),
                decimal_places=getattr(field, "decimal_places", 2) or 2,
            )


class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.FileField):
    widget = MultipleImageInput

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_field = forms.ImageField(required=False)

    def clean(self, data, initial=None):
        if not data:
            return []

        if not isinstance(data, (list, tuple)):
            data = [data]

        cleaned_files = []
        errors = []
        for uploaded_file in data:
            if not uploaded_file:
                continue
            try:
                cleaned_file = super().clean(uploaded_file, initial)
                self.image_field.clean(cleaned_file)
                cleaned_files.append(cleaned_file)
            except forms.ValidationError as error:
                errors.extend(error.error_list)

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_files


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Identifiant',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Ex: mikefx',
                'autocomplete': 'username',
                'autofocus': True,
            }
        ),
    )
    password = forms.CharField(
        label='Mot de passe',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Votre mot de passe',
                'autocomplete': 'current-password',
            }
        ),
    )

    def __init__(self, *args, language='fr', **kwargs):
        self.language = normalize_language(language)
        super().__init__(*args, **kwargs)
        self.fields['username'].label = tr(self.language, 'form.login.username', 'Identifiant')
        self.fields['username'].widget.attrs['placeholder'] = tr(
            self.language,
            'form.login.username.placeholder',
            'Ex: mikefx',
        )
        self.fields['password'].label = tr(self.language, 'form.password', 'Mot de passe')
        self.fields['password'].widget.attrs['placeholder'] = tr(
            self.language,
            'form.password.placeholder',
            'Votre mot de passe',
        )


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        label='Identifiant',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Identifiant de connexion',
                'autocomplete': 'username',
                'autofocus': True,
            }
        ),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'nom@entreprise.com',
                'autocomplete': 'email',
            }
        ),
    )
    first_name = forms.CharField(
        label='Prenom',
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Prenom',
                'autocomplete': 'given-name',
            }
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name')

    def __init__(self, *args, **kwargs):
        self.language = normalize_language(kwargs.pop('language', 'fr'))
        super().__init__(*args, **kwargs)
        self.fields['username'].label = tr(self.language, 'form.login.username', 'Identifiant')
        self.fields['username'].widget.attrs['placeholder'] = tr(
            self.language,
            'form.login.username.placeholder',
            'Identifiant de connexion',
        )
        self.fields['email'].label = tr(self.language, 'form.email', 'Email')
        self.fields['first_name'].label = tr(self.language, 'form.first_name', 'Prenom')
        self.fields['first_name'].widget.attrs['placeholder'] = tr(
            self.language,
            'form.first_name.placeholder',
            'Prenom',
        )
        self.fields['password1'].label = tr(self.language, 'form.password', 'Mot de passe')
        self.fields['password1'].widget.attrs.update(
            {
                'placeholder': tr(self.language, 'form.password.new.placeholder', 'Minimum 8 caracteres'),
                'autocomplete': 'new-password',
            }
        )
        self.fields['password2'].label = tr(self.language, 'form.password.confirmation', 'Confirmation')
        self.fields['password2'].widget.attrs.update(
            {
                'placeholder': tr(self.language, 'form.password.confirmation.placeholder', 'Confirmez le mot de passe'),
                'autocomplete': 'new-password',
            }
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        if commit:
            user.save()
        return user


class TradeCreateForm(forms.ModelForm):
    executed_at = forms.DateTimeField(
        label="Date d'execution",
        input_formats=[
            '%Y-%m-%dT%H:%M',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d %H:%M:%S',
        ],
    )
    symbol = forms.CharField(initial='XAUUSD')
    rr_ratio = forms.DecimalField(
        label='Ratio',
        max_digits=6,
        decimal_places=2,
    )
    result = forms.ChoiceField(
        label='Resultat',
        choices=Trade.Result.choices,
        initial=Trade.Result.TAKE_PROFIT,
    )
    lot_size = forms.DecimalField(
        label='Quantite (lots)',
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
    )
    gp_value = forms.DecimalField(
        label='G/P',
        max_digits=10,
        decimal_places=2,
        required=False,
    )
    risk_percent = forms.DecimalField(
        label='Risque (% capital)',
        max_digits=5,
        decimal_places=2,
        min_value=Decimal('0.00'),
        max_value=Decimal('100.00'),
        required=False,
    )
    screenshot = forms.ImageField(
        label='Capture du trade',
        required=False,
    )
    screenshots = MultipleImageField(
        label='Images du trade',
        required=False,
    )

    class Meta:
        model = Trade
        fields = (
            'executed_at',
            'symbol',
            'direction',
            'setup',
            'entry_price',
            'rr_ratio',
            'result',
            'lot_size',
            'gp_value',
            'risk_percent',
            'screenshot',
            'confidence',
            'notes',
        )

    def __init__(self, *args, preferences=None, capital_base_override=None, **kwargs):
        self.language = normalize_language(kwargs.pop('language', 'fr'))
        self.preferences = preferences
        self.capital_base_override = capital_base_override
        super().__init__(*args, **kwargs)
        apply_compact_decimal_widgets(self)
        if preferences and not self.is_bound:
            self.fields['symbol'].initial = preferences.default_symbol
            self.fields['direction'].initial = preferences.default_direction
            self.fields['setup'].initial = preferences.default_setup
            self.fields['result'].initial = Trade.Result.TAKE_PROFIT
            self.fields['lot_size'].initial = preferences.default_lot_size
            self.fields['gp_value'].initial = preferences.default_fees
            self.fields['risk_percent'].initial = preferences.default_risk_percent
            self.fields['confidence'].initial = preferences.default_confidence

    def clean_symbol(self):
        return self.cleaned_data['symbol'].upper().strip()

    def clean(self):
        cleaned_data = super().clean()
        result = cleaned_data.get('result')
        rr_ratio = cleaned_data.get('rr_ratio')
        gp_value = cleaned_data.get('gp_value')
        profit_results = {Trade.Result.TAKE_PROFIT, Trade.Result.GAIN}
        loss_results = {Trade.Result.STOP_LOSS, Trade.Result.LOSS}

        if rr_ratio is not None:
            if result in profit_results:
                cleaned_data['rr_ratio'] = abs(rr_ratio)
            elif result in loss_results:
                cleaned_data['rr_ratio'] = -abs(rr_ratio)
            elif result == Trade.Result.BREAK_EVEN:
                cleaned_data['rr_ratio'] = Decimal('0.00')

        if gp_value is not None:
            if result in profit_results:
                cleaned_data['gp_value'] = abs(gp_value)
            elif result in loss_results:
                cleaned_data['gp_value'] = -abs(gp_value)

        if result != Trade.Result.BREAK_EVEN and cleaned_data.get('gp_value') is None:
            self.add_error('gp_value', tr(self.language, 'form.trade.gp_required', 'Le champ G/P est requis pour calculer le risque.'))

        return cleaned_data

    def save(self, commit=True):
        trade = super().save(commit=False)
        if self.capital_base_override is not None:
            trade.capital_base = self.capital_base_override
        elif self.preferences and not trade.pk:
            trade.capital_base = self.capital_base_override or self.preferences.capital_base
        elif not trade.capital_base and self.preferences:
            trade.capital_base = self.capital_base_override or self.preferences.capital_base
        trade.market = SYMBOL_MARKETS.get(trade.symbol, 'Custom')
        trade.exit_price = trade.entry_price
        trade.quantity = trade.lot_size
        trade.fees = Decimal('0.00')
        if trade.result == Trade.Result.BREAK_EVEN:
            trade.risk_amount = Decimal('0.00')
            trade.risk_percent = Decimal('0.00')
        elif trade.gp_value is not None and trade.rr_ratio not in (None, Decimal('0.00')):
            trade.risk_amount = (abs(trade.gp_value) / abs(trade.rr_ratio)).quantize(Decimal('0.01'))
            trade.risk_percent = (
                trade.risk_amount / trade.capital_base * Decimal('100')
            ).quantize(Decimal('0.01'))
        elif trade.risk_percent is not None:
            trade.risk_amount = (trade.capital_base * trade.risk_percent / Decimal('100')).quantize(Decimal('0.01'))
        else:
            trade.risk_amount = Decimal('0.00')
            trade.risk_percent = Decimal('0.00')
        if commit:
            trade.save()
        return trade


class TradingPreferenceForm(forms.ModelForm):
    default_dashboard_year = forms.TypedChoiceField(
        label='Annee dashboard par defaut',
        coerce=int,
    )

    class Meta:
        model = TradingPreference
        fields = (
            'ui_language',
            'default_symbol',
            'default_direction',
            'default_setup',
            'default_lot_size',
            'default_fees',
            'default_confidence',
            'default_dashboard_year',
            'default_week_start_day',
            'capital_base',
            'currency',
        )
        labels = {
            'default_symbol': 'Paire par defaut',
            'default_direction': 'Direction par defaut',
            'default_setup': 'Setup par defaut',
            'default_lot_size': 'Quantite par defaut (lots)',
            'default_fees': 'G/P par defaut',
            'default_confidence': 'Confiance par defaut',
            'default_dashboard_year': 'Annee dashboard par defaut',
            'default_week_start_day': 'Premier jour de la semaine',
            'capital_base': 'Capital initial du compte actif',
            'currency': 'Devise du compte actif',
        }

    def __init__(self, *args, **kwargs):
        self.language = normalize_language(kwargs.pop('language', 'fr'))
        super().__init__(*args, **kwargs)
        apply_compact_decimal_widgets(self)
        remove_autofocus_from_fields(self)
        active_account = getattr(self.instance, 'active_account', None)
        year_choices = self._build_dashboard_year_choices(active_account)
        self.fields['default_dashboard_year'].choices = year_choices
        self.fields['default_dashboard_year'].widget.choices = year_choices
        if active_account and not self.is_bound:
            self.fields['capital_base'].initial = active_account.capital_base
            self.fields['currency'].initial = active_account.currency
        available_year_values = [value for value, _ in year_choices]
        default_year = getattr(self.instance, 'default_dashboard_year', None) or timezone.localdate().year
        if default_year not in available_year_values:
            default_year = timezone.localdate().year if timezone.localdate().year in available_year_values else available_year_values[0]
        if not self.is_bound:
            self.fields['default_dashboard_year'].initial = default_year
        self.fields['ui_language'].label = tr(self.language, 'language.title', "Langue de l'application")
        self.fields['default_symbol'].label = tr(self.language, 'form.preferences.default_symbol', 'Paire par defaut')
        self.fields['default_direction'].label = tr(self.language, 'form.preferences.default_direction', 'Direction par defaut')
        self.fields['default_setup'].label = tr(self.language, 'form.preferences.default_setup', 'Setup par defaut')
        self.fields['default_lot_size'].label = tr(self.language, 'form.preferences.default_lots', 'Quantite par defaut (lots)')
        self.fields['default_fees'].label = tr(self.language, 'form.preferences.default_gp', 'G/P par defaut')
        self.fields['default_confidence'].label = tr(self.language, 'form.preferences.default_confidence', 'Confiance par defaut')
        self.fields['default_dashboard_year'].label = tr(self.language, 'form.preferences.default_dashboard_year', 'Annee dashboard par defaut')
        self.fields['default_week_start_day'].label = tr(self.language, 'form.preferences.default_week_start_day', 'Premier jour de la semaine')
        self.fields['capital_base'].label = tr(self.language, 'form.preferences.active_initial_capital', 'Capital initial du compte actif')
        self.fields['currency'].label = tr(self.language, 'form.preferences.active_currency', 'Devise du compte actif')
        apply_choice_labels(
            self.fields['default_direction'],
            {
                Trade.Direction.LONG: tr(self.language, 'trade.direction.long', 'Long'),
                Trade.Direction.SHORT: tr(self.language, 'trade.direction.short', 'Short'),
            },
        )
        apply_choice_labels(
            self.fields['currency'],
            {
                'USD': tr(self.language, 'currency.usd', 'Dollar americain (USD)'),
                'EUR': tr(self.language, 'currency.eur', 'Euro (EUR)'),
                'GBP': tr(self.language, 'currency.gbp', 'Livre sterling (GBP)'),
                'CHF': tr(self.language, 'currency.chf', 'Franc suisse (CHF)'),
                'XAF': tr(self.language, 'currency.xaf', 'Franc CFA BEAC (XAF)'),
                'XOF': tr(self.language, 'currency.xof', 'Franc CFA BCEAO (XOF)'),
            },
        )
        apply_choice_labels(
            self.fields['default_week_start_day'],
            {
                calendar.MONDAY: tr(self.language, 'weekday.monday', 'Lundi'),
                calendar.TUESDAY: tr(self.language, 'weekday.tuesday', 'Mardi'),
                calendar.WEDNESDAY: tr(self.language, 'weekday.wednesday', 'Mercredi'),
                calendar.THURSDAY: tr(self.language, 'weekday.thursday', 'Jeudi'),
                calendar.FRIDAY: tr(self.language, 'weekday.friday', 'Vendredi'),
                calendar.SATURDAY: tr(self.language, 'weekday.saturday', 'Samedi'),
                calendar.SUNDAY: tr(self.language, 'weekday.sunday', 'Dimanche'),
            },
        )
        apply_choice_labels(
            self.fields['ui_language'],
            {
                'fr': tr(self.language, 'language.option.fr', 'Francais' if self.language == 'fr' else 'French'),
                'en': tr(self.language, 'language.option.en', 'Anglais' if self.language == 'fr' else 'English'),
            },
        )
        self.fields['default_symbol'].widget.attrs.update(
            {
                'placeholder': 'XAUUSD',
                'autocomplete': 'off',
            }
        )
        self.fields['ui_language'].widget.attrs.update(
            {
                'autocomplete': 'off',
            }
        )
        self.fields['default_setup'].widget.attrs.update(
            {
                'placeholder': 'Breakout London',
                'autocomplete': 'off',
            }
        )
        for field_name in ('default_lot_size', 'default_fees', 'capital_base'):
            self.fields[field_name].widget.attrs.setdefault('step', '0.01')
        self.fields['capital_base'].widget.attrs['min'] = '1'

    def clean_default_symbol(self):
        return self.cleaned_data['default_symbol'].upper().strip()

    def _build_dashboard_year_choices(self, active_account):
        current_year = timezone.localdate().year
        years = {current_year}
        trade_query = Trade.objects.filter(user=self.instance.user) if getattr(self.instance, 'user_id', None) else Trade.objects.none()
        if active_account:
            trade_query = trade_query.filter(models.Q(account=active_account) | models.Q(account__isnull=True))
        for executed_at in trade_query.values_list('executed_at', flat=True):
            years.add(timezone.localtime(executed_at).year)
        return [(year, str(year)) for year in sorted(years, reverse=True)]


class BaseTradingAccountForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.language = normalize_language(kwargs.pop('language', 'fr'))
        super().__init__(*args, **kwargs)
        apply_compact_decimal_widgets(self)
        remove_autofocus_from_fields(self)
        self.fields['name'].label = tr(self.language, 'form.account.name', 'Nom du compte')
        self.fields['broker'].label = tr(self.language, 'form.account.broker', 'Broker')
        self.fields['account_identifier'].label = tr(self.language, 'form.account.identifier', 'Numero / identifiant')
        self.fields['capital_base'].label = tr(self.language, 'form.account.initial_capital', 'Capital initial')
        self.fields['currency'].label = tr(self.language, 'form.account.currency', 'Devise')
        self.fields['name'].widget.attrs.update(
            {
                'placeholder': tr(self.language, 'form.account.name.placeholder', 'Ex: Compte principal, FTMO Swing, Prop Firm'),
                'autocomplete': 'off',
            }
        )
        self.fields['broker'].widget.attrs.update(
            {
                'placeholder': tr(self.language, 'form.account.broker.placeholder', 'Ex: IC Markets, FTMO, Exness'),
                'autocomplete': 'off',
            }
        )
        self.fields['account_identifier'].widget.attrs.update(
            {
                'placeholder': tr(self.language, 'form.account.identifier.placeholder', 'Ex: 50124587'),
                'autocomplete': 'off',
            }
        )
        apply_choice_labels(
            self.fields['currency'],
            {
                'USD': tr(self.language, 'currency.usd', 'Dollar americain (USD)'),
                'EUR': tr(self.language, 'currency.eur', 'Euro (EUR)'),
                'GBP': tr(self.language, 'currency.gbp', 'Livre sterling (GBP)'),
                'CHF': tr(self.language, 'currency.chf', 'Franc suisse (CHF)'),
                'XAF': tr(self.language, 'currency.xaf', 'Franc CFA BEAC (XAF)'),
                'XOF': tr(self.language, 'currency.xof', 'Franc CFA BCEAO (XOF)'),
            },
        )
        self.fields['capital_base'].widget.attrs.update(
            {
                'step': '0.01',
                'min': '1',
            }
        )

    def clean_name(self):
        return self.cleaned_data['name'].strip()


class TradingAccountForm(BaseTradingAccountForm):
    set_active = forms.BooleanField(
        required=False,
        initial=True,
        label='Definir ce compte comme actif a la creation',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['set_active'].label = tr(
            self.language,
            'form.account.set_active_on_create',
            'Definir ce compte comme actif a la creation',
        )

    class Meta:
        model = TradingAccount
        fields = ('name', 'broker', 'account_identifier', 'capital_base', 'currency')
        labels = {
            'name': 'Nom du compte',
            'broker': 'Broker',
            'account_identifier': 'Numero / identifiant',
            'capital_base': 'Capital initial',
            'currency': 'Devise',
        }


class TradingAccountEditForm(BaseTradingAccountForm):
    set_active = forms.BooleanField(
        required=False,
        initial=False,
        label='Definir ce compte comme actif apres la mise a jour',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['set_active'].label = tr(
            self.language,
            'form.account.set_active_on_update',
            'Definir ce compte comme actif apres la mise a jour',
        )

    class Meta:
        model = TradingAccount
        fields = ('name', 'broker', 'account_identifier', 'capital_base', 'currency')
        labels = {
            'name': 'Nom du compte',
            'broker': 'Broker',
            'account_identifier': 'Numero / identifiant',
            'capital_base': 'Capital initial',
            'currency': 'Devise',
        }


class TradingPasswordChangeForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        self.language = normalize_language(kwargs.pop('language', 'fr'))
        super().__init__(user, *args, **kwargs)
        remove_autofocus_from_fields(self)
        field_config = {
            'old_password': (
                tr(self.language, 'form.password.current', 'Mot de passe actuel'),
                tr(self.language, 'form.password.current.placeholder_change', 'Mot de passe actuel'),
            ),
            'new_password1': (
                tr(self.language, 'form.password.new', 'Nouveau mot de passe'),
                tr(self.language, 'form.password.new.placeholder_change', 'Saisissez le nouveau mot de passe'),
            ),
            'new_password2': (
                tr(self.language, 'form.password.confirmation', 'Confirmation'),
                tr(self.language, 'form.password.confirm.placeholder_change', 'Confirmez le nouveau mot de passe'),
            ),
        }
        for name, (label, placeholder) in field_config.items():
            self.fields[name].label = label
            self.fields[name].widget.attrs.update(
                {
                    'placeholder': placeholder,
                    'autocomplete': 'current-password' if name == 'old_password' else 'new-password',
                }
            )


class DeleteAccountForm(forms.Form):
    password = forms.CharField(
        label='Mot de passe',
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Confirmez votre mot de passe',
                'autocomplete': 'current-password',
            }
        ),
    )
    confirmation = forms.BooleanField(
        label='Je confirme la suppression definitive de mon compte et de l ensemble de mes donnees.',
        error_messages={
            'required': 'La confirmation de suppression est requise.',
        },
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        self.language = normalize_language(kwargs.pop('language', 'fr'))
        super().__init__(*args, **kwargs)
        remove_autofocus_from_fields(self)
        self.fields['password'].label = tr(self.language, 'form.password', 'Mot de passe')
        self.fields['password'].widget.attrs['placeholder'] = tr(
            self.language,
            'form.delete.password.placeholder',
            'Confirmez votre mot de passe',
        )
        self.fields['confirmation'].label = tr(
            self.language,
            'form.delete.confirmation',
            'Je confirme la suppression definitive de mon compte et de l ensemble de mes donnees.',
        )
        self.fields['confirmation'].error_messages['required'] = tr(
            self.language,
            'form.delete.confirmation_required',
            'La confirmation de suppression est requise.',
        )

    def clean_password(self):
        password = self.cleaned_data['password']
        if self.user is None or not self.user.check_password(password):
            raise forms.ValidationError(tr(self.language, 'form.delete.invalid_password', 'Le mot de passe saisi est incorrect.'))
        return password


class TradingDataExportForm(forms.Form):
    PERIOD_ALL_TIME = 'all_time'
    PERIOD_DAY = 'day'
    PERIOD_WEEK = 'week'
    PERIOD_MONTH = 'month'
    PERIOD_YEAR = 'year'

    period = forms.ChoiceField(
        label='Periode a exporter',
        choices=(
            (PERIOD_ALL_TIME, 'Tout le temps'),
            (PERIOD_DAY, 'Jour'),
            (PERIOD_WEEK, 'Semaine'),
            (PERIOD_MONTH, 'Mois'),
            (PERIOD_YEAR, 'Annee'),
        ),
        initial=PERIOD_ALL_TIME,
    )
    day = forms.DateField(
        required=False,
        label='Jour',
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    week = forms.CharField(
        required=False,
        label='Semaine',
        max_length=8,
        widget=forms.TextInput(attrs={'type': 'week'}),
    )
    month = forms.CharField(
        required=False,
        label='Mois',
        max_length=7,
        widget=forms.TextInput(attrs={'type': 'month'}),
    )
    year = forms.IntegerField(
        required=False,
        label='Annee',
        min_value=1900,
        max_value=9999,
        widget=forms.NumberInput(attrs={'inputmode': 'numeric', 'step': '1', 'min': '1900', 'max': '9999'}),
    )

    def __init__(self, *args, **kwargs):
        self.language = normalize_language(kwargs.pop('language', 'fr'))
        super().__init__(*args, **kwargs)
        remove_autofocus_from_fields(self)

        period_choices = (
            (self.PERIOD_ALL_TIME, tr(self.language, 'settings.export.period.all_time', 'Tout le temps')),
            (self.PERIOD_DAY, tr(self.language, 'settings.export.period.day', 'Jour')),
            (self.PERIOD_WEEK, tr(self.language, 'settings.export.period.week', 'Semaine')),
            (self.PERIOD_MONTH, tr(self.language, 'settings.export.period.month', 'Mois')),
            (self.PERIOD_YEAR, tr(self.language, 'settings.export.period.year', 'Annee')),
        )
        self.fields['period'].label = tr(self.language, 'settings.export.period_label', 'Periode a exporter')
        self.fields['period'].choices = period_choices
        self.fields['period'].widget.choices = period_choices
        self.fields['period'].widget.attrs.update(
            {
                'autocomplete': 'off',
                'data-export-period-select': 'true',
            }
        )
        self.fields['day'].label = tr(self.language, 'settings.export.day_label', 'Jour')
        self.fields['week'].label = tr(self.language, 'settings.export.week_label', 'Semaine')
        self.fields['month'].label = tr(self.language, 'settings.export.month_label', 'Mois')
        self.fields['year'].label = tr(self.language, 'settings.export.year_label', 'Annee')

        today = timezone.localdate()
        iso_year, iso_week, _ = today.isocalendar()
        if not self.is_bound:
            self.fields['day'].initial = today
            self.fields['week'].initial = f'{iso_year}-W{iso_week:02d}'
            self.fields['month'].initial = today.strftime('%Y-%m')
            self.fields['year'].initial = today.year

    def clean_week(self):
        week_value = (self.cleaned_data.get('week') or '').strip()
        if not week_value:
            return ''
        if not re.fullmatch(r'\d{4}-W\d{2}', week_value):
            raise forms.ValidationError(tr(self.language, 'settings.export.week_invalid', 'Selectionnez une semaine valide.'))
        return week_value

    def clean_month(self):
        month_value = (self.cleaned_data.get('month') or '').strip()
        if not month_value:
            return ''
        if not re.fullmatch(r'\d{4}-\d{2}', month_value):
            raise forms.ValidationError(tr(self.language, 'settings.export.month_invalid', 'Selectionnez un mois valide.'))
        return month_value

    def clean(self):
        cleaned_data = super().clean()
        period = cleaned_data.get('period') or self.PERIOD_ALL_TIME
        today = timezone.localdate()
        start_date = None
        end_date = None
        label = tr(self.language, 'settings.export.scope.all_time', 'Tout le temps')
        token = 'all-time'

        if period == self.PERIOD_DAY:
            selected_day = cleaned_data.get('day')
            if not selected_day:
                self.add_error('day', tr(self.language, 'settings.export.day_required', 'Choisissez un jour a exporter.'))
            else:
                start_date = selected_day
                end_date = selected_day
                label = selected_day.strftime('%d/%m/%Y')
                token = selected_day.isoformat()
        elif period == self.PERIOD_WEEK:
            week_value = cleaned_data.get('week')
            if not week_value:
                self.add_error('week', tr(self.language, 'settings.export.week_required', 'Choisissez une semaine a exporter.'))
            else:
                year_label, week_label = week_value.split('-W', 1)
                try:
                    start_date = date.fromisocalendar(int(year_label), int(week_label), 1)
                except ValueError:
                    self.add_error('week', tr(self.language, 'settings.export.week_invalid', 'Selectionnez une semaine valide.'))
                else:
                    end_date = start_date + timedelta(days=6)
                    label = (
                        tr(
                            self.language,
                            'settings.export.scope.week',
                            'Semaine du {start} au {end}',
                        ).format(
                            start=start_date.strftime('%d/%m/%Y'),
                            end=end_date.strftime('%d/%m/%Y'),
                        )
                    )
                    token = week_value
        elif period == self.PERIOD_MONTH:
            month_value = cleaned_data.get('month')
            if not month_value:
                self.add_error('month', tr(self.language, 'settings.export.month_required', 'Choisissez un mois a exporter.'))
            else:
                year_label, month_label = month_value.split('-', 1)
                try:
                    start_date = date(int(year_label), int(month_label), 1)
                except ValueError:
                    self.add_error('month', tr(self.language, 'settings.export.month_invalid', 'Selectionnez un mois valide.'))
                else:
                    if start_date.month == 12:
                        end_date = date(start_date.year + 1, 1, 1) - timedelta(days=1)
                    else:
                        end_date = date(start_date.year, start_date.month + 1, 1) - timedelta(days=1)
                    label = start_date.strftime('%m/%Y')
                    token = month_value
        elif period == self.PERIOD_YEAR:
            selected_year = cleaned_data.get('year')
            if not selected_year:
                self.add_error('year', tr(self.language, 'settings.export.year_required', 'Choisissez une annee a exporter.'))
            else:
                start_date = date(int(selected_year), 1, 1)
                end_date = date(int(selected_year), 12, 31)
                label = str(selected_year)
                token = str(selected_year)
        else:
            cleaned_data['period'] = self.PERIOD_ALL_TIME
            cleaned_data.setdefault('day', today)

        if self.errors:
            return cleaned_data

        cleaned_data['scope'] = {
            'period': cleaned_data.get('period') or self.PERIOD_ALL_TIME,
            'label': label,
            'start_date': start_date,
            'end_date': end_date,
            'filename_token': token,
        }
        return cleaned_data

    def get_scope(self):
        return self.cleaned_data['scope']


class CapitalMovementForm(forms.ModelForm):
    occurred_at = forms.DateTimeField(
        label="Date et heure",
        input_formats=[
            '%Y-%m-%dT%H:%M',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d %H:%M:%S',
        ],
    )

    class Meta:
        model = CapitalMovement
        fields = ('kind', 'occurred_at', 'amount', 'note')

    def __init__(self, *args, **kwargs):
        self.language = normalize_language(kwargs.pop('language', 'fr'))
        super().__init__(*args, **kwargs)
        apply_compact_decimal_widgets(self)
        self.fields['amount'].widget.attrs.update(
            {
                'step': '0.01',
                'min': '0.01',
                'placeholder': '500',
            }
        )
        self.fields['note'].widget.attrs.update(
            {
                'placeholder': tr(
                    self.language,
                    'form.movement.note.placeholder',
                    'Ex: retrait mensuel, apport de capital, ajustement de compte...',
                ),
                'autocomplete': 'off',
            }
        )

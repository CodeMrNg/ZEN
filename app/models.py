import calendar
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

CURRENCY_SYMBOLS = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'CHF': 'CHF ',
    'XAF': 'FCFA ',
    'XOF': 'CFA ',
}


def add_calendar_months(value, months=1):
    month_index = (value.month - 1) + months
    year = value.year + (month_index // 12)
    month = (month_index % 12) + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


def current_local_year():
    return timezone.localdate().year


class Trade(models.Model):
    class Direction(models.TextChoices):
        LONG = 'LONG', 'Long'
        SHORT = 'SHORT', 'Short'

    class Result(models.TextChoices):
        TAKE_PROFIT = 'TAKE_PROFIT', 'Take profit'
        GAIN = 'GAIN', 'Gain'
        BREAK_EVEN = 'BREAK_EVEN', 'Break even'
        STOP_LOSS = 'STOP_LOSS', 'Stoploss'
        LOSS = 'LOSS', 'Perte'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trades',
    )
    account = models.ForeignKey(
        'TradingAccount',
        on_delete=models.CASCADE,
        related_name='trades',
        null=True,
        blank=True,
    )
    executed_at = models.DateTimeField("Date d'execution")
    symbol = models.CharField(max_length=20)
    market = models.CharField(max_length=40, blank=True)
    direction = models.CharField(
        max_length=5,
        choices=Direction.choices,
        default=Direction.LONG,
    )
    result = models.CharField(
        max_length=12,
        choices=Result.choices,
        blank=True,
    )
    setup = models.CharField(max_length=80)
    entry_price = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
    )
    rr_ratio = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('-20.00')), MaxValueValidator(Decimal('20.00'))],
    )
    exit_price = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        validators=[MinValueValidator(Decimal('0.0001'))],
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    lot_size = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    gp_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    risk_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    risk_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
    )
    capital_base = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('10000.00'),
        validators=[MinValueValidator(Decimal('1.00'))],
    )
    screenshot = models.ImageField(
        upload_to='trades/screenshots/',
        blank=True,
        null=True,
    )
    confidence = models.PositiveSmallIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-executed_at', '-created_at')

    def __str__(self):
        return f'{self.symbol} {self.get_direction_display()} {self.executed_at:%Y-%m-%d %H:%M}'

    @property
    def gross_pnl(self):
        if self.result == self.Result.BREAK_EVEN and self.gp_value is not None:
            return self.gp_value
        if self.rr_ratio is not None and self.risk_amount is not None:
            return self.risk_amount * self.rr_ratio
        price_delta = self.exit_price - self.entry_price
        direction_multiplier = Decimal('1') if self.direction == self.Direction.LONG else Decimal('-1')
        return (price_delta * self.quantity) * direction_multiplier

    @property
    def net_pnl(self):
        return self.gross_pnl - self.fees

    @property
    def risk_reward(self):
        if self.rr_ratio is not None:
            return self.rr_ratio
        if not self.risk_amount:
            return None
        if self.risk_amount == 0:
            return None
        return self.net_pnl / self.risk_amount

    @property
    def is_win(self):
        return self.net_pnl > 0

    @property
    def is_loss(self):
        return self.net_pnl < 0

    @property
    def resolved_result(self):
        if self.result:
            return self.result
        if self.rr_ratio is None:
            if self.net_pnl > 0:
                return self.Result.GAIN
            if self.net_pnl < 0:
                return self.Result.LOSS
            return self.Result.BREAK_EVEN
        if self.rr_ratio > 0:
            return self.Result.TAKE_PROFIT
        if self.rr_ratio < 0:
            return self.Result.STOP_LOSS
        return self.Result.BREAK_EVEN

    @property
    def resolved_result_label(self):
        resolved = self.resolved_result
        if not resolved:
            return '--'
        return self.Result(resolved).label

    @property
    def screenshot_gallery_urls(self):
        urls = []
        if self.screenshot:
            urls.append(self.screenshot.url)
        urls.extend(
            screenshot.image.url
            for screenshot in self.screenshots.all()
            if screenshot.image
        )
        return urls

    @property
    def primary_screenshot_url(self):
        gallery_urls = self.screenshot_gallery_urls
        return gallery_urls[0] if gallery_urls else None


class TradeScreenshot(models.Model):
    trade = models.ForeignKey(
        Trade,
        on_delete=models.CASCADE,
        related_name='screenshots',
    )
    image = models.ImageField(upload_to='trades/screenshots/')
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('sort_order', 'pk')
        verbose_name = 'Image de trade'
        verbose_name_plural = 'Images de trade'

    def __str__(self):
        return f'Image trade #{self.trade_id} ({self.sort_order})'


class TradingPreference(models.Model):
    class Currency(models.TextChoices):
        USD = 'USD', 'Dollar americain (USD)'
        EUR = 'EUR', 'Euro (EUR)'
        GBP = 'GBP', 'Livre sterling (GBP)'
        CHF = 'CHF', 'Franc suisse (CHF)'
        XAF = 'XAF', 'Franc CFA BEAC (XAF)'
        XOF = 'XOF', 'Franc CFA BCEAO (XOF)'

    class WeekStartDay(models.IntegerChoices):
        MONDAY = calendar.MONDAY, 'Monday'
        TUESDAY = calendar.TUESDAY, 'Tuesday'
        WEDNESDAY = calendar.WEDNESDAY, 'Wednesday'
        THURSDAY = calendar.THURSDAY, 'Thursday'
        FRIDAY = calendar.FRIDAY, 'Friday'
        SATURDAY = calendar.SATURDAY, 'Saturday'
        SUNDAY = calendar.SUNDAY, 'Sunday'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trading_preferences',
    )
    active_account = models.ForeignKey(
        'TradingAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='active_for_preferences',
    )
    default_symbol = models.CharField(max_length=20, default='XAUUSD')
    default_direction = models.CharField(
        max_length=5,
        choices=Trade.Direction.choices,
        default=Trade.Direction.LONG,
    )
    default_setup = models.CharField(max_length=80, default='Breakout London')
    default_lot_size = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('1.00'),
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    default_risk_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.00'),
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('100.00'))],
    )
    default_fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
    )
    default_confidence = models.PositiveSmallIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    capital_base = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('10000.00'),
        validators=[MinValueValidator(Decimal('1.00'))],
    )
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.USD,
    )
    ui_language = models.CharField(
        max_length=12,
        choices=settings.LANGUAGES,
        default='fr',
    )
    default_dashboard_year = models.PositiveSmallIntegerField(default=current_local_year)
    default_week_start_day = models.PositiveSmallIntegerField(
        choices=WeekStartDay.choices,
        default=calendar.SUNDAY,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Preferences {self.user}'

    @property
    def currency_symbol(self):
        return CURRENCY_SYMBOLS.get(self.currency, f'{self.currency} ')


class TradingAccount(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trading_accounts',
    )
    name = models.CharField(max_length=80, default='Compte principal')
    broker = models.CharField(max_length=80, blank=True)
    account_identifier = models.CharField(max_length=80, blank=True)
    capital_base = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('10000.00'),
        validators=[MinValueValidator(Decimal('1.00'))],
    )
    currency = models.CharField(
        max_length=3,
        choices=TradingPreference.Currency.choices,
        default=TradingPreference.Currency.USD,
    )
    archived_at = models.DateTimeField(
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created_at', 'pk')

    def __str__(self):
        broker_label = f' | {self.broker}' if self.broker else ''
        return f'{self.name}{broker_label}'

    @property
    def currency_symbol(self):
        return CURRENCY_SYMBOLS.get(self.currency, f'{self.currency} ')

    @property
    def is_archived(self):
        return self.archived_at is not None


class CapitalMovement(models.Model):
    class Kind(models.TextChoices):
        DEPOSIT = 'DEPOSIT', 'Depot'
        WITHDRAWAL = 'WITHDRAWAL', 'Retrait'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='capital_movements',
    )
    account = models.ForeignKey(
        'TradingAccount',
        on_delete=models.CASCADE,
        related_name='capital_movements',
        null=True,
        blank=True,
    )
    kind = models.CharField(
        max_length=10,
        choices=Kind.choices,
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    occurred_at = models.DateTimeField("Date d'execution")
    note = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-occurred_at', '-created_at')

    def __str__(self):
        return f'{self.get_kind_display()} {self.amount:,.2f} {self.occurred_at:%Y-%m-%d %H:%M}'


class ServerRefreshStatus(models.Model):
    is_enabled = models.BooleanField(default=True)
    last_refreshed_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Suivi actualisation serveur'
        verbose_name_plural = 'Suivi actualisation serveur'

    def save(self, *args, **kwargs):
        if not self.pk:
            self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return 'Suivi actualisation serveur'

    @property
    def next_refresh_due_at(self):
        return add_calendar_months(self.last_refreshed_at, months=1)

    @property
    def is_overdue(self):
        return self.is_enabled and timezone.now() >= self.next_refresh_due_at


class SocialLink(models.Model):
    class Platform(models.TextChoices):
        WEBSITE = 'WEBSITE', 'Website'
        X = 'X', 'X'
        INSTAGRAM = 'INSTAGRAM', 'Instagram'
        WHATSAPP = 'WHATSAPP', 'WhatsApp'
        TELEGRAM = 'TELEGRAM', 'Telegram'
        YOUTUBE = 'YOUTUBE', 'YouTube'
        LINKEDIN = 'LINKEDIN', 'LinkedIn'
        FACEBOOK = 'FACEBOOK', 'Facebook'
        DISCORD = 'DISCORD', 'Discord'
        GITHUB = 'GITHUB', 'GitHub'
        TIKTOK = 'TIKTOK', 'TikTok'

    label = models.CharField(max_length=60, blank=True)
    platform = models.CharField(max_length=20, choices=Platform.choices)
    url = models.URLField(max_length=300)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('sort_order', 'pk')
        verbose_name = 'Lien social'
        verbose_name_plural = 'Liens sociaux'

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        return self.label or self.get_platform_display()

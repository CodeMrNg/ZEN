from decimal import Decimal, InvalidOperation


def parse_decimal(value):
    if value in (None, ""):
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value).replace(",", "."))
    except (InvalidOperation, ValueError, TypeError):
        return None


def format_decimal_compact(value, decimal_places=2, use_grouping=False, trim_trailing_zeroes=False):
    decimal_value = parse_decimal(value)
    if decimal_value is None:
        return "" if value in (None, "") else str(value)

    if decimal_places <= 0:
        return format(decimal_value, "," if use_grouping else "f").split(".")[0]

    format_spec = f",.{decimal_places}f" if use_grouping else f".{decimal_places}f"
    formatted = format(decimal_value, format_spec)
    if trim_trailing_zeroes and "." in formatted:
        return formatted.rstrip("0").rstrip(".")
    zero_suffix = "." + ("0" * decimal_places)
    if formatted.endswith(zero_suffix):
        return formatted[: -len(zero_suffix)]
    return formatted


def format_decimal_thousands_compact(value, decimal_places=2, use_grouping_below_threshold=True):
    decimal_value = parse_decimal(value)
    if decimal_value is None:
        return "" if value in (None, "") else str(value)

    sign = "-" if decimal_value < 0 else ""
    absolute_value = abs(decimal_value)

    if absolute_value >= Decimal("1000"):
        compact_value = absolute_value / Decimal("1000")
        compact_label = format_decimal_compact(
            compact_value,
            decimal_places=decimal_places,
            use_grouping=False,
            trim_trailing_zeroes=True,
        )
        return f"{sign}{compact_label}k"

    standard_label = format_decimal_compact(
        absolute_value,
        decimal_places=decimal_places,
        use_grouping=use_grouping_below_threshold,
    )
    return f"{sign}{standard_label}"

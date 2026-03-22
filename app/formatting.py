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


def format_decimal_compact(value, decimal_places=2, use_grouping=False):
    decimal_value = parse_decimal(value)
    if decimal_value is None:
        return "" if value in (None, "") else str(value)

    if decimal_places <= 0:
        return format(decimal_value, "," if use_grouping else "f").split(".")[0]

    format_spec = f",.{decimal_places}f" if use_grouping else f".{decimal_places}f"
    formatted = format(decimal_value, format_spec)
    zero_suffix = "." + ("0" * decimal_places)
    if formatted.endswith(zero_suffix):
        return formatted[: -len(zero_suffix)]
    return formatted

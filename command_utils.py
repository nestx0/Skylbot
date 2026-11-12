"""Shared parsing for all/max amounts and inventory selections."""

MAX_ALIASES = frozenset({"all", "max"})


def parse_amount(value: str | int, available: int, *, allow_allin: bool = False) -> int:
    """Resolve an amount; 'allin' is only accepted when betting."""
    token = str(value).strip().lower()
    if token in MAX_ALIASES or (allow_allin and token == "allin"):
        return available
    try:
        return int(token)
    except (ValueError, TypeError) as exc:
        options = "a number, 'all' or 'max'"
        if allow_allin:
            options += ", or 'allin'"
        raise ValueError(f"Please enter {options}.") from exc


def parse_positions(text: str, inventory_length: int) -> tuple[list[int], bool]:
    """Unique sorted 1-based slots; second result is True for all/max."""
    parts = text.strip().split()
    if not parts:
        raise ValueError("Choose at least one inventory slot.")
    if len(parts) == 1 and parts[0].lower() in MAX_ALIASES:
        return list(range(1, inventory_length + 1)), True
    try:
        positions = sorted({int(part) for part in parts})
    except ValueError as exc:
        raise ValueError("Enter slot numbers separated by spaces, or 'all'/'max'.") from exc
    if not positions or positions[0] < 1 or positions[-1] > inventory_length:
        raise ValueError(f"Invalid position. Choose between 1 and {inventory_length}.")
    return positions, False

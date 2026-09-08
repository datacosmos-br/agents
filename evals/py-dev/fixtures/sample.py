def append_value(value: str, values: list[str] | None = None) -> list[str]:
    if values is None:
        values = []
    values.append(value)
    return values

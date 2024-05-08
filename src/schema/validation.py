def basic_string_validation(_string: str, variable: str) -> str:
    value = _string.strip()
    if value == "":
        raise ValueError(f"{variable} cannot be empty")

    return value

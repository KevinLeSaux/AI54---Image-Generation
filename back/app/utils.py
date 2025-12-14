def payload_validator(payload: dict, required_fields: dict) -> list:
    """
    This function validates the input payload against the required fields and their expected types.

    param payload: The input JSON payload to validate.
    param required_fields: A dictionary mapping field names to their expected types.

    return: A list of error messages for missing or invalid fields.
    """

    errors = []

    # Check for missing fields
    missing = [name for name in required_fields if name not in payload]
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")

    # Check for invalid types
    invalid = [
        name
        for name, expected in required_fields.items()
        if name in payload and not isinstance(payload[name], expected)
    ]
    if invalid:
        errors.append(f"invalid types: {', '.join(invalid)}")

    return errors
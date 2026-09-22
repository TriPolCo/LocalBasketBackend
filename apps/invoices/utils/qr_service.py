import secrets


def generate_qr_token():
    """
    Generates a cryptographically secure random token.
    """

    return secrets.token_urlsafe(32)
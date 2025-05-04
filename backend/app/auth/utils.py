import base64
import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import jwt
import requests
from app.config import settings
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def generate_state() -> str:
    """Generate a random state string for CSRF protection

    Returns:
        A URL-safe random string
    """
    return secrets.token_urlsafe(32)


def generate_nonce() -> str:
    """Generate a random nonce for PKCE

    Returns:
        A URL-safe random string
    """
    return secrets.token_urlsafe(16)


def encrypt_refresh_token(refresh_token: str) -> Tuple[str, str, str]:
    """
    Encrypt a refresh token using AES-256-GCM

    Args:
        refresh_token: The refresh token to encrypt

    Returns:
        Tuple of (encrypted_token, iv, tag)
    """
    # Decode the base64 encryption key
    key = base64.b64decode(settings.ENCRYPTION_KEY)

    # Generate a random initialization vector
    iv = os.urandom(12)  # 96 bits for GCM

    # Create AESGCM cipher
    cipher = AESGCM(key)

    # Encrypt the token
    token_bytes = refresh_token.encode("utf-8")
    encrypted_token = cipher.encrypt(iv, token_bytes, None)

    # The tag is appended to the ciphertext by encrypt()
    # For storage, we'll separate it
    ciphertext = encrypted_token[:-16]
    tag = encrypted_token[-16:]

    # Return base64 encoded values for storage
    return (
        base64.b64encode(ciphertext).decode("utf-8"),
        base64.b64encode(iv).decode("utf-8"),
        base64.b64encode(tag).decode("utf-8"),
    )


def decrypt_refresh_token(encrypted_token: str, iv: str, tag: str) -> str:
    """
    Decrypt a refresh token encrypted with AES-256-GCM

    Args:
        encrypted_token: The encrypted token (base64 encoded)
        iv: The initialization vector (base64 encoded)
        tag: The authentication tag (base64 encoded)

    Returns:
        The decrypted refresh token
    """
    # Decode the base64 values
    key = base64.b64decode(settings.ENCRYPTION_KEY)
    encrypted_data = base64.b64decode(encrypted_token)
    iv_bytes = base64.b64decode(iv)
    tag_bytes = base64.b64decode(tag)

    # Recreate the ciphertext with appended tag
    ciphertext_with_tag = encrypted_data + tag_bytes

    # Create AESGCM cipher
    cipher = AESGCM(key)

    # Decrypt
    decrypted_token = cipher.decrypt(iv_bytes, ciphertext_with_tag, None)

    return decrypted_token.decode("utf-8")


def verify_id_token(id_token: str) -> Dict:
    """
    Verify a Google ID token using Google's public keys

    Args:
        id_token: The ID token to verify

    Returns:
        The decoded token payload if valid

    Raises:
        ValueError: If token is invalid
    """
    # Fetch Google's public keys
    response = requests.get(settings.GOOGLE_CERTS_URL)
    keys = response.json()

    # Get the token header to determine which key to use
    header = jwt.get_unverified_header(id_token)
    kid = header.get("kid")

    if not kid or kid not in keys:
        raise ValueError("Invalid token: no matching key found")

    # Get the public key
    public_key = keys[kid]

    # Verify and decode the token
    payload = jwt.decode(
        id_token,
        public_key,
        algorithms=["RS256"],
        audience=settings.GOOGLE_CLIENT_ID,
        options={"verify_exp": True},
    )

    return payload


def create_auth_cookies(
    session_token: str, refresh_token: Optional[str] = None
) -> Dict:
    """
    Create secure cookies for session and refresh tokens

    Args:
        session_token: JWT session token
        refresh_token: Optional refresh token

    Returns:
        Dictionary with cookie settings
    """
    # Common cookie parameters
    cookies = {}
    common_params = {
        "httponly": True,
        "secure": settings.COOKIE_SECURE,
        "samesite": settings.COOKIE_SAMESITE,
        "domain": settings.COOKIE_DOMAIN,
        "path": "/",
    }

    # Session token cookie (short-lived)
    cookies["session_token"] = {
        "key": "session_token",
        "value": session_token,
        # No max_age - this is a session cookie that expires when browser closes
        **common_params,
    }

    # Refresh token cookie (long-lived, if provided)
    if refresh_token:
        expires = datetime.utcnow() + timedelta(days=30)
        cookies["refresh_token"] = {
            "key": "refresh_token",
            "value": refresh_token,
            "max_age": settings.COOKIE_MAX_AGE,
            "expires": expires,
            **common_params,
        }

    return cookies

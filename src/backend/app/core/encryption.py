"""
Encryption utilities for storing sensitive data (API keys) at rest.

Uses AES-256-GCM via the cryptography library with the ENCRYPTION_KEY
environment variable. Falls back to a derived key from SECRET_KEY
if ENCRYPTION_KEY is not set.
"""

import base64
import os
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _get_encryption_key_bytes() -> bytes:
    """Resolve the encryption key to 32 bytes for AES-256."""
    # Prefer ENCRYPTION_KEY, fall back to SECRET_KEY
    raw = os.environ.get("ENCRYPTION_KEY") or os.environ.get("SECRET_KEY", "")
    if not raw:
        raise RuntimeError(
            "Neither ENCRYPTION_KEY nor SECRET_KEY is set. "
            "Cannot encrypt/decrypt API keys."
        )
    # Derive a fixed-length 32-byte key using SHA-256
    import hashlib
    return hashlib.sha256(raw.encode()).digest()


def encrypt(plaintext: str) -> str:
    """Encrypt a string and return base64-encoded ciphertext+nonce.

    Format: base64(nonce || ciphertext) — nonce is 12 bytes prepended.
    """
    key = _get_encryption_key_bytes()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ct).decode("ascii")


def decrypt(encrypted: str) -> str:
    """Decrypt a base64-encoded ciphertext+nonce back to plaintext."""
    key = _get_encryption_key_bytes()
    raw = base64.b64decode(encrypted)
    nonce = raw[:12]
    ct = raw[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, None).decode("utf-8")


def mask_key(api_key: str) -> str:
    """Return a masked version of an API key for display.

    e.g. 'sk-abc...3f2x' or 'AI...xyz' for short keys.
    """
    if len(api_key) <= 8:
        return "***"
    return f"{api_key[:4]}...{api_key[-4:]}"
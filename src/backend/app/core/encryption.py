"""
Encryption utilities for storing sensitive data (API keys) at rest.

Uses AES-256-GCM via the cryptography library.

Key resolution order:
  1. ENCRYPTION_KEY env var (preferred — set in Render/Vercel)
  2. SECRET_KEY env var (fallback — same key used for JWT signing)
  3. Auto-generated key persisted to .encryption_key file (dev only)

For production: always set a dedicated ENCRYPTION_KEY.
"""

import base64
import hashlib
import logging
import os
from pathlib import Path
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger(__name__)

# Auto-generated key file path (dev fallback only)
_KEY_FILE = Path(__file__).parent.parent.parent.parent / ".encryption_key"


def _get_encryption_key_bytes() -> bytes:
    """Resolve the encryption key to 32 bytes for AES-256.

    Resolution order:
      1. ENCRYPTION_KEY env var
      2. SECRET_KEY env var
      3. Auto-generated key in .encryption_key file (created on first run)

    The auto-generated key is for development convenience only.
    In production, always set a dedicated ENCRYPTION_KEY.
    """
    raw = os.environ.get("ENCRYPTION_KEY") or os.environ.get("SECRET_KEY", "")

    if not raw:
        # Dev fallback: auto-generate and persist a key
        raw = _get_or_create_auto_key()

    # Derive a fixed-length 32-byte key using SHA-256
    return hashlib.sha256(raw.encode()).digest()


def _get_or_create_auto_key() -> str:
    """Get or create an auto-generated encryption key file (dev only).

    This ensures development works without any env vars set.
    The key is stored in .encryption_key at the project root.
    This file should NEVER be committed to git.
    """
    if _KEY_FILE.exists():
        key = _KEY_FILE.read_text().strip()
        if key:
            return key

    # Generate a cryptographically secure key
    key = base64.urlsafe_b64encode(os.urandom(32)).decode("ascii")
    _KEY_FILE.write_text(key)

    # Ensure it's in .gitignore
    gitignore = _KEY_FILE.parent / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if ".encryption_key" not in content:
            gitignore.write_text(content.rstrip() + "\n.encryption_key\n")

    logger.warning(
        "Auto-generated ENCRYPTION_KEY at %s (dev only). "
        "Set ENCRYPTION_KEY env var in production.",
        _KEY_FILE,
    )
    return key


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
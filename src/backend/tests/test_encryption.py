"""
Tests for encryption utilities (app.core.encryption).
"""

import os
import pytest

from app.core.encryption import encrypt, decrypt, mask_key


class TestEncryption:
    """AES-256-GCM encrypt/decrypt round-trip tests."""

    def setup_method(self):
        """Ensure a consistent encryption key is set."""
        self._original = os.environ.get("ENCRYPTION_KEY")
        os.environ["ENCRYPTION_KEY"] = "test-encryption-key-for-unit-tests-32b"

    def teardown_method(self):
        """Restore original env."""
        if self._original is not None:
            os.environ["ENCRYPTION_KEY"] = self._original
        else:
            os.environ.pop("ENCRYPTION_KEY", None)

    def test_encrypt_decrypt_round_trip(self):
        """Encrypting then decrypting returns the original plaintext."""
        plaintext = "sk-test-api-key-12345"
        encrypted = encrypt(plaintext)
        assert encrypted != plaintext
        assert decrypt(encrypted) == plaintext

    def test_encrypt_produces_different_ciphertext(self):
        """Each encryption uses a random nonce, so ciphertext differs."""
        plaintext = "same-input"
        e1 = encrypt(plaintext)
        e2 = encrypt(plaintext)
        assert e1 != e2  # different nonces → different ciphertext

    def test_decrypt_both_nonces(self):
        """Both ciphertexts decrypt to the same plaintext."""
        plaintext = "same-input"
        assert decrypt(encrypt(plaintext)) == plaintext
        assert decrypt(encrypt(plaintext)) == plaintext

    def test_encrypt_empty_string(self):
        """Encrypting an empty string works."""
        encrypted = encrypt("")
        assert decrypt(encrypted) == ""

    def test_encrypt_unicode(self):
        """Encrypting unicode characters works."""
        plaintext = "🔑 APIキー 🚀"
        encrypted = encrypt(plaintext)
        assert decrypt(encrypted) == plaintext

    def test_encrypt_long_key(self):
        """Encrypting a long API key works."""
        plaintext = "sk-" + "a" * 200
        encrypted = encrypt(plaintext)
        assert decrypt(encrypted) == plaintext

    def test_no_encryption_key_raises(self):
        """Without ENCRYPTION_KEY or SECRET_KEY, encryption should raise."""
        os.environ.pop("ENCRYPTION_KEY", None)
        os.environ.pop("SECRET_KEY", None)
        with pytest.raises(RuntimeError, match="Neither ENCRYPTION_KEY nor SECRET_KEY"):
            encrypt("test")

    def test_fallback_to_secret_key(self):
        """Falls back to SECRET_KEY when ENCRYPTION_KEY is not set."""
        os.environ.pop("ENCRYPTION_KEY", None)
        os.environ["SECRET_KEY"] = "fallback-secret-key-for-test"
        encrypted = encrypt("test-with-secret-key")
        assert decrypt(encrypted) == "test-with-secret-key"

    def test_decrypt_wrong_key_fails(self):
        """Decrypting with a different key raises an error."""
        os.environ["ENCRYPTION_KEY"] = "key-1-for-test"
        encrypted = encrypt("secret")

        os.environ["ENCRYPTION_KEY"] = "key-2-different"
        with pytest.raises(Exception):
            decrypt(encrypted)


class TestMaskKey:
    """Test API key masking for display."""

    def test_mask_long_key(self):
        """Long keys show first 4 and last 4 chars."""
        assert mask_key("sk-abc12345678xyz") == "sk-a...8xyz"

    def test_mask_short_key(self):
        """Keys ≤8 chars are fully masked."""
        assert mask_key("short12") == "***"

    def test_mask_8_char_key(self):
        """8-char keys are fully masked."""
        assert mask_key("12345678") == "***"

    def test_mask_9_char_key(self):
        """9-char keys show first/last 4."""
        assert mask_key("123456789") == "1234...6789"

    def test_mask_google_key(self):
        """Typical Google API key format."""
        key = "AIzaSyD1234567890abcdefghijklmnop"
        assert mask_key(key) == "AIza...mnop"
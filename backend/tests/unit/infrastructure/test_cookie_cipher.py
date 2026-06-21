import base64
import pytest

from infrastructure.encryption.cookie_cipher import encrypt, decrypt


def test_encrypt_decrypt_roundtrip():
    plaintext = '[{"name": "session_id", "value": "abc123"}]'
    assert decrypt(encrypt(plaintext)) == plaintext


def test_different_ciphertext_each_call():
    plaintext = "same-data"
    assert encrypt(plaintext) != encrypt(plaintext)


def test_decrypt_fails_on_tampered_data():
    from cryptography.exceptions import InvalidTag
    token = encrypt("secret")
    raw = base64.b64decode(token)
    tampered = base64.b64encode(raw[:-1] + bytes([raw[-1] ^ 0xFF])).decode()
    with pytest.raises(InvalidTag):
        decrypt(tampered)


def test_invalid_key_length_raises():
    from unittest.mock import patch, MagicMock
    import infrastructure.encryption.cookie_cipher as cipher_module
    short_key = base64.b64encode(b"short").decode()
    mock_settings = MagicMock()
    mock_settings.cookie_encryption_key = short_key
    with patch.object(cipher_module, "settings", mock_settings):
        with pytest.raises(ValueError, match="32 bytes"):
            cipher_module.encrypt("data")

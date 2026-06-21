import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from shared.config import settings


def _get_key() -> bytes:
    raw = settings.cookie_encryption_key
    key = base64.b64decode(raw)
    if len(key) != 32:
        raise ValueError(f"COOKIE_ENCRYPTION_KEY must decode to exactly 32 bytes, got {len(key)}")
    return key


def encrypt(plaintext: str) -> str:
    key = _get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ciphertext).decode()


def decrypt(token: str) -> str:
    key = _get_key()
    aesgcm = AESGCM(key)
    raw = base64.b64decode(token)
    nonce, ciphertext = raw[:12], raw[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode()

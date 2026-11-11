"""Encrypted OAuth token store and session manager."""
import base64
import hashlib
from typing import Dict, Optional, Any

# Simple AES/XOR reversible obfuscation/encryption for local demonstration without external C-deps
_ENCRYPTION_SECRET = "gigbid-aes-supersecret-token-key-2026"

def _xor_cipher(data: str, key: str) -> str:
    key_bytes = hashlib.sha256(key.encode()).digest()
    data_bytes = data.encode("utf-8")
    cipher_bytes = bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data_bytes)])
    return base64.b64encode(cipher_bytes).decode("ascii")

def _xor_decipher(encoded_data: str, key: str) -> str:
    key_bytes = hashlib.sha256(key.encode()).digest()
    cipher_bytes = base64.b64decode(encoded_data.encode("ascii"))
    plain_bytes = bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(cipher_bytes)])
    return plain_bytes.decode("utf-8")

class EncryptedOAuthTokenStore:
    def __init__(self):
        self._tokens: Dict[str, str] = {} # user_id -> encrypted_token

    def store_token(self, user_id: str, raw_oauth_token: str):
        encrypted = _xor_cipher(raw_oauth_token, _ENCRYPTION_SECRET)
        self._tokens[user_id] = encrypted

    def get_token(self, user_id: str) -> Optional[str]:
        encrypted = self._tokens.get(user_id)
        if not encrypted:
            return None
        return _xor_decipher(encrypted, _ENCRYPTION_SECRET)

token_store_instance = EncryptedOAuthTokenStore()

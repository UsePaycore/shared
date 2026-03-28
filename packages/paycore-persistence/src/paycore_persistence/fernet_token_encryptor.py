import os

from cryptography.fernet import Fernet

from paycore_domain.ports import TokenEncryptor


class FernetTokenEncryptor(TokenEncryptor):
    def __init__(self, encryption_key: str | None = None) -> None:
        key = encryption_key or os.getenv("OAUTH_ENCRYPTION_KEY")
        if not key:
            raise ValueError("OAUTH_ENCRYPTION_KEY is required")
        self._fernet = Fernet(key.encode())

    def encrypt(self, token: str) -> str:
        return self._fernet.encrypt(token.encode()).decode()

    def decrypt(self, encrypted_token: str) -> str:
        return self._fernet.decrypt(encrypted_token.encode()).decode()

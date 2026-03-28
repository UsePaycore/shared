import base64
import hashlib

from cryptography.fernet import Fernet

from paycore_domain.ports import PiiEncryptionService


class FernetPiiEncryptionService(PiiEncryptionService):
    def __init__(self, encryption_key: str) -> None:
        key = hashlib.sha256(encryption_key.encode()).digest()
        self._fernet = Fernet(base64.urlsafe_b64encode(key))

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self._fernet.decrypt(ciphertext.encode()).decode()

from abc import ABC, abstractmethod


class PiiEncryptionService(ABC):
    @abstractmethod
    def encrypt(self, plaintext: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def decrypt(self, ciphertext: str) -> str:
        raise NotImplementedError

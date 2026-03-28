from abc import ABC, abstractmethod


class TokenEncryptor(ABC):
    @abstractmethod
    def encrypt(self, token: str) -> str:
        pass

    @abstractmethod
    def decrypt(self, encrypted_token: str) -> str:
        pass

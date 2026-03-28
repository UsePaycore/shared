import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RabbitMqConfig:
    host: str
    port: int
    user: str
    password: str
    vhost: str = "/"

    @classmethod
    def from_env(cls, prefix: str = "RABBITMQ") -> "RabbitMqConfig":
        environment = os.getenv("ENVIRONMENT", "development")

        user = os.getenv(f"{prefix}_USER", "")
        password = os.getenv(f"{prefix}_PASSWORD", "")

        if environment == "production" and (not user or not password):
            raise ValueError(
                f"{prefix}_USER and {prefix}_PASSWORD environment variables are required in production"
            )

        return cls(
            host=os.getenv(f"{prefix}_HOST", "localhost"),
            port=int(os.getenv(f"{prefix}_PORT", "5672")),
            user=user or "guest",
            password=password or "guest",
            vhost=os.getenv(f"{prefix}_VHOST", "/"),
        )

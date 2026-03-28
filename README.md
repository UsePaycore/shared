# Paycore Shared Libraries

Shared Python packages for the Paycore platform.

## Packages

| Package | Description |
|---------|-------------|
| `paycore-domain` | Domain primitives: entities, value objects, events, exceptions, CQRS |
| `paycore-rabbitmq` | RabbitMQ event bus, consumers with retry/dead-letter support |
| `paycore-persistence` | SQLAlchemy base models, declarative bases, encryption services |

## Installation

```bash
pip install -e packages/paycore-domain
pip install -e packages/paycore-rabbitmq
pip install -e packages/paycore-persistence
```

## Development

```bash
ruff check packages/
pytest packages/paycore-domain/tests/ -v
```

# Local signed dispatch integration (development only)

The local coordinator connects signed claim verification, SQLite outbox,
idempotent local receiver, and acknowledgement reconciliation.

## Explicit restrictions
- **No live dispatch transport** is implemented. The production adapter always raises.
- HMAC signing uses a development-only secret in tests. This is not an identity
  provider, tenant authorization service, issuer lifecycle or production key management.
- `process_local` is an internal testing method, not a public API.
- A local receiver record proves only local acceptance, not delivery to a
  carrier, driver, telematics platform, or external TMS.
- Uncertain actions cannot be automatically retried. A matching persisted
  local receiver record is required for local reconciliation.
- Original research datasets and experiment results are unchanged.
- EXP-15 and EXP-16 remain future planned experiments.

## Tests
```sh
python -m unittest tests.test_local_dispatch_coordinator -v
python -m unittest discover -s tests -v
```

## Before any production use
- Connect a trusted identity provider and verify tenant-scoped claims server-side.
- Authenticate receiver acknowledgements, use durable delivery identifiers,
  and design a transactional boundary across reservation and outbox.
- Add key rotation, revocation, security logging and secrets management.
- Add process-crash injection, concurrency, performance and threat-model testing.
- Run independent acceptance validation against reviewed expected decisions.

# Local dispatch outbox integration phase

This is a **non-production** engineering implementation for Adora's own future
dispatch system. No TMS, vehicle, carrier or third-party API is configured.

## Safety boundary

- The `DisabledDispatchAdapter` always refuses to send commands.
- Enqueue is not execution; claim is not execution; acknowledgement must
  originate from a future trusted receiver.
- Expired in-flight leases become **uncertain**, not automatically retried.
  A future worker must reconcile with the receiving system before any retry.
- The outbox is not yet connected to `src.trusted_gateway`, identity-provider
  verification, tenant isolation or a real receiver.
- `acknowledge()` is a local test interface, **not authenticated**. It must not
  be exposed as a production endpoint.

## Local verification

```bash
python -m unittest tests.test_dispatch_outbox -v
python -m unittest discover -s tests -v
```

## Next engineering gates

1. Define a receiver-side idempotency and signed receipt protocol.
2. Implement a controlled local receiver and reconciliation path.
3. Bind outbox creation to verified issuer claims and tenant/load scope.
4. Add crash-injection and fault-recovery tests before network transport.
5. Independently validate acceptance criteria; preserve original research data.

EXP-15 and EXP-16 are future planned experiments and are not prerequisites
for this phase.

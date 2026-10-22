# EXP-14: OS Process Interruption Recovery and Storage Engine Transaction Durability Specification

##  Architectural Provenance
* **Technical Integration Date:** October 19, 2026
* **System Category:** High-Availability Distributed Systems / Transaction Boundary Enforcement

##  Core Engineering Objectives
This engineering evaluation quantifies the transactional integrity and fault isolation capabilities of the telematics ingestion pipeline when subjected to abrupt operating system-level process terminations (`SIGKILL`). 

The evaluation maps system state compliance across three critical asynchronous boundary phases:
1. **Pre-Flight Boundary (`pre_flight_boundary`):** Interruption occurs prior to network payload transmission.
2. **Post-Mutation Boundary (`post_mutation_boundary`):** Interruption occurs after database state mutation but before downstream packet acknowledgement.
3. **Post-Acknowledgement Boundary (`post_acknowledgement_boundary`):** Interruption occurs after packet acknowledgement but prior to the local client transaction commit.

## Execution Protocol and Pipeline Infrastructure
The validation suite targets the automated tracking modules through a multi-process execution harness:
```bash
python experiments/EXP-14/run.py
```

### Evaluation Parameters
* **Metrics Ingestion Scope:** 18 independent process profiles are executed sequentially (3 profiling repetitions × 3 boundary interruption phases × 2 operational gating strategies).
* **Process Lifecycle Flow:** Each profile spins up an isolated child runtime worker process, blocks execution at a verified cryptographic checkpoint, issues a native operating system-level process termination command, instantiates a post-recovery replay sequence, and executes a full assertions matrix against a persistent SQLite storage engine boundary layer.

## Operational Routing Gating Strategies Evaluated

### 1. Unbuffered Retry Stream (`unbuffered_retry_stream`)
An unprotected delivery pipeline where the connection link re-transmits payloads blindly upon node wake-up or connection re-establishment. This strategy serves as the structural baseline to measure redundant mutations and sequence sync errors during un-gated replay sequences.

### 2. Durable Outbox with Idempotent Receiver (`durable_outbox_idempotent_receiver`)
An advanced, atomic transaction-gated architecture. The dispatch intent is securely hardened into a persistent state outbox before transport. The receiving node executes an explicit idempotency key cross-reference check within a isolated SQLite transaction boundary using `BEGIN IMMEDIATE` modifiers and Write-Ahead Logging (WAL) controls. This strategy ensures exact transaction uniqueness and absolute duplicate-action filtration under severe edge-case runtime interruptions.

## Historical Engineering Ancestry
This engineering validation framework builds upon the systematic development lineage of the centralized state persistence and interruption recovery tracks established in earlier repository milestones. It provides contemporaneous, verifiable proof of systematic technical tracking regarding concurrent telematics signal routing optimization.

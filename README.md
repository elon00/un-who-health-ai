# Health-themed cryptocurrency application prototype

This independent QMOOSA project explores health-data provenance and cryptocurrency token utility. WHO and UN names are project themes; no official affiliation, endorsement or operational health service is established.

## Implemented and tested

- Deterministic, bounded B3/S23 Conway simulation with snapshots and toroidal boundaries.
- Read-only EVM health probing that requires a configured endpoint, expected chain ID and fresh block. Other chain runtimes need separate adapters.
- Payment and signature verification reject unverified inputs. Their genuine x402 and hybrid cryptography backends remain **not implemented**.

Run `python tests/reality_check_harness.py` for local regression tests. A local HTTP integration test exercises the RPC request/response path; it is not evidence of a live chain deployment.

## Remaining product work

Define the actual user workflow, appropriate data/privacy controls, compatible chain, token economics, wallet integration and acceptance criteria. Integrate and verify real payment settlement and reviewed cryptographic implementations. Rust metadata is not an ICP canister deployment; ICP and Base are proposed targets only.

No testnet/mainnet product deployment, medical reliability, post-quantum security, customer traction or 100/100 readiness is certified. See the [portfolio execution plan](https://github.com/elon00/bountyhunter-os) and [current scorecard](reports/PROJECT_SCORECARD.json).

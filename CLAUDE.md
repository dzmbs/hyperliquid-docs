# Hyperliquid Documentation

Community mirror of Hyperliquid protocol docs, auto-synced from https://hyperliquid.gitbook.io/hyperliquid-docs

## Where to find docs

All documentation is in `docs/` preserving the original Gitbook hierarchy. Key sections:

- `docs/for-developers/api/` — REST & WebSocket API reference (info endpoint, exchange endpoint, signing, rate limits)
- `docs/for-developers/hyperevm/` — HyperEVM developer docs (precompiles, transfers, dual-block architecture, RPC)
- `docs/for-developers/nodes/` — Node operation, data schemas
- `docs/trading/` — Trading mechanics (fees, margining, order types, liquidations, funding)
- `docs/hypercore/` — HyperCore L1 (bridge, staking, vaults, oracle)
- `docs/hyperliquid-improvement-proposals-hips/` — HIPs
- `docs/builder-tools/` — Ecosystem tooling
- `docs/support/faq/` — Troubleshooting

## Source tracking

`docs/docs_manifest.json` maps every file to its original Gitbook URL and tracks content hashes.

## Updating docs

```bash
uv run scripts/fetch_docs.py
```

# Hyperliquid Documentation

Community mirror of Hyperliquid protocol documentation, automatically synced from the official Gitbook.

## Source

Official docs: https://hyperliquid.gitbook.io/hyperliquid-docs

## Documentation Structure

```
docs/
├── README.md                          # Main landing page
├── onboarding/                        # Getting started guides
├── hypercore/                         # HyperCore L1 (bridge, staking, vaults, etc.)
├── hyperevm/                          # HyperEVM overview
├── trading/                           # Trading mechanics (fees, margining, order types, etc.)
├── hyperliquid-improvement-proposals-hips/  # HIPs (HIP-1, HIP-2, HIP-3)
├── validators/                        # Running validators, delegation
├── for-developers/
│   ├── api/                           # REST & WebSocket API (info, exchange, signing)
│   ├── hyperevm/                      # HyperEVM dev docs (precompiles, transfers, RPC)
│   └── nodes/                         # Node operation & data schemas
├── builder-tools/                     # HyperEVM & HyperCore tooling
└── support/
    └── faq/                           # Troubleshooting & FAQ
```

## Sync

Documentation is fetched every 3 hours from Gitbook sitemaps via GitHub Actions. Each file maps 1:1 to an official docs page. See `docs/docs_manifest.json` for source URLs and change tracking.

## Usage

Reference files directly:
- API docs: `docs/for-developers/api/`
- Trading: `docs/trading/`
- HyperEVM: `docs/for-developers/hyperevm/`

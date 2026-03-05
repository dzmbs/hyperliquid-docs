# hyperliquid-docs

[![docs updated](https://img.shields.io/github/last-commit/dzmbs/hyperliquid-docs/main?label=docs%20updated&color=brightgreen)](https://github.com/dzmbs/hyperliquid-docs/commits/main)
[![pages](https://img.shields.io/badge/pages-135-blue)](docs/)
[![sync](https://img.shields.io/badge/sync-every%203h-orange)](https://github.com/dzmbs/hyperliquid-docs/actions)

Community mirror of [Hyperliquid](https://hyperliquid.gitbook.io/hyperliquid-docs) documentation, automatically synced every 3 hours.

Built for AI coding agents — works with Claude Code, Codex, Cursor, Copilot, Amp, Windsurf, Cline, Aider, and any tool that reads markdown.

## What's in here

All Hyperliquid documentation as markdown files in [`docs/`](docs/), preserving the original structure:

| Section | Path | Description |
|---------|------|-------------|
| Onboarding | `docs/onboarding/` | Getting started, deposits, testnet |
| HyperCore | `docs/hypercore/` | L1 architecture, bridge, staking, vaults |
| Trading | `docs/trading/` | Fees, margining, order types, liquidations |
| HyperEVM | `docs/for-developers/hyperevm/` | EVM dev docs, precompiles, RPC |
| API | `docs/for-developers/api/` | REST, WebSocket, signing, rate limits |
| Nodes | `docs/for-developers/nodes/` | Running nodes, data schemas |
| HIPs | `docs/hyperliquid-improvement-proposals-hips/` | Protocol improvement proposals |
| Builder Tools | `docs/builder-tools/` | Ecosystem tooling |
| Support | `docs/support/faq/` | FAQ & troubleshooting |

## How it works

A [GitHub Action](.github/workflows/update-docs.yml) runs every 3 hours:
1. Parses the Gitbook [sitemap index](https://hyperliquid.gitbook.io/hyperliquid-docs/sitemap.xml) to discover all pages
2. Fetches markdown via Gitbook's `.md` endpoint
3. Commits any changes

## Using with AI coding tools

### Claude Code
Clone into your project or reference as context:
```bash
git clone https://github.com/dzmbs/hyperliquid-docs.git
```
The `CLAUDE.md` file tells Claude where to find everything.

### Codex / Copilot / Amp / Cursor / Windsurf
The `AGENTS.md` file provides the universal context. Clone or add as a submodule.

### Any tool
Just point your agent at the `docs/` directory — it's plain markdown.

## Local sync

```bash
# Fetch latest docs locally
uv run scripts/fetch_docs.py
```

## License

This project mirrors publicly available documentation from [Hyperliquid](https://hyperliquid.gitbook.io/hyperliquid-docs). All documentation content is the property of Hyperliquid. This mirror is provided for convenience and is not affiliated with or endorsed by Hyperliquid.

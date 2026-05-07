# HIP-4: Outcome markets

### Overview

Outcomes are fully collateralized contracts that settle within a fixed range. They are a general-purpose primitive that are useful for applications such as prediction markets and bounded options-like instruments.&#x20;

Outcomes bring non-linearity, dated contracts, and an alternative form of derivative trading that does not involve leverage or liquidations. The outcome primitive expands the expressivity of HyperCore, while composing with other primitives such as portfolio margin and the HyperEVM.

The first market is a recurring binary outcome that settles daily at 06:00 UTC to the BTC mark price on HyperCore mark prices. See the spec [here](/hyperliquid-docs/trading/contract-specifications.md#recurring-outcomes). Multi-outcome markets will be supported but not part of the initial mainnet release. Additional features and markets will be rolled out in stages.

The outcome trading API is similar to spot, with key differences highlighted here: <https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/asset-ids>.

### Mechanics

Each outcome market consists of two sides, each with a token. Usually the tokens are labeled `Yes` and `No`. Settlement automatically converts either Yes to 1 quote token and No to 0 quote tokens, or vice versa.&#x20;

The order books of Yes and No tokens for the same outcome are merged to share liquidity. For example, an order to buy Yes at price `p` is equivalent to an order to Sell No at price `1-p`. Advanced users may also manually split and merge outcomes. See [here](/hyperliquid-docs/for-developers/api/exchange-endpoint.md#split-outcome) for API examples.

*Questions* are collections of outcomes that where exactly one outcome will settle to Yes, and all others will settle to No. Each outcome trades on a separate order book, but are linked by `negate` and `merge` operations. See [here](/hyperliquid-docs/for-developers/api/exchange-endpoint.md#negate-outcome) for API examples. In other words, users with No shares on different outcomes of the same question can redeem quote tokens before the underlying outcomes settle.


---

# Agent Instructions: Querying This Documentation

If you need additional information that is not directly available in this page, you can query the documentation dynamically by asking a question.

Perform an HTTP GET request on the current page URL with the `ask` query parameter:

```
GET https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-4-outcome-markets.md?ask=<question>
```

The question should be specific, self-contained, and written in natural language.
The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.

> For the complete documentation index, see [llms.txt](https://hyperliquid.gitbook.io/hyperliquid-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/websocket/subscriptions.md). Agents can also search and read this documentation through its [MCP server](https://hyperliquid.gitbook.io/hyperliquid-docs/~gitbook/mcp).

# Subscriptions

This page describes subscribing to data streams using the WebSocket API.

### Subscription messages

To subscribe to specific data feeds, you need to send a subscription message. The subscription message format is as follows:

```json
{
  "method": "subscribe",
  "subscription": { ... }
}
```

The subscription ack provides a snapshot of previous data for time series data (e.g. user fills). These snapshot messages are tagged with `isSnapshot: true` and can be ignored if the previous messages were already processed.

The subscription object contains the details of the specific feed you want to subscribe to. Choose from the following subscription types and provide the corresponding properties:

1. `notification`:
   * Subscription message: `{ "type": "notification", "user": "<address>" }`
   * Data format: `Notification`
2. `webData3` :
   * Subscription message: `{ "type": "webData3", "user": "<address>" }`
   * Data format: `WebData3`
3. `twapStates` :
   * Subscription message: `{ "type": "twapStates", "user": "<address>", "dex": "<dex>" }`
   * Data format: `TwapStates`
4. `clearinghouseState:`
   * Subscription message: `{ "type": "clearinghouseState", "user": "<address>", "dex": "<dex>" }`
   * Data format: `ClearinghouseState`
5. `openOrders`:
   * Subscription message: `{ "type": "openOrders", "user": "<address>", "dex": "<dex>" }`
   * Data format: `OpenOrders`
6. `candle`:
   * Subscription message: `{ "type": "candle", "coin": "<coin_symbol>", "interval": "<candle_interval>" }`
   * Supported intervals: "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "8h", "12h", "1d", "3d", "1w", "1M"
   * Data format: `Candle[]`
7. `l2Book`:
   * Subscription message: `{ "type": "l2Book", "coin": "<coin_symbol>" }`
   * Optional parameters: `nSigFigs: int`, `mantissa: int`
   * Data format: `WsBook`
8. `trades`:
   * Subscription message: `{ "type": "trades", "coin": "<coin_symbol>" }`
   * Data format: `WsTrade[]`
9. `orderUpdates`:
   * Subscription message: `{ "type": "orderUpdates", "user": "<address>" }`
   * Data format: `WsOrder[]`
10. `userEvents`:
    * Subscription message: `{ "type": "userEvents", "user": "<address>" }`
    * Data format: `WsUserEvent`
    * Note: The channel name for `userEvents` messages is `"channel": "user"`
11. `userFills`:
    * Subscription message: `{ "type": "userFills", "user": "<address>" }`
    * Optional parameter: `aggregateByTime: bool`
    * Data format: `WsUserFills`
12. `userFundings`:
    * Subscription message: `{ "type": "userFundings", "user": "<address>" }`
    * Data format: `WsUserFundings`
13. `userNonFundingLedgerUpdates`:
    * Subscription message: `{ "type": "userNonFundingLedgerUpdates", "user": "<address>" }`
    * Data format: `WsUserNonFundingLedgerUpdates`
14. `activeAssetCtx`:
    * Subscription message: `{ "type": "activeAssetCtx", "coin": "<coin_symbol>" }`
    * Data format: `WsActiveAssetCtx` or `WsActiveSpotAssetCtx`
15. `activeAssetData`: (only supports Perps)
    * Subscription message: `{ "type": "activeAssetData", "user": "<address>", "coin": "<coin_symbol>" }`
    * Data format: `WsActiveAssetData`
16. `userTwapSliceFills`:
    * Subscription message: `{ "type": "userTwapSliceFills", "user": "<address>" }`
    * Data format: `WsUserTwapSliceFills`
17. `userTwapHistory`:
    * Subscription message: `{ "type": "userTwapHistory", "user": "<address>" }`
    * Data format: `WsUserTwapHistory`
18. `bbo` :
    * Subscription message: `{ "type": "bbo", "coin": "<coin>" }`
    * Data format: `WsBbo`
19. `spotState`
    * Subscription message: `{ "type": "spotState", "user": "<address>", "isPortfolioMargin": bool }`
    * Data format: `WsSpotState`
    * `isPortfolioMargin` is an optional argument
20. `allDexsClearinghouseState`
    * Subscription message: `{ "type": "allDexsClearinghouseState", "user": "<address>" }`
    * Data format: `WsAllDexsClearinghouseState`
21. `outcomeMetaUpdates`
    * Subscription message: `{ "type": "outcomeMetaUpdates" }`
    * Data format: `WsOutcomeMetaUpdates`
22. `fastAssetCtxs`
    * Subscription message: `{ "type": "fastAssetCtxs" }`
    * Data format: base64 encoded and compressed `WsFastAssetCtxs`
    * To read data, apply in order:\
      1\. base64-decode to bytes\
      2\. decompress: a raw DEFLATE stream (RFC 1951) — there is no zlib (RFC 1950) or gzip (RFC 1952) wrapper. Python `zlib.decompress(b, wbits=-15)`, browsers `new DecompressionStream("deflate-raw")`, Node `fflate.inflateSync`\
      3\. UTF-8 decode and parse as JSON\
      4\. Example to test your implementation\
      payload: `"q1ZyCnFWsqpWyk0syg6oULJSsjQ3NTDQM1Wq1VFyDfFAkTI2MzXQMwJLVVRWWfmFuTiiyBuamOoZKdXWAgA="`\
      decoded: `{ "BTC": { "markPx": "97500.5" }, "ETH": { "markPx": "3650.25" }, "xyz:NVDA": { "markPx": "145.2" }}`
    * The first message is a snapshot, subsequent messages contain only coins that have updated. Fields that have no updates are omitted. A null `midPx` means the book has no mid.
23. `l2`:
    * Subscription message: `{ "type": "l2", "c": "<coin_symbol>" }`
    * Optional parameters: `s: int` (number of significant figures), `m: int` (mantissa). These work like `nSigFigs` and `mantissa` on `l2Book`.
    * Data format: `WsL2`
    * The first message is a `WsBook` snapshot with up to 20 levels per side. Subsequent messages are `WsL2Diff` diffs, either uncompressed under `u` or base64 encoded and compressed under `c`. Decode `c` the same way as `fastAssetCtxs`.
    * To apply a diff, first remove the levels at the indexes in `r` (positions in the previous book), then add or replace the levels in `l` by price. Diffs don't include the number of orders per level.
24. `pac`:
    * Subscription message: `{ "type": "pac" }`
    * Data format: base64 encoded and compressed `WsPac`, decoded the same way as `fastAssetCtxs`
    * Perp asset contexts for every perp dex, as `[dex, ctxs]` pairs. The first perp dex is `""`. Each `ctxs` array is in the same order as that dex's universe.
    * The first message is a snapshot. In subsequent messages, each ctx contains only the fields that changed, or `{}` if nothing changed.
25. `sac`:
    * Subscription message: `{ "type": "sac" }`
    * Data format: base64 encoded and compressed `WsSac`, decoded the same way as `fastAssetCtxs`
    * Spot asset contexts keyed by coin.
    * The first message is a snapshot, subsequent messages contain only coins that have updated. Fields that have no updates are omitted.
26. `allMids` (deprecated, use `fastAssetCtxs`):
    * Subscription message: `{ "type": "allMids", "dex": "<dex>" }`
    * Data format: `AllMids`
    * The `dex` field represents the perp dex to source mids from.
    * Note that the `dex` field is optional. If not provided, then the first perp dex is used. Spot mids are only included with the first perp dex.
27. `allDexsAssetCtxs` (deprecated, use `pac`):
    * Subscription message: `{ "type": "allDexsAssetCtxs" }`
    * Data format: `WsAllDexsAssetCtxs`

### User address

To subscribe to the account data associated with a master or sub-account, you must pass in the actual address of that account. A common pitfall is to use an agent wallet's address which leads to an empty result.

### Data formats

The server will respond to successful subscriptions with a message containing the `channel` property set to `"subscriptionResponse"`, along with the `data` field providing the original subscription. The server will then start sending messages with the `channel` property set to the corresponding subscription type e.g. `"trades"` and the `data` field providing the subscribed data.

The `data` field format depends on the subscription type:

* `AllMids`: All mid prices.
  * Format: `AllMids { mids: Record<string, string> }`
* `Notification`: A notification message.
  * Format: `Notification { notification: string }`
* `WebData3`: Aggregate information about a user, used primarily for the frontend.
  * Format: `WebData3`
* `WsTrade[]`: An array of trade updates.
  * Format: `WsTrade[]`
* `WsBook`: Order book snapshot updates.
  * Format: `WsBook { coin: string; levels: [Array<WsLevel>, Array<WsLevel>]; time: number; }`
* `WsOrder`: User order updates.
  * Format: `WsOrder[]`
* `WsUserEvent`: User events that are not order updates
  * Format: `WsUserEvent { "fills": [WsFill] | "funding": WsUserFunding | "liquidation": WsLiquidation | "nonUserCancel": [WsNonUserCancel] }`
* `WsUserFills` : Fills snapshot followed by streaming fills
* `WsUserFundings` : Funding payments snapshot followed by funding payments on the hour
* `WsUserNonFundingLedgerUpdates`: Ledger updates not including funding payments: withdrawals, deposits, transfers, and liquidations
* `WsBbo` : Bbo updates that are sent only if the bbo changes on a block
* `WsSpotState` : Spot state update.
* `WsAllDexsClearinghouseState` : Clearinghouse states across all dexs for specific user
* `WsAllDexsAssetCtxs` : Asset contexts across all dexs
* `WsOutcomeMetaUpdates` : Changes to the outcome meta
* `WsL2` : Order book snapshot followed by incremental diffs
* `WsPac` : Perp asset context diffs across all dexs
* `WsSac` : Spot asset context diffs

For the streaming user endpoints such as `WsUserFills`,`WsUserFundings` the first message has `isSnapshot: true` and the following streaming updates have `isSnapshot: false`.

### Data type definitions

Here are the definitions of the data types used in the WebSocket API:

```typescript
interface WsTrade {
  coin: string;
  side: string;
  px: string;
  sz: string;
  hash: string;
  time: number;
  // tid is 50-bit hash of (buyer_oid, seller_oid).
  // For a globally unique trade id, use (block_time, coin, tid)
  tid: number;
  users: [string, string] // [buyer, seller]
}

// Snapshot feed, pushed on each block that is at least 0.5 since last push
interface WsBook {
  coin: string;
  levels: [Array<WsLevel>, Array<WsLevel>];
  time: number;
}

interface WsBbo {
  coin: string;
  time: number;
  bbo: [WsLevel | null, WsLevel | null];
}

interface WsLevel {
  px: string; // price
  sz: string; // size
  n: number; // number of orders
}

interface Notification {
  notification: string;
}

interface AllMids {
  mids: Record<string, string>;
}

interface Candle {
  t: number; // open millis
  T: number; // close millis
  s: string; // coin
  i: string; // interval
  o: string; // open price
  c: string; // close price
  h: string; // high price
  l: string; // low price
  v: string; // volume (base unit)
  n: number; // number of trades
}

type WsUserEvent = {"fills": WsFill[]} | {"funding": WsUserFunding} | {"liquidation": WsLiquidation} | {"nonUserCancel" :WsNonUserCancel[]};

interface WsUserFills {
  isSnapshot?: boolean;
  user: string;
  fills: Array<WsFill>;
}

interface WsFill {
  coin: string;
  px: string; // price
  sz: string; // size
  side: string;
  time: number;
  startPosition: string;
  dir: string; // used for frontend display
  closedPnl: string;
  hash: string; // L1 transaction hash
  oid: number; // order id
  crossed: boolean; // whether order crossed the spread (was taker)
  fee: string; // negative means rebate
  tid: number; // unique trade id
  liquidation?: FillLiquidation;
  feeToken: string; // the token the fee was paid in
  builderFee?: string; // amount paid to builder, also included in fee
}

interface FillLiquidation {
  liquidatedUser?: string;
  markPx: string;
  method: "market" | "backstop";
}

interface WsUserFunding {
  time: number;
  coin: string;
  usdc: string;
  szi: string;
  fundingRate: string;
}

interface WsLiquidation {
  lid: number;
  liquidator: string;
  liquidated_user: string;
  liquidated_ntl_pos: string;
  liquidated_account_value: string;
}

interface WsNonUserCancel {
  coin: String;
  oid: number;
}

interface WsOrder {
  order: WsBasicOrder;
  status: string; // See https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint#query-order-status-by-oid-or-cloid for a list of possible values
  statusTimestamp: number;
}

interface WsBasicOrder {
  coin: string;
  side: string;
  limitPx: string;
  sz: string;
  oid: number;
  timestamp: number;
  origSz: string;
  cloid: string | undefined;
}

interface WsActiveAssetCtx {
  coin: string;
  ctx: PerpsAssetCtx;
}

interface WsActiveSpotAssetCtx {
  coin: string;
  ctx: SpotAssetCtx;
}

type SharedAssetCtx = {
  dayNtlVlm: string;
  prevDayPx: string;
  markPx: string;
  midPx?: string | null;
};

type PerpsAssetCtx = SharedAssetCtx & {
  funding: string;
  openInterest: string;
  oraclePx: string;
};

type SpotAssetCtx = SharedAssetCtx & {
  circulatingSupply: string;
};

interface WsActiveAssetData {
  user: string;
  coin: string;
  leverage: Leverage;
  maxTradeSzs: [string, string];
  availableToTrade: [string, string];
}

interface WsTwapSliceFill {
  fill: WsFill;
  twapId: number;
}

interface WsUserTwapSliceFills {
  isSnapshot?: boolean;
  user: string;
  twapSliceFills: Array<WsTwapSliceFill>;
}

interface TwapState {
  coin: string;
  user: string;
  side: string;
  sz: string;
  executedSz: string;
  executedNtl: string;
  minutes: number;
  reduceOnly: boolean;
  randomize: boolean;
  timestamp: number;
}

type TwapStatus = "activated" | "terminated" | "finished" | "error";
interface WsTwapHistory {
  state: TwapState;
  status: {
    status: TwapStatus;
    description: string;
  };
  time: number;
}

interface WsUserTwapHistory {
  isSnapshot?: boolean;
  user: string;
  history: Array<WsTwapHistory>;
}

// Additional undocumented fields in WebData3 will be removed on a future update
interface WebData3 {
  userState: {
    agentAddress: string | null;
    agentValidUntil: number | null;
    serverTime: number;
    cumLedger: string;
    isVault: boolean;
    user: string;
    optOutOfSpotDusting?: boolean;
    dexAbstractionEnabled?: boolean;
  };
  perpDexStates: Array<PerpDexState>;
}

interface PerpDexState {
  totalVaultEquity: string;
  perpsAtOpenInterestCap?: Array<string>;
  leadingVaults?: Array<LeadingVault>;
}

interface LeadingVault {
  address: string;
  name: string;
}

interface ClearinghouseState {
  dex: string;
  user: string;
  clearinghouseState: InnerClearinghouseState;
}

interface InnerClearinghouseState {
  assetPositions: Array<AssetPosition>;
  marginSummary: MarginSummary;
  crossMarginSummary: MarginSummary;
  crossMaintenanceMarginUsed: string;
  withdrawable: string;
}

interface MarginSummary {
  accountValue: string;
  totalNtlPos: string;
  totalRawUsd: string;
  totalMarginUsed: string;
}

interface AssetPosition { type: "oneWay"; position: Position }

interface OpenOrders {
  dex: string;
  user: string;
  orders: Array<Order>;
}

interface TwapStates {
  dex: string;
  user: string;
  states: Array<[number, TwapState]>;
}

interface WsSpotState {
  user: string;
  spotState: SpotState;
}

interface SpotState {
  balances: Array<UserBalance>;
}

interface UserBalance {
  coin: string;
  token?: number;
  hold: string;
  total: string;
  entryNtl: string;
}

interface WsAllDexsClearinghouseState {
  user: string;
  clearinghouseStates: Array<[string, InnerClearinghouseState]>;
}

interface WsAllDexsAssetCtxs {
  ctxs: Array<[string, Array<PerpsAssetCtx>]>;
}

type WsOutcomeMetaUpdates = [WsOutcomeMetaUpdate];

type WsOutcomeMetaUpdate =
  | { outcomeCreated: OutcomeSpec }
  | { outcomeSettled: number }
  | { questionUpdated: QuestionSpec }
  | { questionSettled: number };

type OutcomeSpec = {
  outcome: number;
  name: string;
  description: string;
  sideSpecs: [OutcomeSideSpec, OutcomeSideSpec];
};

type OutcomeSideSpec = {
  name: string;
};

type QuestionSpec = {
  question: number;
  name: string;
  description: string;
  fallbackOutcome: number;
  namedOutcomes: number[];
  settledNamedOutcomes: number[];
};

type FFastAssetCtx = {
  markPx?: string;
  midPx?: string | null;
};
type WsFastAssetCtxs = Record<string, FFastAssetCtx>;

// s: snapshot; u: uncompressed diff; c: base64 encoded and compressed WsL2Diff
type WsL2 = { s: WsBook } | { u: WsL2Diff } | { c: string };

interface WsL2Diff {
  c: string; // coin
  t: number; // time
  l: [Array<WsL2LevelUpdate>, Array<WsL2LevelUpdate>]; // [bids, asks] levels added or changed
  r: [Array<number>, Array<number>]; // [bids, asks] indexes of removed levels in the previous book
}

interface WsL2LevelUpdate {
  p: string; // price
  s: string; // size
}

// Each [dex, ctxs] vector is positional over the dex's universe
type WsPac = Array<[string, Array<Partial<PerpsAssetCtx>>]>;

type WsSac = Record<string, Partial<SpotAssetCtx>>;
```

<details>

<summary>WsUserNonFundingLedgerUpdates</summary>

```typescript
interface WsUserNonFundingLedgerUpdate {
  time: number;
  hash: string;
  delta: WsLedgerUpdate;
}

type WsLedgerUpdate =
  | WsDeposit
  | WsWithdraw
  | WsInternalTransfer
  | WsSubAccountTransfer
  | WsLedgerLiquidation
  | WsVaultDelta
  | WsVaultWithdrawal
  | WsVaultLeaderCommission
  | WsSpotTransfer
  | WsAccountClassTransfer
  | WsSpotGenesis
  | WsRewardsClaim;

interface WsDeposit {
  type: "deposit";
  usdc: string;
}

interface WsWithdraw {
  type: "withdraw";
  usdc: string;
  nonce: number;
  fee: string;
}

interface WsInternalTransfer {
  type: "internalTransfer";
  usdc: string;
  user: string;
  destination: string;
  fee: string;
}

interface WsSubAccountTransfer {
  type: "subAccountTransfer";
  usdc: string;
  user: string;
  destination: string;
}

interface WsLedgerLiquidation {
  type: "liquidation";
  // NOTE: for isolated positions this is the isolated account value
  accountValue: string;
  leverageType: "Cross" | "Isolated";
  liquidatedPositions: Array<LiquidatedPosition>;
}

interface LiquidatedPosition {
  coin: string;
  szi: string;
}

interface WsVaultDelta {
  type: "vaultCreate" | "vaultDeposit" | "vaultDistribution";
  vault: string;
  usdc: string;
}

interface WsVaultWithdrawal {
  type: "vaultWithdraw";
  vault: string;
  user: string;
  requestedUsd: string;
  commission: string;
  closingCost: string;
  basis: string;
  netWithdrawnUsd: string;
}

interface WsVaultLeaderCommission {
  type: "vaultLeaderCommission";
  user: string;
  usdc: string;
}

interface WsSpotTransfer = {
  type: "spotTransfer";
  token: string;
  amount: string;
  usdcValue: string;
  user: string;
  destination: string;
  fee: string;
}

interface WsAccountClassTransfer = {
  type: "accountClassTransfer";
  usdc: string;
  toPerp: boolean;
}

interface WsSpotGenesis = {
  type: "spotGenesis";
  token: string;
  amount: string;
}

interface WsRewardsClaim = {
  type: "rewardsClaim";
  amount: string;
}
```

</details>

Please note that the above data types are in TypeScript format, and their usage corresponds to the respective subscription types.

### Examples

Here are a few examples of subscribing to different feeds using the subscription messages:

1. Subscribe to mark and mid prices for all assets:

   ```json
   { "method": "subscribe", "subscription": { "type": "fastAssetCtxs" } }
   ```
2. Subscribe to notifications for a specific user:

   ```json
   { "method": "subscribe", "subscription": { "type": "notification", "user": "<address>" } }
   ```
3. Subscribe to web data for a specific user:

   ```json
   { "method": "subscribe", "subscription": { "type": "webData3", "user": "<address>" } }
   ```
4. Subscribe to candle updates for a specific coin and interval:

   ```json
   { "method": "subscribe", "subscription": { "type": "candle", "coin": "<coin_symbol>", "interval": "<candle_interval>" } }
   ```
5. Subscribe to order book updates for a specific coin:

   ```json
   { "method": "subscribe", "subscription": { "type": "l2", "c": "<coin_symbol>" } }
   ```
6. Subscribe to trades for a specific coin:

   ```json
   { "method": "subscribe", "subscription": { "type": "trades", "coin": "<coin_symbol>" } }
   ```

### Unsubscribing from WebSocket feeds

To unsubscribe from a specific data feed on the Hyperliquid WebSocket API, you need to send an unsubscribe message with the following format:

```json
{
  "method": "unsubscribe",
  "subscription": { ... }
}
```

The `subscription` object should match the original subscription message that was sent when subscribing to the feed. This allows the server to identify the specific feed you want to unsubscribe from. By sending this unsubscribe message, you inform the server to stop sending further updates for the specified feed.

Please note that unsubscribing from a specific feed does not affect other subscriptions you may have active at that time. To unsubscribe from multiple feeds, you can send multiple unsubscribe messages, each with the appropriate subscription details.

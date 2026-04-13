# Priority fees

### Gossip (read) priority

There are 5 independent Dutch auctions synced to the same 3 minute schedule. The auction indices are optionally interpreted by nodes as an ordering for their peers when sending data with `split_client_blocks: true`. As documented in the node repository, these are the fastest transaction inputs to execution, broadcast even before they are executed by the L1. The foundation non-validator will opt into respecting the gossip priority auction ordering.&#x20;

The lower auction indices are strictly prioritized over higher indices. The prioritization applies to all data in the mempool transactions stream equally. The ordering should be relatively consistent in expectation but is subject to variance from the p2p consensus network. Gossip priority applies only to reading data. For prioritization of sending data, see the section below on order priority. Nodes respecting gossip priority will use the previous auction winners relative to that node's current execution state. Similar to token, spot, and perp deployment auctions, fees are burned.

The previous auction winners (i.e., current gossip priority ordering) and current auction statuses can be queried using the info request `{ "type": "gossipPriorityAuctionStatus"}`.&#x20;

Gossip priority reduces the need for market makers to hyper-optimize their infrastructure to remain competitive. To participate in the auction, users send action `{"type": "gossipPriorityBid", "slotId": 0, "ip": "1.2.3.4", "maxGas": 100000000}` where gas is wei of HYPE charged from spot balance. Each auction resets to 10 times the previous winning price of that slot, and have a minimum price of `0.1 HYPE`. Any address may bid on behalf of any IP address.

### Order (write) priority

Orders can be sent with grouping of the form `{"p": 12345}` where the rate is interpreted as a fraction `p / 100000000.0`. The rate is charged from undelegated staking balance as a fraction of the filled notional, converted to HYPE using the spot mark price. Currently, priority grouping is only supported for order actions where every order is IOC and HIP-3. The max priority rate is 8bps, i.e. `p = 80000`. Under order priority, all cancels are prioritized before all immediately executable orders. However, higher priority orders are prioritized before lower priority orders as a linear function of priority rate.&#x20;

Order priority reduces the need for market makers to hyper-optimize their order entry and connectivity, and instead focus on the strategy itself. It further protects makers and allows responsiveness to price moves driven by traditional venues.

Order priority applies only to sending data. For prioritization of reading data, see the previous section on gossip priority. Similar to gossip priority auctions, order priority fees are burned.

Note: priority fee paid will be included in user fills before the feature is enabled on mainnet

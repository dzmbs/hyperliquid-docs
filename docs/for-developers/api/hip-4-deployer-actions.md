> For the complete documentation index, see [llms.txt](https://hyperliquid.gitbook.io/hyperliquid-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-4-deployer-actions.md).

# HIP-4 deployer actions

### Overview

To ensure markets are high quality and well-defined, validators vote on outcome templates, which HIP-4 deployers use as the basis for permissionless deployments. Templates fix the structure of the specification's display text, side names, and the set of typed keywords.

Deploying has no gas cost. Capacity is instead bounded by per-deployer limits (see Limits).

### Action format

The following actions are involved in deployment:

```json
{ "type": "activateOutcomeDeployer", "venueNameIfActivate": "aa" }
{ "type": "spotDeploy", "outcome": { "<variant>": { ...variant fields... } } }
```

* Outcomes and questions are referenced by the numeric index assigned at creation, e.g. `"outcome": 7`.
* Venue name follow same rule as HIP-3 dex name: 2-4 lowercase characters. This cannot be changed after creation and must be unique.
* As with HIP-3, all lists of tuples should be lexographically sorted before signing
* `keywordToValue` is a sorted list of tuples mapping each template keyword to its value. For example, `[["expiry","20260801-0600"],["target","100"],["underlying","ABC"]]`.
* Name-and-description values are two-element arrays: `["<name>", "<description>"]`.
* `sideNames` arrays are `["<YES side name>", "<NO side name>"]`.
* Amounts and settlement fractions are decimal strings (`"1"`, `"0.25"`).

### Activation

```json
{ "type": "activateOutcomeDeployer", "isDeactivate": <boolean> }
```

* **Staking requirement**: active deployers must maintain the staking requirement for as long as it remains an outcome deployer. Requirements stack with the deployer's other staking requirements. For example, stake that counts towards HIP-3 deployment does not double-count towards outcome deployment.
* Deployers must use Standard account abstraction.

Deactivate with `"isDeactivate": true`. Deactivation requires that the minimum deployer staking duration (183 days, restarted on re-activation) has elapsed and that the deployer has no active outcomes.

### Templates

Every deployer-created market comes from a template. A template has one of three roles:

* **Standalone outcome**: deploys a single YES/NO market; the template fixes the side names.
* **Question**: deploys a question (the container).
* **Question outcome**: deploys one named outcome of a question; each question-outcome template declares its parent question template, and instantiations are only accepted under that parent.

A template fixes display name and description text containing `{keyword}` placeholders (e.g., `"{underlying} above {target} at {expiry}"`) together with a typed `hint` per keyword. An instantiation supplies exactly one value per keyword.

Keyword value formats by hint type:

| Hint       | Value format                                                             |
| ---------- | ------------------------------------------------------------------------ |
| `dateTime` | `%Y%m%d-%H%M`, e.g. `"20260712-1830"`; must be within the next year      |
| `date`     | `YYYYMMDD`, e.g. `"20260712"` (end of day); must be within the next year |
| `string`   | free text                                                                |
| `hlPerp`   | coin name of an existing perp, e.g. `"ABC"` or `"test:ABC"`              |

Values are at most 100 characters and cannot contain `{`, `}`, or `|` (`:` is allowed, e.g. for HIP-3 coin names).

The onchain outcome descriptions are derived from the instantiation:

* **Name**: `template:<template_id>`, e.g. `template:aaa`. The `template:` prefix is reserved. Only template deployments can produce it.
* **Description**: the keyword-value pairs sorted by keyword and joined as `keyword:value|keyword:value`, e.g. `expiry:20260801-0600|target:100|underlying:BTC`.
* **Side names**: for standalone outcomes, `template:` plus the template's side names (e.g. `template:Over` / `template:Under`); question named outcomes use the defaults `Yes` / `No`.
* **Question fallback**: named `template fallback` with description `other` and side names `Yes` / `No`.

### Action reference

The `outcome` family of `spotDeploy` has four deployer variants.

#### `registerStandaloneOutcomeFromTemplate`

Deploys a standalone YES/NO market from a standalone outcome template.

```json
{
  "type": "spotDeploy",
  "outcome": {
    "registerStandaloneOutcomeFromTemplate": {
      "id": "abc",
      "keywordToValue": {
        "expiry": "20260801-0600",
        "target": "100",
        "underlying": "ABC"
      }
    }
  }
}
```

#### `registerQuestionFromTemplate`

Deploys a question and its named outcomes in one action.

```json
{
  "type": "spotDeploy",
  "outcome": {
    "registerQuestionFromTemplate": {
      "questionTemplateInstance": {
        "id": "abc",
        "keywordToValue": { "expiry": "20260801-1830" }
      },
      "namedOutcomeTemplateInstances": [
        { "id": "abc-outcome", "keywordToValue": { "choice": "A" } },
        { "id": "abc-outcome", "keywordToValue": { "choice": "B" } },
        { "id": "abc-other", "keywordToValue": {} }
      ]
    }
  }
}
```

* Each named outcome template must declare the question template as its parent. The same named outcome template may be instantiated multiple times with different values.
* A question with N named outcomes registers N + 1 outcomes (the fallback is created automatically). All count toward the deployer's active-outcome cap.
* **The named outcome set is fixed at creation**. A future upgrade will support adding outcomes to a live question. Bounded to at most 100 named outcomes per question.

#### `settleOutcome`

Settles one outcome of the deployer.

```json
{
  "type": "spotDeploy",
  "outcome": {
    "settleOutcome": {
      "outcome": 7,
      "settleFraction": "1",
      "details": "",
      "nameAndDescription": ["template:abc", "expiry:20260801-0600|target:100|underlying:ABC"],
      "sideNames": ["template:Over", "template:Under"]
    }
  }
}
```

* `nameAndDescription` and `sideNames` must exactly match the outcome being settled.
* `settleFraction` is a decimal in `[0, 1]`. Standalone outcomes may settle to any fraction (e.g. `"0.66"` for scalar payouts); outcomes that belong to a question must settle to exactly `"0"` or `"1"`.
* `details` must be empty.
* For question outcomes, settlement is sequential: named outcomes may settle to `"0"` in any order. A single outcome settles to `"1"` after it is the last active named outcome, which automatically settles the fallback to 0 and settles the question.

#### `settleQuestion2`

Settles all remaining named outcomes of a question in one action. Note: The original `settleQuestion` variant is discontinued.

```json
{
  "type": "spotDeploy",
  "outcome": {
    "settleQuestion2": {
      "question": 3,
      "outcomeSettlements": [
        {
          "outcome": 11,
          "settleFraction": "1",
          "details": "",
          "nameAndDescription": ["template:abc-outcome", "choice:A"],
          "sideNames": ["Yes", "No"]
        },
        {
          "outcome": 12,
          "settleFraction": "0",
          "details": "",
          "nameAndDescription": ["template:abc-outcome", "choice:B"],
          "sideNames": ["Yes", "No"]
        }
      ],
      "nameAndDescription": ["template:abc", "expiry:20260801-1830"]
    }
  }
}
```

* `outcomeSettlements` must cover exactly the question's remaining active named outcomes, with exactly one settling to `"1"` and all others to `"0"`. The fallback settles to 0 automatically.

### Read API

* `{"type": "outcomeMeta"}` info request includes outcome deployer information.
* `{"type": "outcomeTemplates"}` info request returns all templates.

### Limits

* At most `N` active outcomes per deployer (N=10 on testnet). Settling outcomes frees capacity.
* A deployer can deploy `M` outcomes per day (M=50 on testnet).

Polymarket Liquidity Provider (LP) Data Fetcher

**Overview**
This script is a Python tool for analysing Polymarket prediction markets, specifically designed for Liquidity Providers (LPs). 
It fetches real-time market data via the Polymarket ClobClient API, calculates estimated LP rewards per $100 provided (using geometric and simple means), computes annualized volatility across time windows (1h to 30d), and outputs results to CSV files. 
Markets are ranked by reward potential while factoring in risk (volatility/reward ratio).

Key outputs:

(a) Top markets by gm_reward_per_100 (daily estimated earnings per $100 LP).
(b) Volatility metrics for risk assessment.
(c) Filtered views (e.g., low-vol markets).

This programme is ideal for identifying high-yield, low-risk LP opportunities in events like earnings bets or geopolitics.

**Features**

- Market Sampling: Pulls all active Polymarket markets with rewards enabled.
- Order Book Analysis: Simulates LP rewards based on bid/ask depth near midpoint.
- Volatility Calculation: Annualized std dev of log returns from 1m price history.
- Risk-Adjusted Ranking: Composite scores balancing rewards, vol, and price balance.
- Output Options: Local CSVs stored in the CSV/ folder.
- Parallel Processing: Fast execution with threading for order books and volatility.

**Prerequisites**

- Python 3.8+
- A Polygon wallet private key (for API authentication - no funds required for data fetching)

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/terrytrl100/prediction_markets_test.git
cd prediction_markets_test
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (.env)
Create a `.env` file in the root directory (ignored by Git). Add your Polymarket wallet details:

```
PK=your_polygon_private_key_here
```

**Note:** Your private key is used for API authentication with Polymarket. For **data fetching only**, the wallet doesn't need any funds. If you plan to use the trading functions (see Advanced section below), use a development wallet with minimal funds you can afford to lose. Never commit your `.env` file!

## Usage

Run the main script:
```bash
python data_updater.py
```

The script will fetch ~1000+ markets (runtime: 2–5 minutes depending on API rate limits).

### Output Files

- `CSV/all_markets.csv`: Full ranked list of all markets
- `CSV/volatility_markets.csv`: Low-volatility markets subset (volatility_sum < 20)
- `CSV/full_markets.csv`: Raw order book data
- Console output: Top 10 markets by rewards + progress logs

### Example Console Output
```
Top 10 Markets (by gm_reward_per_100):
[Table of markets with rewards, volatility, and odds...]
```

## Project Structure

### Python Modules

#### `data_updater.py` (Main Script)
**Purpose:** Automated market data fetching and analysis  
**Usage:** `python data_updater.py`

Main functions:
- `fetch_and_process_data()`: Main entry point - fetches and processes all markets
- `get_clob_client()`: Creates authenticated API client
- `get_all_markets(client)`: Fetches all active markets with rewards
- `add_volatility_to_df(df)`: Calculates volatility metrics across multiple timeframes
- `get_markets(all_results, sel_df)`: Ranks markets by reward potential

**Output:** Three CSV files in `CSV/` folder with market analysis

#### `trading_utils.py` (Manual Trading Functions)
**Purpose:** Helper functions for placing real trades  
**⚠️ Warning:** These functions interact with real smart contracts. Use only with funds you can afford to lose.

**Usage Example:**
```python
from trading_utils import approveContracts, market_action, get_position

# One-time setup (requires ~$0.50 MATIC for gas)
approveContracts()

# Place a buy order ($100 at 55% probability)
market_action(
    marketId="0x123abc...",  # Get from CSV files
    action="BUY",
    price=0.55,
    size=100
)

# Check position value
value = get_position("0x123abc...")
print(f"Position worth: ${value:.2f}")
```

**Functions:**
- `approveContracts()`: One-time setup to approve USDC/CTF tokens (required before first trade)
- `market_action(marketId, action, price, size)`: Place buy/sell orders
- `get_position(marketId)`: Get current position value in USD

**Requirements:**
- Wallet must have USDC balance
- Must run `approveContracts()` once per wallet
- Needs `erc20ABI.json` file in project root

#### `find_markets.py` (Internal Utilities)
**Purpose:** Market discovery and analysis utilities  
**Note:** Used internally by `data_updater.py` - most users don't need to interact with this directly

Contains helper functions for:
- Order book analysis
- Reward calculations
- Volatility computations
- Market filtering and ranking

## Advanced: Building Custom Trading Bots

You can build automated trading strategies on top of these modules:

```python
import pandas as pd
from trading_utils import market_action
from data_updater import fetch_and_process_data

# 1. Get latest market analysis
fetch_and_process_data()

# 2. Load the results
markets = pd.read_csv('CSV/volatility_markets.csv')

# 3. Filter for your criteria
good_markets = markets[
    (markets['gm_reward_per_100'] > 2.0) &
    (markets['volatility_sum'] < 10)
].head(5)

# 4. Place orders (manually review first!)
for _, market in good_markets.iterrows():
    print(f"Consider: {market['question']}")
    print(f"Reward: {market['gm_reward_per_100']}, Vol: {market['volatility_sum']}")
    # Uncomment to actually trade:
    # market_action(market['token1'], "BUY", 0.50, 100)
```

**⚠️ Trading Risks:**
- Market prices can move quickly
- LP positions face impermanent loss risk
- Smart contract interactions are irreversible
- Only use development wallets with funds you can afford to lose

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
- A Polymarket wallet (on Polygon) with USDC for LP (optional for data fetch)

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

**Note:** Your private key should be a hex string (e.g., 0xabc123...). This enables API/trading functionality—use a development wallet with minimal funds. Never commit your `.env` file!

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

## Trading/LP Integration (Advanced)

The project includes utility functions for advanced trading operations:

- `approveContracts()`: Approve USDC/CTF contracts (run once per wallet)
- `market_action(marketId, 'BUY'/'SELL', price, size)`: Place orders on markets
- `get_position(marketId)`: Check current holdings value

**Warning:** These functions interact with real smart contracts on Polygon. Use with caution and only with funds you can afford to lose.

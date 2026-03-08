import requests
import pandas as pd
import os
import json
from datetime import datetime, timezone

OUTPUT_FILE = os.path.expanduser("~/Documents/quantmarkets/market_prices.csv")

KALSHI_BASE = "https://api.elections.kalshi.com/trade-api/v2"
POLYMARKET_BASE = "https://gamma-api.polymarket.com"

SKIP_TICKERS = ["KXBTCD", "KXBTC-", "KXETH", "KXSOL", "KXXRP", "KXINXU", "KXNASDAQ", "KXMVE"]

def fetch_kalshi_markets():
    print("Fetching Kalshi markets...")
    all_markets = []
    cursor = None
    for page in range(10):
        params = {"limit": 100, "status": "open"}
        if cursor:
            params["cursor"] = cursor
        try:
            r = requests.get(f"{KALSHI_BASE}/markets", params=params, timeout=30)
            if r.status_code != 200:
                break
            data = r.json()
            batch = data.get("markets", [])
            all_markets.extend(batch)
            cursor = data.get("cursor")
            if not cursor or len(batch) < 100:
                break
        except Exception as e:
            print(f"Kalshi error: {e}")
            break

    rows = []
    timestamp = datetime.now(timezone.utc).isoformat()

    for m in all_markets:
        ticker = m.get("ticker", "")
        if not ticker or any(x in ticker for x in SKIP_TICKERS):
            continue

        yes_bid = m.get("yes_bid", 0)
        yes_ask = m.get("yes_ask", 0)
        last_price = m.get("last_price", 0)
        open_time = m.get("open_time")
        close_time = m.get("close_time")
        event_ticker = m.get("event_ticker", "")

        if last_price and last_price > 0:
            mid_price = last_price / 100
        elif yes_bid and yes_ask and yes_bid > 0 and yes_ask > 0:
            mid_price = (yes_bid + yes_ask) / 2 / 100
        else:
            continue

        if mid_price <= 0 or mid_price >= 1:
            continue

        rows.append({
            "timestamp": timestamp,
            "source": "kalshi",
            "ticker": ticker,
            "event_ticker": event_ticker,
            "mid_price": round(mid_price, 4),
            "open_time": open_time,
            "close_time": close_time,
        })

    print(f"Kalshi: {len(rows)} valid markets")
    return rows

def fetch_polymarket_markets():
    print("Fetching Polymarket markets...")
    rows = []
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        offset = 0
        while offset < 500:
            r = requests.get(
                f"{POLYMARKET_BASE}/markets",
                params={"limit": 100, "offset": offset, "active": "true", "closed": "false"},
                timeout=30
            )
            if r.status_code != 200:
                break
            batch = r.json()
            if not batch:
                break

            for m in batch:
                # skip non-binary markets
                if m.get("groupItemCount", 0) > 0:
                    continue

                outcome_prices = m.get("outcomePrices")
                if not outcome_prices:
                    continue

                try:
                    prices = json.loads(outcome_prices) if isinstance(outcome_prices, str) else outcome_prices
                    yes_price = float(prices[0])
                except:
                    continue

                if yes_price <= 0 or yes_price >= 1:
                    continue

                rows.append({
                    "timestamp": timestamp,
                    "source": "polymarket",
                    "ticker": m.get("conditionId", ""),
                    "event_ticker": m.get("question", "")[:80],
                    "mid_price": round(yes_price, 4),
                    "open_time": m.get("startDateIso"),
                    "close_time": m.get("endDateIso"),
                })

            offset += 100

    except Exception as e:
        print(f"Polymarket error: {e}")

    print(f"Polymarket: {len(rows)} valid markets")
    return rows

def collect():
    print(f"Running collector at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    rows = []
    rows.extend(fetch_kalshi_markets())
    rows.extend(fetch_polymarket_markets())

    if not rows:
        print("No rows to save.")
        return

    df = pd.DataFrame(rows)

    if os.path.exists(OUTPUT_FILE):
        df.to_csv(OUTPUT_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(OUTPUT_FILE, mode="w", header=True, index=False)

    print(f"Total saved: {len(rows)} rows to {OUTPUT_FILE}")

if __name__ == "__main__":
    collect()

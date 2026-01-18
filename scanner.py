import yfinance as yf
import requests
from watchlist import WATCHLIST
from state import positions
import warnings
import pandas as pd

warnings.simplefilter(action="ignore", category=FutureWarning)

DISCORD_WEBHOOK = None

def alert(msg):
    print(msg)
    if DISCORD_WEBHOOK:
        try:
            requests.post(DISCORD_WEBHOOK, json={"content": msg}, timeout=5)
        except Exception as e:
            print("Alert failed:", e)

def normalize_df(df):
    """Fix yfinance multi-index columns"""
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def scan(interval="1d"):
    results = []
    period = "60d" if interval != "1d" else "1y"

    for ticker in WATCHLIST:
        try:
            df = yf.download(
                ticker,
                period=period,
                interval=interval,
                progress=False,
                auto_adjust=True
            )
        except Exception as e:
            print(f"Download error {ticker}: {e}")
            continue

        if df is None or df.empty or len(df) < 200:
            print(f"Skipping {ticker}: insufficient data")
            continue

        df = normalize_df(df)

        # Moving averages
        df["MA10"] = df["Close"].rolling(10).mean()
        df["MA50"] = df["Close"].rolling(50).mean()
        df["MA200"] = df["Close"].rolling(200).mean()

        latest = df.iloc[-1]

        # 🔒 Force scalars (safe)
        price = float(latest["Close"])
        ma10  = float(latest["MA10"])
        ma50  = float(latest["MA50"])
        ma200 = float(latest["MA200"])

        in_position = positions.get(ticker, False)

        # ENTRY
        enter = (
            not in_position and
            ma10 > ma50 > ma200 and
            price > ma50
        )

        # EXIT
        exit_signal = (
            in_position and (
                ma10 < ma50 or
                price < ma200 or
                price < ma10
            )
        )

        if enter:
            positions[ticker] = True
            alert(f"🟢 ENTER LONG {ticker} @ {round(price,2)}")

        if exit_signal:
            positions[ticker] = False
            alert(f"🔴 EXIT LONG {ticker} @ {round(price,2)}")

        # Cash-secured put suggestion (2–3% OTM)
        put_low  = round(price * 0.97, 2)
        put_high = round(price * 0.99, 2)
        prem_low  = round(price * 0.01, 2)
        prem_high = round(price * 0.015, 2)

        results.append({
            "ticker": ticker,
            "price": round(price, 2),
            "ma10": round(ma10, 2),
            "ma50": round(ma50, 2),
            "ma200": round(ma200, 2),
            "in_position": positions.get(ticker, False),
            "put_strike": f"{put_low}-{put_high}",
            "put_premium": f"${prem_low}-${prem_high}"
        })

    return results

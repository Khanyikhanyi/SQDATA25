# filename: sqfx_feed.py
from flask import Flask, jsonify
import yfinance as yf
import time

app = Flask(__name__)

# ───────── CONFIG ─────────
categories = {
    "Indices": ["^GSPC", "^IXIC"],  # S&P 500, NASDAQ
    "Forex": ["EURUSD=X", "GBPUSD=X", "USDJPY=X"]
}

latest_data = {}

# ───────── FETCHER ─────────
def fetch_all_prices():
    snapshot = {}
    for group, symbols in categories.items():
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="1d", interval="1m")
                if not data.empty:
                    snapshot[symbol] = round(data["Close"].iloc[-1], 5)
                else:
                    snapshot[symbol] = "No data"
            except Exception as e:
                snapshot[symbol] = f"Error: {str(e)[:25]}"
    snapshot["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
    return snapshot

# ───────── ROUTES ─────────
@app.route("/")
def home():
    return jsonify({
        "status": "✅ ShadowQuantFX API Active",
        "usage": {"endpoint": "/prices", "method": "GET"},
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route("/health")
def health():
    return jsonify({"status": "OK", "time": time.strftime("%H:%M:%S")})

@app.route("/prices", methods=["GET"])
def prices():
    # always refresh data before returning
    global latest_data
    latest_data = fetch_all_prices()
    return jsonify(latest_data)

# ───────── STARTUP ─────────
if __name__ == "__main__":
    print("🚀 Starting ShadowQuantFX Cloud API...")
    # fetch once immediately at startup
    latest_data = fetch_all_prices()
    app.run(host="0.0.0.0", port=5000)

# filename: sqfx_feed.py
from flask import Flask, jsonify, request
import yfinance as yf
import time

app = Flask(__name__)

# ─────────────── CONFIG ───────────────
API_KEY = "ShadowQuantFX_Private_Key_2025"  # optional: restrict access
categories = {
    "Stocks": ["AAPL", "MSFT", "GOOG", "TSLA"],
    "Indices": ["^GSPC", "^IXIC"],
    "Forex": ["EURUSD=X", "GBPUSD=X", "USDJPY=X"]
}
latest_data = {}

# ─────────────── CORE ───────────────
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

@app.before_request
def auth_check():
    if request.path in ["/", "/health"]:
        return
    key = request.headers.get("X-API-Key")
    if key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

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
    return jsonify(fetch_all_prices())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

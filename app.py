"""Flask web app: paste Solana addresses, see Devnet SOL balances."""
from flask import Flask, jsonify, render_template, request

from solana_viewer import DEVNET_RPC_URL, RpcError, get_balances, parse_addresses

app = Flask(__name__)
MAX_ADDRESSES = 500


@app.get("/")
def index():
    return render_template("index.html", rpc_url=DEVNET_RPC_URL)


@app.post("/api/balances")
def balances():
    data = request.get_json(silent=True) or {}
    addresses = parse_addresses(data.get("addresses", ""))
    if not addresses:
        return jsonify(error="Enter at least one address."), 400
    if len(addresses) > MAX_ADDRESSES:
        return jsonify(error=f"Please enter at most {MAX_ADDRESSES} addresses."), 400
    try:
        return jsonify(results=get_balances(addresses))
    except RpcError as exc:
        return jsonify(error=str(exc)), 502


if __name__ == "__main__":
    app.run(debug=True)

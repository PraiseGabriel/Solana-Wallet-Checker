# Solana Account Viewer

Enter one or more Solana wallet addresses and see the SOL balance of each, fetched from Solana Devnet over JSON-RPC.

## Features
- Paste multiple addresses (newline, comma, or space separated)
- Validates each address (base58, 32 bytes) before calling the network
- Fetches all balances in one RPC request (`getMultipleAccounts`, batched in groups of 100)
- Handles accounts that do not exist on Devnet (shown as 0 SOL, "Account not found")
- Web UI (Flask) and command line interface

## Setup
```
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the web app
```
python app.py
```
Open http://127.0.0.1:5000

## Run the CLI
```
python cli.py <address1> <address2> ...
```

## Tests
```
pytest
```

## Configuration
Default RPC endpoint is `https://api.devnet.solana.com`. Override it with the `SOLANA_RPC_URL` environment variable.

## Get Devnet SOL to test with
Create a wallet address and request an airdrop at https://faucet.solana.com (select Devnet).

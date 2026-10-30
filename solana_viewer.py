import os
import re

import requests

DEVNET_RPC_URL = os.environ.get("SOLANA_RPC_URL", "https://api.devnet.solana.com")
LAMPORTS_PER_SOL = 1_000_000_000
MAX_PER_REQUEST = 100  # getMultipleAccounts limit
BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


class RpcError(Exception):
    """Raised when the RPC endpoint cannot be reached or returns an error."""


def is_valid_address(address: str) -> bool:
    
    if not 32 <= len(address) <= 44:
        return False
    num = 0
    for ch in address:
        idx = BASE58_ALPHABET.find(ch)
        if idx < 0:
            return False
        num = num * 58 + idx
    leading_zeros = len(address) - len(address.lstrip("1"))
    decoded_len = leading_zeros + (num.bit_length() + 7) // 8
    return decoded_len == 32


def parse_addresses(text: str) -> list[str]:
    """Split on commas/whitespace/newlines and remove duplicates, keeping order."""
    seen, result = set(), []
    for item in re.split(r"[\s,;]+", text.strip()):
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def lamports_to_sol(lamports: int) -> str:
    """Exact lamports -> SOL string (9 decimals) without float rounding."""
    return f"{lamports // LAMPORTS_PER_SOL}.{lamports % LAMPORTS_PER_SOL:09d}"


def _rpc_call(method: str, params: list, rpc_url: str):
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    try:
        resp = requests.post(rpc_url, json=payload, timeout=15)
        resp.raise_for_status()
        body = resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise RpcError(f"Could not reach Solana RPC: {exc}") from exc
    if "error" in body:
        raise RpcError(body["error"].get("message", "Unknown RPC error"))
    return body["result"]


def get_balances(addresses: list[str], rpc_url: str = DEVNET_RPC_URL) -> list[dict]:
    """Return one result dict per address, in input order.

    status is one of: "ok", "not_found" (account has no lamports/doesn't exist
    on Devnet yet), or "invalid" (not a valid Solana address).
    """
    results = {}
    valid = []
    for addr in addresses:
        if is_valid_address(addr):
            valid.append(addr)
        else:
            results[addr] = {"address": addr, "status": "invalid",
                             "lamports": None, "sol": None}

    for i in range(0, len(valid), MAX_PER_REQUEST):
        chunk = valid[i:i + MAX_PER_REQUEST]
        result = _rpc_call(
            "getMultipleAccounts",
            [chunk, {"encoding": "base64", "commitment": "confirmed",
                     "dataSlice": {"offset": 0, "length": 0}}],
            rpc_url,
        )
        for addr, account in zip(chunk, result["value"]):
            if account is None:
                results[addr] = {"address": addr, "status": "not_found",
                                 "lamports": 0, "sol": "0.000000000"}
            else:
                lamports = account["lamports"]
                results[addr] = {"address": addr, "status": "ok",
                                 "lamports": lamports,
                                 "sol": lamports_to_sol(lamports)}

    return [results[a] for a in addresses]

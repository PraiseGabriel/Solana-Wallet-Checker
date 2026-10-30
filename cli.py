"""Command line viewer: python cli.py ADDR1 ADDR2 ..."""
import sys

from solana_viewer import DEVNET_RPC_URL, RpcError, get_balances, parse_addresses


def main() -> int:
    addresses = parse_addresses(" ".join(sys.argv[1:]))
    if not addresses:
        print("Usage: python cli.py <address> [<address> ...]")
        return 1
    try:
        rows = get_balances(addresses)
    except RpcError as exc:
        print(f"Error: {exc}")
        return 2
    print(f"Network: Devnet ({DEVNET_RPC_URL})\n")
    for r in rows:
        if r["status"] == "invalid":
            print(f"{r['address']}  INVALID ADDRESS")
        else:
            note = "  (account not found)" if r["status"] == "not_found" else ""
            print(f"{r['address']}  {r['sol']} SOL{note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

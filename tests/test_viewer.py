from unittest.mock import patch

import solana_viewer as sv

SYSTEM = "11111111111111111111111111111111"
TOKEN = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"


def test_valid_and_invalid_addresses():
    assert sv.is_valid_address(SYSTEM)
    assert sv.is_valid_address(TOKEN)
    assert not sv.is_valid_address("hello")
    assert not sv.is_valid_address("0" * 44)  # '0' is not base58


def test_parse_addresses_dedupes():
    assert sv.parse_addresses(f"{SYSTEM}, {TOKEN}\n{SYSTEM}") == [SYSTEM, TOKEN]


def test_lamports_to_sol():
    assert sv.lamports_to_sol(1_500_000_000) == "1.500000000"
    assert sv.lamports_to_sol(1) == "0.000000001"


def test_get_balances_mixed():
    fake = {"value": [{"lamports": 2_000_000_000}, None]}
    with patch.object(sv, "_rpc_call", return_value=fake):
        rows = sv.get_balances([SYSTEM, "bad", TOKEN])
    assert [r["status"] for r in rows] == ["ok", "invalid", "not_found"]
    assert rows[0]["sol"] == "2.000000000"

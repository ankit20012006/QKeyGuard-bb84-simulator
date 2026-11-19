from src.bb84_protocol import simulate_bb84
from src.security_analysis import security_status


def test_sifting_disclosure_and_remaining_candidate_partition():
    result = simulate_bb84(200, eve=False, seed=84, test_fraction=0.2)
    assert set(result.test_indices).isdisjoint(result.secret_indices)
    assert sorted(result.test_indices + result.secret_indices) == result.matching_indices
    assert len(result.sifted_alice) == len(result.matching_indices)
    assert len(result.disclosed_alice) == len(result.test_indices)
    assert len(result.secret_alice) == len(result.secret_indices)


def test_empty_test_and_sifted_cases_are_handled():
    result = simulate_bb84(1, eve=False, seed=8, test_fraction=0)
    assert result.test_qber is None
    assert result.sifted_qber in (0.0, None)
    assert result.test_indices == []
    assert security_status(result)[0] == "Insufficient key material"


def test_qber_sample_is_computed_only_on_disclosed_positions():
    result = simulate_bb84(500, eve=True, seed=6, test_fraction=0.25)
    expected = sum(result.alice_bits[i] != result.bob_bits[i] for i in result.test_indices) / len(result.test_indices)
    assert result.test_qber == expected

from src.bb84_protocol import simulate_bb84


def test_eve_intercept_resend_qber_approaches_quarter():
    result = simulate_bb84(12000, eve=True, seed=2201, test_fraction=0.2)
    assert result.eve_bits is not None
    assert result.eve_bases is not None
    assert abs(result.sifted_qber - 0.25) < 0.035


def test_more_signals_improve_statistical_stability():
    small = simulate_bb84(400, eve=True, seed=51)
    large = simulate_bb84(10000, eve=True, seed=51)
    assert abs(large.sifted_qber - 0.25) < abs(small.sifted_qber - 0.25)

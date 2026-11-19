import pytest

from src.bb84_protocol import build_transmission_circuit, simulate_bb84


@pytest.mark.parametrize("basis", [0, 1])
@pytest.mark.parametrize("bit", [0, 1])
def test_matching_basis_recovers_encoded_bit(basis, bit):
    # Directly test all possible preparations through repeated exact-basis circuits.
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    qc = build_transmission_circuit(bit, basis, basis)
    backend = AerSimulator()
    memory = backend.run(transpile(qc, backend), shots=64, memory=True, seed_simulator=33).result().get_memory()
    assert set(memory) == {str(bit)}


def test_no_eve_has_zero_sifted_qber():
    result = simulate_bb84(1024, eve=False, seed=7)
    assert result.sifted_qber == 0
    assert result.test_qber == 0
    assert result.eve_bits is None


def test_seed_reproduces_protocol_and_measurements():
    first = simulate_bb84(100, eve=True, seed=991)
    second = simulate_bb84(100, eve=True, seed=991)
    for attribute in ("alice_bits", "alice_bases", "bob_bases", "bob_bits", "eve_bases", "eve_bits", "test_indices"):
        assert getattr(first, attribute) == getattr(second, attribute)


def test_user_supplied_statevector_backend_uses_supported_one_qubit_batches():
    from qiskit_aer import AerSimulator

    result = simulate_bb84(32, eve=False, seed=2, backend=AerSimulator(method="statevector"))
    assert result.sifted_qber == 0


def test_invalid_size_and_fraction_rejected():
    with pytest.raises(ValueError):
        simulate_bb84(0)
    with pytest.raises(ValueError):
        simulate_bb84(8, test_fraction=1.1)

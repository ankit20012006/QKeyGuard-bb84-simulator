"""BB84 protocol engine built from Qiskit Aer circuits."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


@dataclass(frozen=True)
class SimulationResult:
    """One BB84 run; ``test_indices`` are publicly disclosed in this demo."""

    alice_bits: list[int]
    alice_bases: list[int]
    bob_bases: list[int]
    bob_bits: list[int]
    eve_bases: list[int] | None
    eve_bits: list[int] | None
    matching_indices: list[int]
    test_indices: list[int]
    secret_indices: list[int]
    test_qber: float | None
    sifted_qber: float | None
    eve_enabled: bool
    seed: int | None
    circuit: QuantumCircuit

    @property
    def sifted_alice(self) -> list[int]:
        return [self.alice_bits[i] for i in self.matching_indices]

    @property
    def sifted_bob(self) -> list[int]:
        return [self.bob_bits[i] for i in self.matching_indices]

    @property
    def disclosed_alice(self) -> list[int]:
        return [self.alice_bits[i] for i in self.test_indices]

    @property
    def disclosed_bob(self) -> list[int]:
        return [self.bob_bits[i] for i in self.test_indices]

    @property
    def secret_alice(self) -> list[int]:
        return [self.alice_bits[i] for i in self.secret_indices]

    @property
    def secret_bob(self) -> list[int]:
        return [self.bob_bits[i] for i in self.secret_indices]


def _normalise_seed(seed: int | None, stream: int = 0) -> int | None:
    if seed is None:
        return None
    return int(np.random.SeedSequence([int(seed), stream]).generate_state(1)[0])


def encode_qubit(bit: int, basis: int, circuit: QuantumCircuit | None = None) -> QuantumCircuit:
    """Prepare |bit> in basis 0 (Z) or basis 1 (X)."""
    if bit not in (0, 1) or basis not in (0, 1):
        raise ValueError("bit and basis must each be 0 or 1")
    qc = circuit if circuit is not None else QuantumCircuit(1, 1)
    if bit:
        qc.x(0)
    if basis:
        qc.h(0)
    return qc


def build_transmission_circuit(
    bit: int, alice_basis: int, bob_basis: int, *, measure: bool = True
) -> QuantumCircuit:
    """Build Alice preparation followed by Bob's basis choice and measurement."""
    qc = QuantumCircuit(1, 1 if measure else 0)
    encode_qubit(bit, alice_basis, qc)
    qc.barrier(label="quantum channel")
    if bob_basis:
        qc.h(0)
    if measure:
        qc.measure(0, 0)
    return qc


def _run_circuits(circuits: list[QuantumCircuit], backend: Any, seed: int | None, stream: int) -> list[int]:
    compiled = transpile(circuits, backend, seed_transpiler=_normalise_seed(seed, stream))
    result = backend.run(
        compiled,
        shots=1,
        memory=True,
        seed_simulator=_normalise_seed(seed, stream + 1),
    ).result()
    # Each circuit is at most the backend's supported width; Qiskit's displayed
    # memory is c[n-1]...c[0], so reverse each chunk before concatenating.
    bits: list[int] = []
    for i in range(len(circuits)):
        bits.extend(int(bit) for bit in result.get_memory(i)[0].replace(" ", "")[::-1])
    return bits


def _qber(left: list[int], right: list[int], indices: list[int]) -> float | None:
    if not indices:
        return None
    return sum(left[i] != right[i] for i in indices) / len(indices)


def simulate_bb84(
    n_qubits: int = 128,
    *,
    eve: bool = False,
    seed: int | None = None,
    test_fraction: float = 0.2,
    backend: Any | None = None,
) -> SimulationResult:
    """Simulate BB84, using Aer for every quantum preparation and measurement.

    Random classical choices (bits and bases) use NumPy. Bob's and Eve's
    outcomes are obtained from Aer measurement jobs. For Eve, her measured
    classical outcome controls a second Qiskit circuit that creates the resend.
    """
    if isinstance(n_qubits, bool) or not isinstance(n_qubits, (int, np.integer)) or n_qubits < 1:
        raise ValueError("n_qubits must be a positive integer")
    if not 0 <= test_fraction <= 1:
        raise ValueError("test_fraction must be between 0 and 1")

    rng = np.random.default_rng(seed)
    alice_bits = rng.integers(0, 2, size=n_qubits).tolist()
    alice_bases = rng.integers(0, 2, size=n_qubits).tolist()
    bob_bases = rng.integers(0, 2, size=n_qubits).tolist()
    # Signals are independent, so Aer MPS keeps the state representation linear
    # in signal count instead of allocating an exponential statevector.
    aer = backend or AerSimulator(method="matrix_product_state")

    backend_width = int(aer.configuration().n_qubits)
    # Chunk multi-signal runs only when the selected simulator has an MPS
    # representation. A user-supplied statevector backend stays one-qubit wide.
    method = getattr(getattr(aer, "options", None), "method", None)
    max_width = backend_width if method == "matrix_product_state" else 1

    def batch_circuits(bits: list[int], sender_bases: list[int], receiver_bases: list[int], name: str) -> list[QuantumCircuit]:
        circuits = []
        for start in range(0, n_qubits, max_width):
            stop = min(start + max_width, n_qubits)
            width = stop - start
            qc = QuantumCircuit(width, width, name=f"{name}_{start // max_width + 1}")
            for local, i in enumerate(range(start, stop)):
                if bits[i]:
                    qc.x(local)
                if sender_bases[i]:
                    qc.h(local)
                if receiver_bases[i]:
                    qc.h(local)
                qc.measure(local, local)
            circuits.append(qc)
        return circuits

    if not eve:
        first = batch_circuits(alice_bits, alice_bases, bob_bases, "Alice to Bob")
        bob_bits = _run_circuits(first, aer, seed, 10)
        eve_bases = eve_bits = None
        display_circuit = build_transmission_circuit(alice_bits[0], alice_bases[0], bob_bases[0])
    else:
        eve_bases = rng.integers(0, 2, size=n_qubits).tolist()
        # First stage: Eve's random-basis measurements.
        eve_stage = batch_circuits(alice_bits, alice_bases, eve_bases, "Alice → Eve")
        eve_bits = _run_circuits(eve_stage, aer, seed, 20)

        # Eve prepares a fresh qubit in the state she inferred, then Bob measures.
        resend = batch_circuits(eve_bits, eve_bases, bob_bases, "Eve → Bob (resend)")
        bob_bits = _run_circuits(resend, aer, seed, 30)

        # Readable per-signal schematic: stage 1/2 are the measured circuits above.
        display_circuit = build_attack_schematic(alice_bits[0], alice_bases[0], eve_bases[0], eve_bits[0], bob_bases[0])

    matching = [i for i in range(n_qubits) if alice_bases[i] == bob_bases[i]]
    test_count = min(len(matching), int(round(len(matching) * test_fraction)))
    test_indices = sorted(rng.choice(matching, size=test_count, replace=False).tolist()) if test_count else []
    test_set = set(test_indices)
    secret_indices = [i for i in matching if i not in test_set]
    return SimulationResult(
        alice_bits=alice_bits,
        alice_bases=alice_bases,
        bob_bases=bob_bases,
        bob_bits=bob_bits,
        eve_bases=eve_bases,
        eve_bits=eve_bits,
        matching_indices=matching,
        test_indices=test_indices,
        secret_indices=secret_indices,
        test_qber=_qber(alice_bits, bob_bits, test_indices),
        sifted_qber=_qber(alice_bits, bob_bits, matching),
        eve_enabled=eve,
        seed=seed,
        circuit=display_circuit,
    )


def build_attack_schematic(
    bit: int, alice_basis: int, eve_basis: int, eve_bit: int, bob_basis: int
) -> QuantumCircuit:
    """Schematic for one intercept/resend signal; measurements are staged."""
    qc = QuantumCircuit(1, 2)
    if bit:
        qc.x(0)
    if alice_basis:
        qc.h(0)
    qc.barrier(label="Alice to Eve")
    if eve_basis:
        qc.h(0)
    qc.measure(0, 0)
    qc.barrier(label="resend")
    qc.reset(0)
    if eve_bit:
        qc.x(0)
    if eve_basis:
        qc.h(0)
    if bob_basis:
        qc.h(0)
    qc.measure(0, 1)
    return qc

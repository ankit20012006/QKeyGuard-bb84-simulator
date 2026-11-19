"""Helpers for measured QBER interpretation and presentation."""

from __future__ import annotations

from .bb84_protocol import SimulationResult


def security_status(result: SimulationResult, threshold: float = 0.11) -> tuple[str, str]:
    if not result.matching_indices or not result.test_indices:
        return "Insufficient key material", "There are not enough sifted test bits to estimate QBER."
    qber = result.test_qber or 0.0
    if qber > threshold:
        return "Potential eavesdropping detected", f"Test QBER is {qber:.1%}, above the selected {threshold:.0%} threshold."
    if result.eve_enabled:
        return "Low test QBER observed", "A low sample QBER does not prove security or rule out an attacker."
    return "No Eve configured in this simulation", "The simulator ran without Eve; this does not prove a real channel is secure."

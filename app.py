"""Streamlit dashboard for the QKeyGuard BB84 teaching simulator."""

from __future__ import annotations

import streamlit as st

from src.bb84_protocol import simulate_bb84
from src.security_analysis import security_status
from src.visualization import (
    basis_figure,
    bit_comparison_figure,
    circuit_figure,
    measurement_histogram,
    protocol_frame,
    qber_comparison_figure,
    workflow_figure,
)

st.set_page_config(page_title="QKeyGuard · BB84 lab", page_icon="🔐", layout="wide")
st.markdown("""<style>
  .stApp {background: radial-gradient(ellipse at 20% 0%, #132d49 0, #0b1220 48%, #090e18 100%); color:#e2e8f0}
  [data-testid="stSidebar"] {background:#101b2a}
  [data-testid="stSidebar"] * {color:#dbeafe !important}
  [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {opacity:1 !important}
  [data-testid="stSidebar"] input {color:#0f172a !important;background:#f8fafc !important}
  [data-testid="stMetricLabel"] {color:#94a3b8 !important}
  [data-testid="stMetricValue"] {color:#e2e8f0 !important}
  h1,h2,h3 {letter-spacing:-.025em}
  .hero {padding:1.5rem 1.8rem;border:1px solid #28425e;border-radius:18px;background:linear-gradient(120deg,#12243a,#101827);margin-bottom:1rem}
  .eyebrow {color:#38bdf8;text-transform:uppercase;letter-spacing:.16em;font-size:.75rem;font-weight:700}
  .participant {border:1px solid #29435e;border-radius:14px;padding:1rem;background:#111e2f;text-align:center}
  .muted {color:#94a3b8}
</style>""", unsafe_allow_html=True)

st.markdown('<div class="hero"><div class="eyebrow">Interactive quantum communication lab</div><h1>QKeyGuard</h1><p>See how BB84 uses incompatible measurement bases to create shared key material—and how intercept-and-resend can disturb it.</p><p class="muted">Educational simulator · ideal local quantum simulation · no real cryptographic keys</p></div>', unsafe_allow_html=True)

people = st.columns(3)
for col, emoji, who, what in zip(people, ["🟦", "🟪", "🟧"], ["Alice", "Bob", "Eve"], ["Encodes random bits", "Chooses measurement bases", "Optional intercept and resend"]):
    with col:
        st.markdown(f'<div class="participant"><div style="font-size:2rem">{emoji}</div><b>{who}</b><br><span class="muted">{what}</span></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Simulation controls")
    n_qubits = st.slider("Signals sent", min_value=16, max_value=1024, value=512, step=16, help="Signals use independent qubits batched into Aer circuits.")
    eve_enabled = st.toggle("Enable Eve: intercept and resend", value=False)
    set_seed = st.checkbox("Use a reproducible seed", value=True)
    seed = st.number_input("Random seed", min_value=0, max_value=2**31 - 1, value=84, disabled=not set_seed)
    test_fraction = st.slider("Sifted bits disclosed for QBER sample", .05, .5, .2, .05)
    threshold = st.slider("Alert threshold", .01, .3, .11, .01)
    run = st.button("▶ Run BB84 simulation", type="primary", width="stretch")
    st.caption("Basis choices and bits use NumPy randomness. Quantum measurements use Qiskit Aer.")

if "result" not in st.session_state:
    st.session_state.result = simulate_bb84(n_qubits=512, eve=False, seed=84)
    st.session_state.seed = 84
    st.session_state.test_fraction = .2
    st.session_state.comparison = (simulate_bb84(n_qubits=512, eve=False, seed=84), simulate_bb84(n_qubits=512, eve=True, seed=84))
if run:
    current_seed = int(seed) if set_seed else None
    with st.spinner("Preparing and measuring quantum circuits with Qiskit Aer…"):
        st.session_state.result = simulate_bb84(n_qubits, eve=eve_enabled, seed=current_seed, test_fraction=test_fraction)
        compare_seed = current_seed
        st.session_state.comparison = (
            simulate_bb84(n_qubits, eve=False, seed=compare_seed, test_fraction=test_fraction),
            simulate_bb84(n_qubits, eve=True, seed=compare_seed, test_fraction=test_fraction),
        )
        st.session_state.seed = current_seed
        st.session_state.test_fraction = test_fraction

result = st.session_state.result
status, explanation = security_status(result, threshold)
st.markdown("### Run summary")
metric_cols = st.columns(4)
metric_cols[0].metric("Signals", len(result.alice_bits))
metric_cols[1].metric("Matching bases", len(result.matching_indices))
metric_cols[2].metric("Disclosed test bits", len(result.test_indices))
metric_cols[3].metric("Remaining key candidates", len(result.secret_indices))
tone = "🟠" if result.test_qber is not None and result.test_qber > threshold else "🟢"
st.info(f"{tone} **{status}.** {explanation}  Test-sample QBER: **{'n/a' if result.test_qber is None else f'{result.test_qber:.1%}'}**. A low observed QBER alone does not establish security.")

st.plotly_chart(workflow_figure(result.eve_enabled), width="stretch")
tab_results, tab_quantum, tab_analysis, tab_learn = st.tabs(["Protocol results", "Quantum circuit", "Analysis", "Learn BB84"])

with tab_results:
    st.subheader("Basis reconciliation and sifting")
    st.plotly_chart(basis_figure(result), width="stretch")
    st.caption("Only matching-basis positions are sifted. The sample positions below are disclosed and must be excluded from any key.")
    st.dataframe(protocol_frame(result), width="stretch", hide_index=True, height=360)
    st.markdown("**Sifted raw key** (before sample disclosure)")
    left, right = st.columns(2)
    left.code("Alice: " + "".join(map(str, result.sifted_alice)) if result.sifted_alice else "Alice: (empty)")
    right.code("Bob:   " + "".join(map(str, result.sifted_bob)) if result.sifted_bob else "Bob: (empty)")
    st.markdown("**Disclosed test sample** — removed from key material")
    left, right = st.columns(2)
    left.code("Alice: " + "".join(map(str, result.disclosed_alice)) if result.disclosed_alice else "Alice: (empty)")
    right.code("Bob:   " + "".join(map(str, result.disclosed_bob)) if result.disclosed_bob else "Bob: (empty)")
    st.markdown("**Remaining secret-key candidates** (not a final secure key; error correction and privacy amplification are omitted)")
    left, right = st.columns(2)
    left.code("Alice: " + "".join(map(str, result.secret_alice)) if result.secret_alice else "Alice: (empty)")
    right.code("Bob:   " + "".join(map(str, result.secret_bob)) if result.secret_bob else "Bob: (empty)")

with tab_quantum:
    st.subheader("Qiskit circuit for one signal")
    st.caption("The Eve schematic shows her measurement, reset, and resend. In the simulator, Eve and Bob stages are executed as separate Aer jobs so Eve's measured result controls the resent state.")
    st.pyplot(circuit_figure(result.circuit), width="stretch")
    st.code(result.circuit.draw(output="text"), language="text")

with tab_analysis:
    st.subheader("Measurement comparison")
    st.plotly_chart(bit_comparison_figure(result), width="stretch")
    st.plotly_chart(measurement_histogram(result), width="stretch")
    if all(run.sifted_qber is not None for run in st.session_state.comparison):
        st.plotly_chart(qber_comparison_figure(*st.session_state.comparison), width="stretch")
        st.caption("The comparison plot uses all simulator-known sifted errors as a diagnostic. In an actual protocol parties estimate QBER from only the disclosed test sample.")
    else:
        st.warning("At least one comparison run has no sifted bits, so a QBER comparison is unavailable. Increase the number of signals.")

with tab_learn:
    st.subheader("The ideas behind BB84")
    st.markdown("""
    - **Qubit:** a quantum two-level system. Here each signal is encoded as one qubit.
    - **Z basis:** computational states `|0⟩` and `|1⟩`. Alice applies `X` to encode bit 1.
    - **X basis:** Hadamard states `|+⟩` and `|−⟩`. Alice applies `H` after the optional `X`.
    - **Measurement:** a measurement in the matching basis recovers the encoded bit. Measuring in the other basis gives a random result and changes the state.
    - **Basis reconciliation / sifting:** Alice and Bob compare bases over a public channel and keep positions where their choices match.
    - **QBER:** the fraction of disagreements in disclosed, randomly selected sifted test bits. The demo also plots the simulator's full sifted error rate for diagnostics.
    - **Intercept and resend:** Eve measures each qubit in a random basis, then prepares a replacement state. If she chose the wrong basis, she can introduce an error. With ideal BB84 and full random-basis intercept/resend, expected sifted QBER is 25%; finite samples vary.

    Real BB84 also requires an **authenticated** classical channel, error correction, and privacy amplification. This ideal simulator does not implement a security proof, device imperfections, loss, finite-key bounds, or final key distillation. It cannot certify a real communication link.
    """)

st.divider()
st.caption("QKeyGuard · Educational demonstration only · No key distillation or cryptographic key export.")

"""Plotly and Matplotlib visualisations for the Streamlit dashboard."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .bb84_protocol import SimulationResult


def protocol_frame(result: SimulationResult) -> pd.DataFrame:
    rows = []
    matching = set(result.matching_indices)
    tests = set(result.test_indices)
    secret = set(result.secret_indices)
    for i in range(len(result.alice_bits)):
        rows.append({
            "Position": i + 1,
            "Alice bit": result.alice_bits[i],
            "Alice basis": "X" if result.alice_bases[i] else "Z",
            "Eve basis": ("X" if result.eve_bases[i] else "Z") if result.eve_bases is not None else "—",
            "Eve result": result.eve_bits[i] if result.eve_bits is not None else "—",
            "Bob basis": "X" if result.bob_bases[i] else "Z",
            "Bob result": result.bob_bits[i],
            "Matching bases": i in matching,
            "Role": "Test (disclosed)" if i in tests else "Key candidate" if i in secret else "Discarded",
        })
    return pd.DataFrame(rows)


def basis_figure(result: SimulationResult) -> go.Figure:
    n = len(result.alice_bits)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(1, n + 1)), y=[1 if x == y else 0 for x, y in zip(result.alice_bases, result.bob_bases)], mode="markers", name="Bases match", marker={"color": "#4ade80", "size": 8}))
    fig.update_layout(title="Basis reconciliation", xaxis_title="Signal position", yaxis={"tickvals": [0, 1], "ticktext": ["Different", "Match"], "range": [-0.4, 1.4]}, height=260, margin={"t": 50, "b": 45}, template="plotly_dark", plot_bgcolor="#111e2f", paper_bgcolor="#0b1220", font_color="#e2e8f0", title_font_color="#e2e8f0")
    return fig


def bit_comparison_figure(result: SimulationResult, max_points: int = 100) -> go.Figure:
    count = min(max_points, len(result.alice_bits))
    positions = list(range(1, count + 1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=positions, y=result.alice_bits[:count], mode="lines+markers", name="Alice", line={"color": "#60a5fa"}))
    fig.add_trace(go.Scatter(x=positions, y=result.bob_bits[:count], mode="lines+markers", name="Bob", line={"color": "#f472b6"}))
    fig.update_layout(title=f"Alice and Bob outcomes (first {count} signals)", xaxis_title="Signal position", yaxis={"tickvals": [0, 1], "range": [-0.25, 1.25]}, height=300, margin={"t": 50, "b": 45}, template="plotly_dark", plot_bgcolor="#111e2f", paper_bgcolor="#0b1220", font_color="#e2e8f0", title_font_color="#e2e8f0")
    return fig


def qber_comparison_figure(no_eve: SimulationResult, with_eve: SimulationResult) -> go.Figure:
    vals = [100 * (no_eve.sifted_qber or 0), 100 * (with_eve.sifted_qber or 0)]
    fig = go.Figure(go.Bar(x=["No Eve", "Intercept and resend"], y=vals, marker_color=["#34d399", "#fb923c"], text=[f"{v:.1f}%" for v in vals], textposition="outside"))
    fig.add_hline(y=25, line_dash="dash", line_color="#a78bfa", annotation_text="25% ideal Eve expectation")
    fig.update_layout(title="Sifted-key bit error rate (diagnostic view)", yaxis_title="Sifted QBER (%)", yaxis={"range": [0, max(35, max(vals, default=0) + 8)]}, height=340, template="plotly_dark", plot_bgcolor="#111e2f", paper_bgcolor="#0b1220", font_color="#e2e8f0", title_font_color="#e2e8f0")
    return fig


def measurement_histogram(result: SimulationResult):
    rows = [{"Party": party, "Outcome": str(bit)} for party, bits in [("Alice", result.alice_bits), ("Bob", result.bob_bits)] for bit in bits]
    fig = px.histogram(pd.DataFrame(rows), x="Outcome", color="Party", barmode="group", title="Raw measurement outcome counts", color_discrete_sequence=["#60a5fa", "#f472b6"])
    fig.update_layout(template="plotly_dark", plot_bgcolor="#111e2f", paper_bgcolor="#0b1220", font_color="#e2e8f0", title_font_color="#e2e8f0")
    return fig


def workflow_figure(eve: bool) -> go.Figure:
    node_y = 0.68
    if eve:
        horizontal_nodes = [
            (0.08, "<b>Alice</b><br>bits + bases"),
            (0.36, "<b>Quantum</b><br>channel"),
            (0.64, "<b>Eve</b><br>measure + resend"),
            (0.92, "<b>Bob</b><br>measure"),
        ]
    else:
        horizontal_nodes = [
            (0.08, "<b>Alice</b><br>bits + bases"),
            (0.50, "<b>Quantum</b><br>channel"),
            (0.92, "<b>Bob</b><br>measure"),
        ]
    nodes = [(x, node_y, label) for x, label in horizontal_nodes]
    nodes.append((horizontal_nodes[-1][0], -0.32, "<b>Public basis</b><br>check"))
    fig = go.Figure()
    for x, y, label in nodes:
        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            text=[label],
            mode="markers+text",
            textposition="middle center",
            textfont={"family": "Arial, Segoe UI, sans-serif", "color": "#e2e8f0", "size": 13},
            marker={"size": 132, "color": "#17324d", "line": {"color": "#38bdf8", "width": 2}},
            showlegend=False,
            hoverinfo="skip",
        ))
    for (x1, y1, _), (x2, y2, _) in zip(nodes, nodes[1:]):
        fig.add_annotation(
            x=x2,
            y=y2,
            ax=x1,
            ay=y1,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowcolor="#64748b",
            standoff=70,
            startstandoff=70,
        )
    fig.update_layout(
        title={"text": "BB84 workflow", "font": {"family": "Arial, Segoe UI, sans-serif", "size": 18, "color": "#e2e8f0"}},
        font={"family": "Arial, Segoe UI, sans-serif", "size": 14, "color": "#e2e8f0"},
        xaxis={"visible": False, "range": [0, 1], "fixedrange": True},
        yaxis={"visible": False, "range": [-0.88, 1.20], "fixedrange": True},
        height=390,
        autosize=True,
        margin={"t": 60, "b": 30, "l": 25, "r": 25},
        template="plotly_dark",
        plot_bgcolor="#0b1220",
        paper_bgcolor="#0b1220",
    )
    return fig


def circuit_figure(circuit):
    figure, axis = plt.subplots(figsize=(max(7, len(circuit.data) * 0.55), 2.4))
    circuit.draw(output="mpl", ax=axis, style={"backgroundcolor": "#f8fafc", "linecolor": "#334155"})
    figure.tight_layout()
    return figure

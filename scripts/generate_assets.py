"""Generate reproducible circuit and workflow illustrations for the README."""

from pathlib import Path
import sys

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.bb84_protocol import simulate_bb84

DEST = ROOT / "assets" / "diagrams"
DEST.mkdir(parents=True, exist_ok=True)


def draw(circuit, name: str) -> None:
    figure = circuit.draw(output="mpl", style={"backgroundcolor": "#f8fafc", "linecolor": "#1e293b"})
    figure.savefig(DEST / name, dpi=180, bbox_inches="tight")
    plt.close(figure)


def workflow() -> None:
    figure, axis = plt.subplots(figsize=(12, 2.8))
    axis.set_xlim(0, 12)
    axis.set_ylim(0, 3)
    axis.axis("off")
    points = [(1.1, "Alice", "random bits\n+ Z / X bases"), (4.2, "Quantum channel", "prepared qubits"), (7.1, "Eve (optional)", "measure + resend"), (10.5, "Bob", "random bases\n+ measurements")]
    for x, title, subtitle in points:
        axis.text(x, 1.65, f"{title}\n{subtitle}", ha="center", va="center", color="#e2e8f0", fontsize=11,
                 bbox={"boxstyle": "round,pad=0.75", "facecolor": "#14243a", "edgecolor": "#38bdf8", "linewidth": 1.5})
    for start, end in [(2.0, 3.15), (5.1, 6.1), (8.25, 9.45)]:
        axis.annotate("", xy=(end, 1.65), xytext=(start, 1.65), arrowprops={"arrowstyle": "-|>", "color": "#64748b", "lw": 2})
    axis.annotate("basis comparison → sifting → disclosed QBER sample", xy=(6, .4), ha="center", color="#475569", fontsize=10)
    figure.savefig(DEST / "bb84_workflow.png", dpi=180, bbox_inches="tight", facecolor="#f8fafc")
    plt.close(figure)


def main() -> None:
    clean = simulate_bb84(8, eve=False, seed=84)
    attacked = simulate_bb84(8, eve=True, seed=84)
    draw(clean.circuit, "single_qubit_no_eve.png")
    draw(attacked.circuit, "single_qubit_eve_intercept_resend.png")
    workflow()


if __name__ == "__main__":
    main()

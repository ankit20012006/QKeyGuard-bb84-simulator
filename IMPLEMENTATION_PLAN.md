# QKeyGuard implementation plan

1. **Inspect environment and repository** — confirm the workspace state, Python runtime, installed libraries, and repository instructions.
2. **Specify scientific model** — use Z/X BB84 states, independent random bases, matching-basis sifting, a disclosed test sample, and a distinct pool of remaining key candidates.
3. **Implement Qiskit engine** — prepare and measure each signal with Aer; simulate Eve as an actual measurement stage followed by a new preparation controlled by Eve's observed outcome.
4. **Build dashboard and charts** — provide editable parameters, Alice/Bob/Eve views, circuit/workflow diagrams, basis comparison, bit comparison, histograms, QBER comparison, and careful status messages.
5. **Validate behavior** — test encoding, noiseless measurements, attack QBER statistics, reproducibility, sifting, sample accounting, and small/empty cases.
6. **Document and package** — provide setup/run steps, scientific explanation, references, notebook walkthrough, generated visual artifacts, and a short demo outline.
7. **End-to-end verification** — run tests, generate assets, validate notebook syntax, and start the Streamlit application.

## Environment inspection

- Workspace began empty and had no repository-specific `AGENTS.md` or Git metadata.
- Python 3.12.15 is available through `uv`; the system `python` command is not on PATH.
- Qiskit, Aer, Streamlit, and the scientific Python packages were initially absent.
- Dependencies are installed in the isolated `.venv` from the compatible version ranges in `requirements.txt`.

## Current implementation

The scientific model, modular Qiskit engine, dashboard, package files, notebook, documentation, and presentation are implemented. The engine uses matrix product state simulation with backend-width circuit batches; Eve's first measurement outcome controls the resend batch. All 13 automated tests pass. The notebook validates, generated circuit/workflow images and screenshots are included, and browser checks exercised both the no-Eve and Eve scenarios through Streamlit.

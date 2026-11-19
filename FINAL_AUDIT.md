# QKeyGuard Final Audit

**Audit outcome:** Ready for an educational hackathon submission. The core BB84 model, Eve attack, key accounting, and measured QBER behavior are correct for this idealized simulator. This is not a production QKD implementation or a production cryptographic system.

## Scope and method

I inspected the protocol engine, dashboard, visualizations, tests, notebook, README, and dependency declarations. I ran the complete test suite, executed the notebook, checked dependency resolution and compatibility, launched the app on its configured loopback address, and ran five paired statistical experiments with fixed seeds.

The scientific review is consistent with [IBM Quantum Learning's QKD explanation](https://quantum.cloud.ibm.com/learning/en/modules/computer-science/quantum-key-distribution) and the original Bennett–Brassard BB84 work ([republished paper](https://doi.org/10.1016/j.tcs.2014.05.025)). For ideal random-basis intercept-and-resend, the expected sifted error rate is 25%: half of Eve's basis choices are wrong, and those cause a 50% error chance when Alice and Bob later keep matching-basis positions.

## Protocol audit

| Item | Finding |
| --- | --- |
| Alice's bits and bases | `numpy.random.default_rng(seed)` produces independent uniform bit and basis arrays. A fixed seed reproduces them. This is a classical PRNG, not a cryptographic or quantum random-number source. |
| Bob's bases | Bob's basis array is generated in a separate uniform draw from the same seeded generator. It is statistically independent of Alice's draw. |
| Z encoding | Optional `X` prepares `|0⟩` or `|1⟩`. |
| X encoding | `X` followed by `H` prepares `|+⟩` or `|−⟩`. Bob measures X by applying `H` before the computational-basis measurement. |
| Quantum measurement | Alice preparation and Bob/Eve measurement are Qiskit circuits executed by Qiskit Aer. Measurement outcomes are read from Aer result memory; they are not synthesized with NumPy. |
| Eve attack | Eve selects independent random bases, measures Alice's states in an Aer run, and the returned Eve bits and bases control fresh resend circuits in a second Aer run. Bob measures those resent states. |
| Sifting | Matching Alice/Bob bases define the sifted positions. The retained bit arrays use those exact positions. |
| Test disclosure | A random subset is selected without replacement from sifted positions. Those positions are excluded from `secret_indices` and the displayed remaining candidates. |
| QBER | `test_qber` counts disagreements only on the disclosed test sample. `sifted_qber` is the simulator-known full sifted error rate and is labeled as a diagnostic; a real protocol cannot inspect unrevealed bits. |
| Reproducibility | Fixed seeds reproduce the classical choices, Aer measurements, Eve results, and disclosure sample. The automated test checks these arrays across repeated executions. |
| Empty data | Empty test samples return `None`; the dashboard reports insufficient material. The QBER comparison is now withheld if either comparison run has no sifted bits. |

The gate sequence and attack model are scientifically correct for ideal BB84 with individual intercept-and-resend. The matrix product state simulator batches independent qubits within Aer's backend width; no cross-signal gates or entanglement are introduced.

## Statistical experiments

I ran five paired experiments, each with 20,000 transmitted signals, a 20% disclosed test sample, and seeds `7`, `84`, `991`, `2201`, and `2026`. No-Eve and Eve-enabled runs were each executed for every seed. The table reports the measured full sifted QBER and the separate disclosed-sample QBER.

| Seed | Sifted positions | No-Eve sifted QBER | No-Eve test QBER | Eve sifted QBER | Eve test QBER |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 7 | 10,020 | 0.000% | 0.000% | 25.489% | 25.200% |
| 84 | 9,879 | 0.000% | 0.000% | 25.580% | 26.113% |
| 991 | 10,039 | 0.000% | 0.000% | 25.072% | 26.295% |
| 2201 | 10,189 | 0.000% | 0.000% | 25.341% | 24.926% |
| 2026 | 9,966 | 0.000% | 0.000% | 24.764% | 25.489% |
| **Pooled** | **50,093** | **0.000%** | **0.000%** | **25.249%** | — |

The pooled Eve result is 12,648 errors in 50,093 sifted bits. Against the theoretical 25%, this is a difference of **+0.249 percentage points**. The binomial standard error at 25% is **0.193 percentage points**, making the observed difference **1.29 standard errors**. The per-seed sample standard deviation of sifted QBER is 0.332 percentage points. These values show ordinary finite-sample variation; there is no unexpected deviation.

For an additional 20,000-signal no-Eve draw (seed `303`), Alice's bit counts were 10,003 zeros and 9,997 ones; Alice's bases were 10,044 Z and 9,956 X; Bob's bases were 10,031 Z and 9,969 X. Bases matched on 49.895% of signals. The 2×2 Alice/Bob basis contingency test gave χ²=0.081, p=0.776, consistent with independent uniform choices.

## Security wording and hardcoding review

- The app says that a low QBER does not prove security, distinguishes “No Eve configured” from proof of security, and shows an alert only when the selected sample threshold is exceeded.
- The README, app, notebook, and presentation describe this as an educational ideal simulator and explicitly say the remaining bits are only candidates, not a final key.
- Authentication, error correction, privacy amplification, finite-key analysis, device imperfections, channel loss, and general/coherent attacks are identified as omitted.
- Dashboard measurements and plots are computed from each `SimulationResult`. The 25% chart line is a theoretical reference, not a measured output. README example values and screenshots are documented from an actual seeded run.
- No production encryption or secure communication is claimed.

## Verification report

| Check | Result |
| --- | --- |
| Complete automated suite | **13 passed** (`pytest -q`; 10.36 s on the final source state before report creation). |
| Notebook execution | **4 code cells executed, no errors.** Windows emitted a non-fatal ZeroMQ Proactor event-loop warning and the usual local-kernel TCP encryption warning. |
| Notebook schema | Validated with `nbformat`. |
| Dependency installation | Existing isolated environment was installed from `requirements.txt`; `uv pip install --dry-run -r requirements.txt` resolved with no changes. `uv pip check` reported all installed packages compatible. |
| Runtime versions | Python 3.12.15, Qiskit 2.6.2, Qiskit Aer 0.18.4, NumPy 2.5.5, Streamlit 1.67.0, pytest 8.4.2. |
| Application startup | Streamlit started successfully; HTTP returned **200** on `http://127.0.0.1:8765`. The configured bind address was loopback. The process was stopped after verification. Qiskit's text circuit renderer emitted a non-fatal Windows CP1252 warning and fell back to UTF-8. |
| Browser demonstration | Both no-Eve and Eve runs were exercised. With 512 signals and seed 84, no-Eve test QBER was 0.0%; Eve test QBER was 30.6%, above the 11% alert threshold. Screenshots are in `assets/screenshots/`. |
| README setup/run guidance | The uv setup path, requirements resolution, and Streamlit command were checked. This machine did not have Python 3.12 registered with the Windows `py` launcher, so the documented uv alternative was used. |

## Changes made for this audit

- `README.md`: corrected the description from one circuit per signal to independent qubits batched into Qiskit circuits; corrected the BB84 paper DOI; recorded reproducible measured example values.
- `src/bb84_protocol.py`: avoided building an unused Bob-basis circuit in Eve mode. Eve behavior and random streams are unchanged.
- `app.py`: hides the comparison chart when a scenario has no sifted QBER, instead of allowing missing data to look like 0%.
- `FINAL_AUDIT.md`: added this audit and results record.

No tests or experiment results were hardcoded or altered to obtain passing outcomes.

## Remaining limitations

- This uses ideal local Aer simulation. It does not model physical qubits, optical channels, noise, losses, device side channels, or a real eavesdropper.
- Classical choices use NumPy's pseudorandom generator. They are reproducible for teaching, not suitable for generating production cryptographic material.
- Eve's supported attack is individual random-basis intercept-and-resend; this is not a complete security analysis against arbitrary attacks.
- The QBER threshold is a demonstration control, not a security proof or universal acceptance threshold. Finite samples can miss or misestimate disturbance.
- The dashboard intentionally displays per-position bits and remaining candidates for instruction. These are not private or certified secret keys.
- Error correction, privacy amplification, authentication, finite-key security bounds, and final key distillation are not implemented.
- The MPS batching relies on signals being independent. It is not an entangled multi-signal protocol simulator.

## Submission readiness

**Ready for educational hackathon judging and demonstration.** The core protocol and attack work, tests pass, notebook and dashboard run, measured statistics agree with theory, and documentation makes the security scope clear. **Not suitable for production encryption, production QKD, or real key generation.**

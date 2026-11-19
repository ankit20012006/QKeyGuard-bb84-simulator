# QKeyGuard · 3–5 minute demo

## Selected Project Topic

**Open Topic: Quantum Cryptography using Qiskit**

QKeyGuard is an interactive BB84 Quantum Key Distribution simulator built using Python, Qiskit, Qiskit Aer, and Streamlit.

The project demonstrates quantum key exchange, basis reconciliation, key sifting, QBER analysis, and Eve's intercept-and-resend attack through interactive simulations and visualizations.

## 1. The problem
How can Alice and Bob notice if someone measures the quantum signals they use to establish shared random key material?

## 2. Why quantum communication
Quantum states are disturbed by measurement in an incompatible basis. BB84 turns that behavior into an eavesdropping check.

## 3. BB84 in one minute
Alice encodes each random bit in either Z (`|0⟩`,`|1⟩`) or X (`|+⟩`,`|−⟩`). Bob guesses bases at random. They announce bases publicly and keep the matching positions. A random subset is revealed to estimate QBER and is removed from the key candidates.

## 4. Live run without Eve
Run with Eve disabled. Show the circuit's X/H encoding and Bob's basis measurement. In an ideal simulator, matching-basis bits agree, so sifted QBER is zero.

## 5. Live run with Eve
Switch on intercept and resend. Eve measures with random bases and prepares a replacement qubit from her result. Compare the visible error pattern and test sample. Full random-basis intercept/resend has an expected 25% sifted QBER; a finite sample can land above or below it.

## 6. Implementation
The engine uses one Qiskit circuit per signal and Qiskit Aer for quantum measurements. NumPy provides reproducible classical bit and basis choices. Alice-to-Eve and Eve-to-Bob are separate simulated stages so Eve's observed bit controls the resend.

## 7. Limits and next steps
The demo is idealized and does not create a final key. Production BB84 needs an authenticated classical channel, error correction, privacy amplification, finite-key analysis, and careful hardware/device security.

**Closing line:** QKeyGuard is a visual teaching tool for the core BB84 idea: an interceptor's wrong-basis measurements can leave statistical evidence.
